"""Database models"""

from datetime import datetime, timedelta
from hashlib import md5
from typing import List, Literal

from sqlalchemy import (
    JSON,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import Index

from argos.checks import BaseCheck, get_registered_check
from argos.schemas import WebsiteCheck
from argos.schemas.utils import IPVersion, Method


def compute_task_group(context) -> str:
    data = context.current_parameters["request_data"]
    if data is None:
        data = ""
    return (
        f"{context.current_parameters['method']}-"
        f"{context.current_parameters['ip_version']}-"
        f"{context.current_parameters['url']}-"
        f"{md5(data.encode()).hexdigest()}"
    )


class Base(DeclarativeBase):
    type_annotation_map = {List[WebsiteCheck]: JSON, dict: JSON}


class Task(Base):
    """
    There is one task per check.

    It contains all information needed to run the jobs on the agents.
    Agents will return information in the result table.
    """

    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)

    # Info needed to run the task
    url: Mapped[str] = mapped_column()
    domain: Mapped[str] = mapped_column()
    ip_version: Mapped[IPVersion] = mapped_column(
        Enum("4", "6", name="ip_version_enum"),
    )
    check: Mapped[str] = mapped_column()
    expected: Mapped[str] = mapped_column()
    frequency: Mapped[float] = mapped_column()
    recheck_delay: Mapped[float] = mapped_column(nullable=True)
    already_retried: Mapped[bool] = mapped_column(insert_default=False)
    retry_before_notification: Mapped[int] = mapped_column(insert_default=0)
    contiguous_failures: Mapped[int] = mapped_column(insert_default=0)
    method: Mapped[Method] = mapped_column(
        Enum(
            "GET",
            "HEAD",
            "POST",
            "OPTIONS",
            "CONNECT",
            "TRACE",
            "PUT",
            "PATCH",
            "DELETE",
            name="method",
        ),
        insert_default="GET",
    )
    request_data: Mapped[str] = mapped_column(nullable=True)

    # Orchestration-related
    selected_by: Mapped[str] = mapped_column(nullable=True)
    selected_at: Mapped[datetime] = mapped_column(nullable=True)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    next_run: Mapped[datetime] = mapped_column(nullable=True)
    task_group: Mapped[str] = mapped_column(insert_default=compute_task_group)

    severity: Mapped[Literal["ok", "warning", "critical", "unknown"]] = mapped_column(
        Enum("ok", "warning", "critical", "unknown", name="severity"),
        insert_default="unknown",
    )
    last_severity_update: Mapped[datetime] = mapped_column(nullable=True)

    results: Mapped[List["Result"]] = relationship(
        back_populates="task",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __str__(self) -> str:
        return f"DB Task {self.url} (IPv{self.ip_version}) - {self.check} - {self.expected}"

    def get_check(self) -> BaseCheck:
        """Returns a check instance for this specific task"""
        return get_registered_check(self.check)

    def set_times_severity_and_deselect(self, severity, submitted_at):
        """Removes the lock on task, set its severity and set the time for the next run"""
        self.severity = severity
        self.last_severity_update = submitted_at
        self.selected_by = None
        self.selected_at = None

        now = datetime.now()
        self.completed_at = now
        if (
            self.recheck_delay is not None
            and severity != "ok"
            and not self.already_retried
        ):
            self.next_run = now + timedelta(minutes=self.recheck_delay)
            self.already_retried = True
        else:
            self.next_run = now + timedelta(minutes=self.frequency)
            self.already_retried = False

    @property
    def last_result(self):
        """Get last result of the task"""
        if not self.results:
            return None
        return max(self.results, key=lambda r: r.id)

    @property
    def status(self):
        """Get status of the task, i.e. the status of its last result"""
        if not self.last_result:
            return None
        return self.last_result.status


Index("similar_tasks", Task.task_group)


class Result(Base):
    """There are multiple results per task.

    The results store information returned by the agents.

    You can read `status` as  "Was the agent able to do the check?"
    while the `severity` depends on the return value of the check.
    """

    __tablename__ = "results"
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    task: Mapped["Task"] = relationship(back_populates="results")
    agent_id: Mapped[str] = mapped_column(nullable=True)

    submitted_at: Mapped[datetime] = mapped_column()
    # XXX change "on-check" to something better.
    status: Mapped[Literal["success", "failure", "error", "on-check"]] = mapped_column(
        Enum("success", "failure", "error", "on-check", name="status")
    )
    severity: Mapped[Literal["ok", "warning", "critical", "unknown"]] = mapped_column(
        Enum("ok", "warning", "critical", "unknown", name="severity")
    )
    context: Mapped[dict] = mapped_column()

    def set_status(self, status, severity):
        self.severity = severity
        self.status = status

    def __str__(self):
        return f"DB Result {self.id} - {self.status} - {self.context}"


class ConfigCache(Base):
    """Database model containing information on the current state
    of the configuration.

    This is used to determine if tasks are to be updated.

    These settings are cached:
    - general_frequency: the content of general.frequency setting, in minutes
                         ex: 5
    - websites_hash:     the hash (sha256sum) of websites setting, to allow a quick
                         comparison without looping through all websites.
                         ex: 8b886e7db7b553fe99f6d5437f31745987e243c77b2109b84cf9a7f8bf7d75b1
    """

    __tablename__ = "config_cache"
    name: Mapped[str] = mapped_column(primary_key=True)
    val: Mapped[str] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class User(Base):
    """Database model for user authentication"""

    __tablename__ = "users"
    username: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column()
    disabled: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True)
    last_login_at: Mapped[datetime] = mapped_column(nullable=True)

    def update_last_login_at(self):
        self.last_login_at = datetime.now()
