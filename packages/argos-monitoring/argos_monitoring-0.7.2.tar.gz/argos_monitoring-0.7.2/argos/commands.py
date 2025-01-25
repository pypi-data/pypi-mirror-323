import asyncio
import os
from functools import wraps
from pathlib import Path
from sys import exit as sysexit
from uuid import uuid4

import click
import uvicorn
from alembic import command
from alembic.config import Config

from argos import VERSION, logging
from argos.agent import ArgosAgent


async def get_db():
    from argos.server.main import connect_to_db, get_application, setup_database

    app = get_application()
    setup_database(app)
    return await connect_to_db(app)


def coroutine(f):
    """Decorator to enable async functions in click"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def validate_config_access(ctx, param, value):
    for file in list(
        dict.fromkeys([value, "argos-config.yaml", "/etc/argos/config.yaml"])
    ):
        path = Path(file)

        if path.is_file() and os.access(path, os.R_OK):
            return file

    if value == "argos-config.yaml":
        raise click.BadParameter(
            f"the file {value} does not exists or is not reachable, "
            "nor does /etc/argos/config.yaml."
        )

    raise click.BadParameter(
        f"the file {value} does not exists or is not reachable, "
        "nor does argos-config.yaml or /etc/argos/config.yaml."
    )


@click.group()
def cli():
    pass


@cli.group()
def server():
    """Commands for managing server, server’s configuration and users"""


@server.group()
def user():
    """User management"""


@cli.command()
def version():
    """Prints Argos’ version and exits"""
    click.echo(VERSION)


@cli.command()
@click.argument("server_url", envvar="ARGOS_AGENT_SERVER_URL")
@click.argument("auth", envvar="ARGOS_AGENT_TOKEN")
@click.option(
    "--max-tasks",
    default=10,
    help="Number of concurrent tasks this agent can run",
)
@click.option(
    "--wait-time",
    default=10,
    help="Waiting time between two polls on the server (seconds)",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(logging.LOG_LEVELS, case_sensitive=False),
)
def agent(server_url, auth, max_tasks, wait_time, log_level):
    """Get and run tasks for the provided server. Will wait for new tasks.

    Usage: argos agent https://argos.example.org "auth-token-here"

    Alternatively, you can use the following environment variables to avoid passing
    arguments to the agent on the command line:

      \b
      ARGOS_AGENT_SERVER_URL=https://argos.example.org
      ARGOS_AGENT_TOKEN=auth-token-here
    """
    click.echo("Starting argos agent. Will retry forever.")
    from argos.logging import logger

    logger.setLevel(log_level)
    agent_ = ArgosAgent(server_url, auth, max_tasks, wait_time)
    asyncio.run(agent_.run())


@server.command()
@click.option("--host", default="127.0.0.1", help="Host to bind")
@click.option("--port", default=8000, type=int, help="Port to bind")
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead. "
    "Default value: argos-config.yaml and /etc/argos/config.yaml as fallback.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option("--reload", is_flag=True, help="Enable hot reloading")
def start(host, port, config, reload):
    """Starts the server (use only for testing or development!)

    See https://argos-monitoring.framasoft.org/deployment/systemd.html#server
    for advices on how to start the server for production.
    """
    os.environ["ARGOS_YAML_FILE"] = config
    uvicorn.run("argos.server:app", host=host, port=port, reload=reload)


def validate_max_lock_seconds(ctx, param, value):
    if value <= 60:
        raise click.BadParameter("Should be strictly higher than 60")
    return value


def validate_max_results(ctx, param, value):
    if value <= 0:
        raise click.BadParameter("Should be a positive integer")
    return value


@server.command()
@click.option(
    "--max-results",
    default=100,
    help="Number of results per task to keep",
    callback=validate_max_results,
)
@click.option(
    "--max-lock-seconds",
    default=100,
    help=(
        "The number of seconds after which a lock is "
        "considered stale, must be higher than 60 "
        "(the checks have a timeout value of 60 seconds)"
    ),
    callback=validate_max_lock_seconds,
)
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead. "
    "Default value: argos-config.yaml and /etc/argos/config.yaml as fallback.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@coroutine
async def cleandb(max_results, max_lock_seconds, config):
    """Clean the database (to run routinely)

    \b
    - Removes old results from the database.
    - Removes locks from tasks that have been locked for too long.
    """
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server import queries

    db = await get_db()
    removed = await queries.remove_old_results(db, max_results)
    updated = await queries.release_old_locks(db, max_lock_seconds)

    click.echo(f"{removed} results removed")
    click.echo(f"{updated} locks released")


@server.command()
@click.option(
    "--time-without-agent",
    default=5,
    help="Time without seeing an agent after which a warning will be issued, in minutes. "
    "Default is 5 minutes.",
    callback=validate_max_results,
)
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@coroutine
async def watch_agents(time_without_agent, config):
    """Watch agents (to run routinely)

    Issues a warning if no agent has been seen by the server for a given time.
    """
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server import queries

    db = await get_db()
    agents = await queries.get_recent_agents_count(db, time_without_agent)
    if agents == 0:
        click.echo(f"No agent has been seen in the last {time_without_agent} minutes.")
        sysexit(1)


@server.command(short_help="Load or reload tasks’ configuration")
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead. "
    "Default value: argos-config.yaml and /etc/argos/config.yaml as fallback.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@coroutine
async def reload_config(config):
    """Read tasks’ configuration and add/delete tasks in database if needed"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server import queries
    from argos.server.main import read_config

    _config = read_config(config)

    db = await get_db()
    changed = await queries.update_from_config(db, _config)

    click.echo(f"{changed['added']} tasks added")
    click.echo(f"{changed['vanished']} tasks deleted")


@server.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead. "
    "Default value: argos-config.yaml and /etc/argos/config.yaml as fallback.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@coroutine
async def migrate(config):
    """Run database migrations"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server.settings import read_yaml_config

    settings = read_yaml_config(config)

    current_dir = Path(__file__).resolve().parent
    alembic_cfg = Config(current_dir / "server" / "migrations" / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.general.db.url))
    command.upgrade(alembic_cfg, "head")


@user.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option("--name", prompt=True, help="Name of the user to create.")
@click.password_option()
@coroutine
async def add(config, name, password):
    """Add new user"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from passlib.context import CryptContext

    from argos.server import queries

    db = await get_db()
    _user = await queries.get_user(db, name)
    if _user is not None:
        click.echo(f"User {name} already exists.")
        sysexit(1)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    await queries.add_user(db, name, pwd_context.hash(password))
    click.echo(f"User {name} added.")


@user.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option(
    "--name", prompt=True, help="Name of the user you want to change the password."
)
@click.password_option()
@coroutine
async def change_password(config, name, password):
    """Change user’s password"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from passlib.context import CryptContext

    from argos.server import queries

    db = await get_db()
    _user = await queries.get_user(db, name)
    if _user is None:
        click.echo(f"User {name} does not exist.")
        sysexit(1)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    _user.password = pwd_context.hash(password)
    db.commit()
    click.echo(f"Password of user {name} changed.")


@user.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option(
    "--name", required=True, help="Name of the user you want to test the password for."
)
@click.option("--password", prompt=True, hide_input=True)
@coroutine
async def verify_password(config, name, password):
    """Test user’s password"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from passlib.context import CryptContext

    from argos.server import queries

    db = await get_db()
    _user = await queries.get_user(db, name)
    if _user is None:
        click.echo(f"User {name} does not exist.")
        sysexit(1)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if not pwd_context.verify(password, _user.password):
        click.echo("Wrong password!")
        sysexit(2)

    click.echo("The provided password is correct.")


@user.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option("--name", required=True, help="Name of the user to disable.")
@coroutine
async def disable(config, name):
    """Disable user"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server import queries

    db = await get_db()
    _user = await queries.get_user(db, name)
    if _user is None:
        click.echo(f"User {name} does not exist.")
        sysexit(1)
    if _user.disabled:
        click.echo(f"User {name} is already disabled.")
        sysexit(2)

    _user.disabled = True
    db.commit()

    click.echo(f"User {name} disabled.")


@user.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option("--name", required=True, help="Name of the user to reenable")
@coroutine
async def enable(config, name):
    """Enable user"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server import queries

    db = await get_db()
    _user = await queries.get_user(db, name)
    if _user is None:
        click.echo(f"User {name} does not exist.")
        sysexit(1)
    if not _user.disabled:
        click.echo(f"User {name} is already enabled.")
        sysexit(2)

    _user.disabled = False
    db.commit()

    click.echo(f"User {name} enabled.")


@user.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option("--name", required=True, help="Name of the user to delete.")
@coroutine
async def delete(config, name):
    """Delete user"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server import queries

    db = await get_db()
    _user = await queries.get_user(db, name)
    if _user is None:
        click.echo(f"User {name} does not exist.")
        sysexit(1)

    db.delete(_user)
    db.commit()

    click.echo(f"User {name} deleted.")


@user.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@coroutine
async def show(config):
    """List all users"""
    # It’s mandatory to do it before the imports
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server import queries

    db = await get_db()
    users = await queries.list_users(db)
    if users.count() == 0:
        click.echo("There is no users in database.")
        sysexit(1)

    click.echo("✅ means that the user is enabled.")
    click.echo("❌ means that the user is disabled.")

    for _user in users.all():
        status = "✅"
        if _user.disabled:
            status = "❌"
        click.echo(f"{status} {_user.username}, last login: {_user.last_login_at}")


@server.command(short_help="Generate a token for agents")
@coroutine
async def generate_token():
    """Generate a token, which can be used as an agent’s authentication token.

    It’s actually an UUID
    """
    click.echo(uuid4())


@server.command()
@coroutine
async def generate_config():
    """Output a self-documented example config file.

    \b
    Redirect the output to a file to save it:
        argos server generate-config > /etc/argos/config.yaml
    """
    config_example = Path(__file__).resolve().parent / "config-example.yaml"
    with config_example.open("r", encoding="utf-8") as f:
        print(f.read())


@server.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option("--domain", help="Domain for the notification", default="example.org")
@click.option("--severity", help="Severity", default="CRITICAL")
@coroutine
async def test_mail(config, domain, severity):
    """Send a test email"""
    os.environ["ARGOS_YAML_FILE"] = config

    from datetime import datetime

    from argos.logging import set_log_level
    from argos.server.alerting import notify_by_mail
    from argos.server.main import read_config
    from argos.server.models import Result, Task

    conf = read_config(config)

    if not conf.general.mail:
        click.echo("Mail is not configured, cannot test", err=True)
        sysexit(1)
    else:
        now = datetime.now()
        task = Task(
            url=f"https://{domain}",
            domain=domain,
            check="body-contains",
            expected="foo",
            frequency=1,
            selected_by="test",
            selected_at=now,
        )

        result = Result(
            submitted_at=now,
            status="success",
            context={"foo": "bar"},
            task=task,
            agent_id="test",
            severity="ok",
        )

        class _FalseRequest:
            def url_for(*args, **kwargs):
                return "/url"

        set_log_level("debug")
        notify_by_mail(
            result,
            task,
            severity=severity,
            old_severity="OLD SEVERITY",
            config=conf.general.mail,
            request=_FalseRequest(),
        )


@server.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option("--domain", help="Domain for the notification", default="example.org")
@click.option("--severity", help="Severity", default="CRITICAL")
@coroutine
async def test_gotify(config, domain, severity):
    """Send a test gotify notification"""
    os.environ["ARGOS_YAML_FILE"] = config

    from datetime import datetime

    from argos.logging import set_log_level
    from argos.server.alerting import notify_with_gotify
    from argos.server.main import read_config
    from argos.server.models import Result, Task

    conf = read_config(config)

    if not conf.general.gotify:
        click.echo("Gotify notifications are not configured, cannot test", err=True)
        sysexit(1)
    else:
        now = datetime.now()
        task = Task(
            url=f"https://{domain}",
            domain=domain,
            check="body-contains",
            expected="foo",
            frequency=1,
            selected_by="test",
            selected_at=now,
        )

        result = Result(
            submitted_at=now,
            status="success",
            context={"foo": "bar"},
            task=task,
            agent_id="test",
            severity="ok",
        )

        class _FalseRequest:
            def url_for(*args, **kwargs):
                return "/url"

        set_log_level("debug")
        notify_with_gotify(
            result,
            task,
            severity=severity,
            old_severity="OLD SEVERITY",
            config=conf.general.gotify,
            request=_FalseRequest(),
        )


@server.command()
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@click.option("--domain", help="Domain for the notification", default="example.org")
@click.option("--severity", help="Severity", default="CRITICAL")
@click.option(
    "--apprise-group", help="Apprise group for the notification", required=True
)
@coroutine
async def test_apprise(config, domain, severity, apprise_group):
    """Send a test apprise notification"""
    os.environ["ARGOS_YAML_FILE"] = config

    from datetime import datetime

    from argos.logging import set_log_level
    from argos.server.alerting import notify_with_apprise
    from argos.server.main import read_config
    from argos.server.models import Result, Task

    conf = read_config(config)

    if not conf.general.apprise:
        click.echo("Apprise notifications are not configured, cannot test", err=True)
        sysexit(1)
    else:
        now = datetime.now()
        task = Task(
            url=f"https://{domain}",
            domain=domain,
            check="body-contains",
            expected="foo",
            frequency=1,
            selected_by="test",
            selected_at=now,
        )

        result = Result(
            submitted_at=now,
            status="success",
            context={"foo": "bar"},
            task=task,
            agent_id="test",
            severity="ok",
        )

        class _FalseRequest:
            def url_for(*args, **kwargs):
                return "/url"

        set_log_level("debug")
        notify_with_apprise(
            result,
            task,
            severity=severity,
            old_severity="OLD SEVERITY",
            group=conf.general.apprise[apprise_group],
            request=_FalseRequest(),
        )


@server.command(short_help="Nagios compatible severities report")
@click.option(
    "--config",
    default="argos-config.yaml",
    help="Path of the configuration file. "
    "If ARGOS_YAML_FILE environment variable is set, its value will be used instead.",
    envvar="ARGOS_YAML_FILE",
    callback=validate_config_access,
)
@coroutine
async def nagios(config):
    """Output a report of current severities suitable for Nagios
    with a Nagios compatible exit code"""
    os.environ["ARGOS_YAML_FILE"] = config

    # The imports are made here otherwise the agent will need server configuration files.
    from argos.server import queries

    exit_nb = 0
    db = await get_db()
    severities = await queries.get_severity_counts(db)

    if severities["warning"] != 0:
        exit_nb = 1
    if severities["critical"] != 0:
        exit_nb = 2
    if severities["unknown"] != 0:
        exit_nb = 2

    stats = (
        f"ok={severities['ok']}; warning={severities['warning']}; "
        f"critical={severities['critical']}; unknown={severities['unknown']};"
    )

    if exit_nb == 0:
        print("OK — All sites are ok|{stats}")
    elif exit_nb == 1:
        print(f"WARNING — {severities['warning']} sites are in warning state|{stats}")
    elif severities["critical"] == 0:
        print(f"UNKNOWN — {severities['unknown']} sites are in unknown state|{stats}")
    elif severities["unknown"] == 0:
        print(
            f"CRITICAL — {severities['critical']} sites are in critical state|{stats}"
        )
    else:
        print(
            f"CRITICAL/UNKNOWN — {severities['critical']} sites are in critical state "
            f"and {severities['unknown']} sites are in unknown state|{stats}"
        )

    sysexit(exit_nb)


if __name__ == "__main__":
    cli()
