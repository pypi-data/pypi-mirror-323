"""Functions to ease SQL queries management"""
from datetime import datetime, timedelta
from hashlib import sha256
from typing import List
from urllib.parse import urljoin

from sqlalchemy import asc, desc, func, Select
from sqlalchemy.orm import Session

from argos import schemas
from argos.logging import logger
from argos.server.models import Result, Task, ConfigCache, User


async def list_tasks(db: Session, agent_id: str, limit: int = 100):
    """List tasks and mark them as selected"""
    subquery = (
        db.query(func.distinct(Task.task_group))
        .filter(
            Task.selected_by == None,  # noqa: E711
            ((Task.next_run <= datetime.now()) | (Task.next_run == None)),  # noqa: E711
        )
        .limit(limit)
        .subquery()
    )
    tasks = db.query(Task).filter(Task.task_group.in_(Select(subquery))).all()

    now = datetime.now()
    for task in tasks:
        task.selected_at = now
        task.selected_by = agent_id
    db.commit()
    return tasks


async def add_user(db: Session, name: str, password: str) -> User:
    user = User(
        username=name,
        password=password,
        disabled=False,
    )
    db.add(user)
    db.commit()
    return user


async def get_user(db: Session, username: str) -> None | User:
    return db.get(User, username)


async def list_users(db: Session):
    return db.query(User).order_by(asc(User.username))


async def get_task(db: Session, task_id: int) -> None | Task:
    return db.get(Task, task_id)


async def create_result(db: Session, agent_result: schemas.AgentResult, agent_id: str):
    result = Result(
        submitted_at=datetime.now(),
        status=agent_result.status,
        context=agent_result.context,
        task_id=agent_result.task_id,
        agent_id=agent_id,
    )
    db.add(result)
    return result


async def count_tasks(db: Session, selected: None | bool = None):
    query = db.query(Task)
    if selected is not None:
        if selected:
            query = query.filter(Task.selected_by is not None)  # type: ignore[arg-type]
        else:
            query = query.filter(Task.selected_by is None)  # type: ignore[arg-type]

    return query.count()


async def count_results(db: Session):
    return db.query(Result).count()


async def has_config_changed(db: Session, config: schemas.Config) -> bool:  # pylint: disable-msg=too-many-statements
    """Check if websites config has changed by using a hashsum and a config cache"""
    websites_hash = sha256(str(config.websites).encode()).hexdigest()
    conf_caches = db.query(ConfigCache).all()
    same_config = True
    keys = [
        "websites_hash",
        "general_frequency",
        "general_recheck_delay",
        "general_retry_before_notification",
        "general_ipv4",
        "general_ipv6",
    ]
    if conf_caches:
        for conf in conf_caches:
            keys.remove(conf.name)
            match conf.name:
                case "websites_hash":
                    if conf.val != websites_hash:
                        same_config = False
                        conf.val = websites_hash
                        conf.updated_at = datetime.now()
                case "general_frequency":
                    if conf.val != str(config.general.frequency):
                        same_config = False
                        conf.val = str(config.general.frequency)
                        conf.updated_at = datetime.now()
                case "general_recheck_delay":
                    if conf.val != str(config.general.recheck_delay):
                        same_config = False
                        conf.val = str(config.general.recheck_delay)
                        conf.updated_at = datetime.now()
                case "general_retry_before_notification":
                    if conf.val != str(config.general.retry_before_notification):
                        same_config = False
                        conf.val = str(config.general.retry_before_notification)
                        conf.updated_at = datetime.now()
                case "general_ipv4":
                    if conf.val != str(config.general.ipv4):
                        same_config = False
                        conf.val = str(config.general.ipv4)
                        conf.updated_at = datetime.now()
                case "general_ipv6":
                    if conf.val != str(config.general.ipv6):
                        same_config = False
                        conf.val = str(config.general.ipv6)
                        conf.updated_at = datetime.now()

        for i in keys:
            match i:
                case "websites_hash":
                    c = ConfigCache(
                        name="websites_hash",
                        val=websites_hash,
                        updated_at=datetime.now(),
                    )
                case "general_frequency":
                    c = ConfigCache(
                        name="general_frequency",
                        val=str(config.general.frequency),
                        updated_at=datetime.now(),
                    )
                case "general_recheck_delay":
                    c = ConfigCache(
                        name="general_recheck_delay",
                        val=str(config.general.recheck_delay),
                        updated_at=datetime.now(),
                    )
                case "general_retry_before_notification":
                    c = ConfigCache(
                        name="general_retry_before_notification",
                        val=str(config.general.retry_before_notification),
                        updated_at=datetime.now(),
                    )
                case "general_ipv4":
                    c = ConfigCache(
                        name="general_ipv4",
                        val=str(config.general.ipv4),
                        updated_at=datetime.now(),
                    )
                case "general_ipv6":
                    c = ConfigCache(
                        name="general_ipv6",
                        val=str(config.general.ipv6),
                        updated_at=datetime.now(),
                    )
            db.add(c)

        db.commit()

        if keys:
            return True

        if same_config:
            return False

    else:  # no config cache found
        web_hash = ConfigCache(
            name="websites_hash", val=websites_hash, updated_at=datetime.now()
        )
        gen_freq = ConfigCache(
            name="general_frequency",
            val=str(config.general.frequency),
            updated_at=datetime.now(),
        )
        gen_recheck = ConfigCache(
            name="general_recheck_delay",
            val=str(config.general.recheck_delay),
            updated_at=datetime.now(),
        )
        gen_retry_before_notif = ConfigCache(
            name="general_retry_before_notification",
            val=str(config.general.retry_before_notification),
            updated_at=datetime.now(),
        )
        gen_ipv4 = ConfigCache(
            name="general_ipv4",
            val=str(config.general.ipv4),
            updated_at=datetime.now(),
        )
        gen_ipv6 = ConfigCache(
            name="general_ipv6",
            val=str(config.general.ipv6),
            updated_at=datetime.now(),
        )
        db.add(web_hash)
        db.add(gen_freq)
        db.add(gen_recheck)
        db.add(gen_retry_before_notif)
        db.add(gen_ipv4)
        db.add(gen_ipv6)
        db.commit()

    return True


async def update_from_config(db: Session, config: schemas.Config):  # pylint: disable-msg=too-many-branches
    """Update tasks from config file"""
    config_changed = await has_config_changed(db, config)
    if not config_changed:
        return {"added": 0, "vanished": 0}

    max_task_id = (
        db.query(func.max(Task.id).label("max_id")).all()  #  pylint: disable-msg=not-callable
    )[0].max_id
    tasks = []
    unique_properties = []
    seen_tasks: List[int] = []
    for website in config.websites:  # pylint: disable-msg=too-many-nested-blocks
        domain = str(website.domain)
        frequency = website.frequency or config.general.frequency
        recheck_delay = website.recheck_delay or config.general.recheck_delay
        retry_before_notification = (
            website.retry_before_notification
            if website.retry_before_notification is not None
            else config.general.retry_before_notification
        )
        ipv4 = website.ipv4 if website.ipv4 is not None else config.general.ipv4
        ipv6 = website.ipv6 if website.ipv6 is not None else config.general.ipv6
        if ipv4 is False and ipv6 is False:
            logger.warning("IPv4 AND IPv6 are disabled on website %s!", domain)
            continue

        for ip_version in ["4", "6"]:
            for p in website.paths:
                url = urljoin(domain, str(p.path))
                for check_key, expected in p.checks:
                    # Check the db for already existing tasks.
                    existing_tasks = (
                        db.query(Task)
                        .filter(
                            Task.url == url,
                            Task.method == p.method,
                            Task.request_data == p.request_data,
                            Task.check == check_key,
                            Task.expected == expected,
                            Task.ip_version == ip_version,
                        )
                        .all()
                    )

                    if (ip_version == "4" and ipv4 is False) or (
                        ip_version == "6" and ipv6 is False
                    ):
                        continue

                    if existing_tasks:
                        existing_task = existing_tasks[0]

                        seen_tasks.append(existing_task.id)

                        if frequency != existing_task.frequency:
                            existing_task.frequency = frequency
                        if recheck_delay != existing_task.recheck_delay:
                            existing_task.recheck_delay = recheck_delay  # type: ignore[assignment]
                        if (
                            retry_before_notification
                            != existing_task.retry_before_notification
                        ):
                            existing_task.retry_before_notification = (
                                retry_before_notification
                            )
                        logger.debug(
                            "Skipping db task creation for url=%s, "
                            "method=%s, check_key=%s, expected=%s, "
                            "frequency=%s, recheck_delay=%s, "
                            "retry_before_notification=%s, ip_version=%s.",
                            url,
                            p.method,
                            check_key,
                            expected,
                            frequency,
                            recheck_delay,
                            retry_before_notification,
                            ip_version,
                        )

                    else:
                        properties = (
                            url,
                            p.method,
                            check_key,
                            expected,
                            ip_version,
                            p.request_data,
                        )
                        if properties not in unique_properties:
                            unique_properties.append(properties)
                            task = Task(
                                domain=domain,
                                url=url,
                                ip_version=ip_version,
                                method=p.method,
                                request_data=p.request_data,
                                check=check_key,
                                expected=expected,
                                frequency=frequency,
                                recheck_delay=recheck_delay,
                                retry_before_notification=retry_before_notification,
                                already_retried=False,
                            )
                            logger.debug("Adding a new task in the db: %s", task)
                            tasks.append(task)

    db.add_all(tasks)
    db.commit()

    # Delete vanished tasks
    if max_task_id:
        vanished_tasks = (
            db.query(Task)
            .filter(Task.id <= max_task_id, Task.id.not_in(seen_tasks))
            .delete()
        )
        db.commit()
        logger.info(
            "%i tasks has been removed since not in config file anymore", vanished_tasks
        )
        return {"added": len(tasks), "vanished": vanished_tasks}

    return {"added": len(tasks), "vanished": 0}


async def get_severity_counts(db: Session) -> dict:
    """Get the severities (ok, warning, critical…) and their count"""
    query = db.query(Task.severity, func.count(Task.id).label("count")).group_by(  # pylint: disable-msg=not-callable
        Task.severity
    )

    # Execute the query and fetch the results
    task_counts_by_severity = query.all()

    counts_dict = dict(task_counts_by_severity)  # type: ignore[var-annotated,arg-type]
    for key in ("ok", "warning", "critical", "unknown"):
        counts_dict.setdefault(key, 0)
    return counts_dict


async def reschedule_all(db: Session):
    """Reschedule checks of all non OK tasks ASAP"""
    db.query(Task).filter(Task.severity.in_(["warning", "critical", "unknown"])).update(
        {Task.next_run: datetime.now() - timedelta(days=1)}
    )
    db.commit()


async def remove_old_results(db: Session, max_results: int):
    tasks = db.query(Task).all()
    deleted = 0
    for task in tasks:
        # Get the id of the oldest result to keep
        subquery = (
            db.query(Result.id)
            .filter(Result.task_id == task.id)
            .order_by(desc(Result.id))
            .limit(max_results)
            .subquery()
        )
        min_id = db.query(func.min(subquery.c.id)).scalar()  #  pylint: disable-msg=not-callable

        # Delete all the results older than min_id
        if min_id:
            deleted += (
                db.query(Result)
                .where(Result.id < min_id, Result.task_id == task.id)
                .delete()
            )
            db.commit()

    return deleted


async def release_old_locks(db: Session, max_lock_seconds: int):
    """Remove outdated locks on tasks"""
    max_acceptable_time = datetime.now() - timedelta(seconds=max_lock_seconds)

    # Release the locks on jobs that have been selected_at for more than max_lock_time
    updated = (
        db.query(Task)
        .filter(Task.selected_at < max_acceptable_time)
        .update({Task.selected_at: None, Task.selected_by: None})
    )
    db.commit()
    return updated


async def get_recent_agents_count(db: Session, minutes: int):
    """Get agents seen less than <minutes> ago"""
    max_time = datetime.now() - timedelta(minutes=minutes)

    agents = db.query(Result.agent_id).filter(Result.submitted_at > max_time).distinct()
    return agents.count()
