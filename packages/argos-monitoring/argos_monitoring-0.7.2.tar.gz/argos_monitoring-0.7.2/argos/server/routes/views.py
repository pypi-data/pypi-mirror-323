"""Web interface for humans"""
from collections import defaultdict
from datetime import datetime, timedelta
from functools import cmp_to_key
from pathlib import Path
from typing import Annotated
from urllib.parse import urlparse

from fastapi import APIRouter, Cookie, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session

from argos.checks.base import Status
from argos.schemas import Config
from argos.server import queries
from argos.server.exceptions import NotAuthenticatedException
from argos.server.models import Result, Task, User
from argos.server.routes.dependencies import get_config, get_db, get_manager

route = APIRouter()

current_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=current_dir / ".." / "templates")
SEVERITY_LEVELS = {"ok": 1, "warning": 2, "critical": 3, "unknown": 4}


@route.get("/login")
async def login_view(
    request: Request,
    msg: str | None = None,
    config: Config = Depends(get_config),
):
    if config.general.unauthenticated_access == "all":
        return RedirectResponse(
            request.url_for("get_severity_counts_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    token = request.cookies.get("access-token")
    if token is not None and token != "":
        manager = request.app.state.manager
        user = await manager.get_current_user(token)
        if user is not None:
            return RedirectResponse(
                request.url_for("get_severity_counts_view"),
                status_code=status.HTTP_303_SEE_OTHER,
            )

    if msg == "logout":
        msg = "You have been successfully disconnected."
    else:
        msg = None

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "msg": msg,
            "remember": config.general.remember_me_duration,
        },
    )


@route.post("/login")
async def post_login(
    request: Request,
    db: Session = Depends(get_db),
    data: OAuth2PasswordRequestForm = Depends(),
    rememberme: Annotated[str | None, Form()] = None,
    config: Config = Depends(get_config),
):
    if config.general.unauthenticated_access == "all":
        return RedirectResponse(
            request.url_for("get_severity_counts_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    username = data.username

    invalid_credentials = templates.TemplateResponse(
        "login.html",
        {"request": request, "msg": "Sorry, invalid username or bad password."},
    )

    if config.general.ldap is not None:
        from ldap import INVALID_CREDENTIALS  # pylint: disable-msg=no-name-in-module
        from argos.server.routes.dependencies import find_ldap_user

        ldap_dn = await find_ldap_user(config, request.app.state.ldap, username)
        if ldap_dn is None:
            return invalid_credentials
        try:
            request.app.state.ldap.simple_bind_s(ldap_dn, data.password)
        except INVALID_CREDENTIALS:
            return invalid_credentials
    else:
        user = await queries.get_user(db, username)
        if user is None:
            return invalid_credentials

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        if not pwd_context.verify(data.password, user.password):
            return invalid_credentials

        user.last_login_at = datetime.now()
        db.commit()

    manager = request.app.state.manager
    session_duration = config.general.session_duration
    if config.general.remember_me_duration is not None and rememberme == "on":
        session_duration = config.general.remember_me_duration
    delta = timedelta(minutes=session_duration)
    token = manager.create_access_token(data={"sub": username}, expires=delta)
    response = RedirectResponse(
        request.url_for("get_severity_counts_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        key=manager.cookie_name,
        value=token,
        httponly=True,
        samesite="strict",
        expires=int(delta.total_seconds()),
    )
    return response


@route.get("/logout")
async def logout_view(
    request: Request,
    config: Config = Depends(get_config),
    user: User | None = Depends(get_manager),
):
    if config.general.unauthenticated_access == "all":
        return RedirectResponse(
            request.url_for("get_severity_counts_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    response = RedirectResponse(
        request.url_for("login_view").include_query_params(msg="logout"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.delete_cookie(key="access-token")
    return response


@route.get("/")
async def get_severity_counts_view(
    request: Request,
    user: User | None = Depends(get_manager),
    db: Session = Depends(get_db),
    auto_refresh_enabled: Annotated[bool, Cookie()] = False,
    auto_refresh_seconds: Annotated[int, Cookie()] = 15,
):
    """Shows the number of results per severity"""
    counts_dict = await queries.get_severity_counts(db)

    agents = db.query(Result.agent_id).distinct().all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "counts_dict": counts_dict,
            "agents": agents,
            "auto_refresh_enabled": auto_refresh_enabled,
            "auto_refresh_seconds": auto_refresh_seconds,
            "user": user,
        },
    )


@route.get("/domains")
async def get_domains_view(
    request: Request,
    user: User | None = Depends(get_manager),
    config: Config = Depends(get_config),
    db: Session = Depends(get_db),
):
    """Show all tasks and their current state"""
    if config.general.unauthenticated_access == "dashboard":
        if user is None:
            raise NotAuthenticatedException

    tasks = db.query(Task).all()

    domains_severities = defaultdict(list)
    domains_last_checks = defaultdict(list)  # type: ignore[var-annotated]

    for task in tasks:
        domain = urlparse(task.url).netloc
        domains_severities[domain].append(task.severity)
        if task.last_severity_update is not None:
            domains_last_checks[domain] = task.last_severity_update
        else:
            domains_last_checks[domain] = "Waiting to be checked"

    def _max_severity(severities):
        return max(severities, key=SEVERITY_LEVELS.get)

    def _cmp_domains(a, b):
        if SEVERITY_LEVELS[a[1]] < SEVERITY_LEVELS[b[1]]:
            return 1
        if SEVERITY_LEVELS[a[1]] > SEVERITY_LEVELS[b[1]]:
            return -1
        if a[0] > b[0]:
            return 1
        if a[0] < b[0]:
            return -1
        return 0

    domains = [(key, _max_severity(value)) for key, value in domains_severities.items()]
    domains.sort(key=cmp_to_key(_cmp_domains))

    agents = db.query(Result.agent_id).distinct().all()

    return templates.TemplateResponse(
        "domains.html",
        {
            "request": request,
            "domains": domains,
            "last_checks": domains_last_checks,
            "total_task_count": len(tasks),
            "agents": agents,
            "user": user,
        },
    )


@route.get("/domain/{domain}")
async def get_domain_tasks_view(
    request: Request,
    domain: str,
    user: User | None = Depends(get_manager),
    config: Config = Depends(get_config),
    db: Session = Depends(get_db),
):
    """Show all tasks attached to a domain"""
    if config.general.unauthenticated_access == "dashboard":
        if user is None:
            raise NotAuthenticatedException

    tasks = db.query(Task).filter(Task.domain.contains(f"//{domain}")).all()
    return templates.TemplateResponse(
        "domain.html",
        {
            "request": request,
            "domain": domain,
            "tasks": tasks,
            "user": user,
        },
    )


@route.get("/result/{result_id}")
async def get_result_view(
    request: Request,
    result_id: int,
    user: User | None = Depends(get_manager),
    config: Config = Depends(get_config),
    db: Session = Depends(get_db),
):
    """Show the details of a result"""
    if config.general.unauthenticated_access == "dashboard":
        if user is None:
            raise NotAuthenticatedException

    result = db.query(Result).get(result_id)
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "result": result,
            "error": Status.ERROR,
            "user": user,
        },
    )


@route.get("/task/{task_id}/results")
async def get_task_results_view(
    request: Request,
    task_id: int,
    user: User | None = Depends(get_manager),
    db: Session = Depends(get_db),
    config: Config = Depends(get_config),
):
    """Show history of a task’s results"""
    if config.general.unauthenticated_access == "dashboard":
        if user is None:
            raise NotAuthenticatedException

    results = (
        db.query(Result)
        .filter(Result.task_id == task_id)
        .order_by(Result.submitted_at.desc())  # type: ignore[attr-defined]
        .all()
    )
    task = db.query(Task).get(task_id)
    description = ""
    if task is not None:
        description = task.get_check().get_description(config)
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "results": results,
            "task": task,
            "description": description,
            "error": Status.ERROR,
            "user": user,
        },
    )


@route.get("/agents")
async def get_agents_view(
    request: Request,
    user: User | None = Depends(get_manager),
    config: Config = Depends(get_config),
    db: Session = Depends(get_db),
):
    """Show argos agents and the last time the server saw them"""
    if config.general.unauthenticated_access == "dashboard":
        if user is None:
            raise NotAuthenticatedException

    last_seen = (
        db.query(Result.agent_id, func.max(Result.submitted_at).label("submitted_at"))
        .group_by(Result.agent_id)
        .all()
    )

    return templates.TemplateResponse(
        "agents.html",
        {
            "request": request,
            "last_seen": last_seen,
            "user": user,
        },
    )


@route.post("/refresh")
async def set_refresh_cookies_view(
    request: Request,
    user: User | None = Depends(get_manager),
    auto_refresh_enabled: Annotated[bool, Form()] = False,
    auto_refresh_seconds: Annotated[int, Form()] = 15,
):
    response = RedirectResponse(
        request.url_for("get_severity_counts_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    # Cookies’ age in Chrome can’t be more than 400 days
    # https://developer.chrome.com/blog/cookie-max-age-expires
    delta = int(timedelta(days=400).total_seconds())
    response.set_cookie(
        key="auto_refresh_enabled",
        value=str(auto_refresh_enabled),
        httponly=True,
        samesite="strict",
        expires=delta,
    )
    response.set_cookie(
        key="auto_refresh_seconds",
        value=str(max(5, int(auto_refresh_seconds))),
        httponly=True,
        samesite="strict",
        expires=delta,
    )
    return response
