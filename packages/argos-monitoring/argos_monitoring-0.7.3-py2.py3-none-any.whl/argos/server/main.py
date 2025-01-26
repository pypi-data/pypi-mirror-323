import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from argos.logging import logger
from argos.server import models, routes, queries
from argos.server.exceptions import NotAuthenticatedException, auth_exception_handler
from argos.server.settings import read_yaml_config


def get_application() -> FastAPI:
    """Spawn Argos FastAPI server"""
    config_file = os.environ["ARGOS_YAML_FILE"]
    config = read_config(config_file)

    root_path = config.general.root_path

    if root_path != "":
        logger.info("Root path for Argos: %s", root_path)
        if root_path.endswith("/"):
            root_path = root_path[:-1]
            logger.info("Fixed root path for Argos: %s", root_path)

    appli = FastAPI(lifespan=lifespan, root_path=root_path)

    # Config is the argos config object (built from yaml)
    appli.state.config = config
    appli.add_exception_handler(NotAuthenticatedException, auth_exception_handler)
    appli.state.manager = create_manager(config.general.cookie_secret)

    if config.general.ldap is not None:
        import ldap

        l = ldap.initialize(config.general.ldap.uri)
        l.simple_bind_s(config.general.ldap.bind_dn, config.general.ldap.bind_pwd)
        appli.state.ldap = l

    @appli.state.manager.user_loader()
    async def query_user(user: str) -> None | str | models.User:
        """
        Get a user from the db or LDAP
        :param user: name of the user
        :return: None or the user object
        """
        if appli.state.config.general.ldap is not None:
            from argos.server.routes.dependencies import find_ldap_user

            return await find_ldap_user(appli.state.config, appli.state.ldap, user)

        return await queries.get_user(appli.state.db, user)

    appli.include_router(routes.api, prefix="/api")
    appli.include_router(routes.views)

    static_dir = Path(__file__).resolve().parent / "static"

    appli.mount("/static", StaticFiles(directory=static_dir), name="static")
    return appli


async def connect_to_db(appli):
    appli.state.db = appli.state.SessionLocal()
    return appli.state.db


def read_config(yaml_file):
    try:
        config = read_yaml_config(yaml_file)
        return config
    except ValidationError as err:
        logger.error("Errors where found while reading configuration:")
        for error in err.errors():
            logger.error("%s is %s", error["loc"], error["type"])
        sys.exit(1)


def setup_database(appli):
    config = appli.state.config
    db_url = str(config.general.db.url)
    logger.debug("Using database URL %s", db_url)
    # For sqlite, we need to add connect_args={"check_same_thread": False}
    if config.general.env == "production" and db_url.startswith("sqlite:////tmp"):
        logger.warning("Using sqlite in /tmp is not recommended for production")

    extra_settings = {}
    if config.general.db.pool_size:
        extra_settings.setdefault("pool_size", config.general.db.pool_size)

    if config.general.db.max_overflow:
        extra_settings.setdefault("max_overflow", config.general.db.max_overflow)

    engine = create_engine(db_url, **extra_settings)

    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute("pragma foreign_keys=ON")

    if db_url.startswith("sqlite:///"):
        event.listen(engine, "connect", _fk_pragma_on_connect)

    appli.state.SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    appli.state.engine = engine
    models.Base.metadata.create_all(bind=engine)


def create_manager(cookie_secret: str) -> LoginManager:
    if cookie_secret == "foo_bar_baz":
        logger.warning(
            "You should change the cookie_secret secret in your configuration file."
        )
    return LoginManager(
        cookie_secret,
        "/login",
        use_cookie=True,
        use_header=False,
        not_authenticated_exception=NotAuthenticatedException,
    )


@asynccontextmanager
async def lifespan(appli):
    """Server start and stop actions

    Setup database connection then close it at shutdown.
    """
    setup_database(appli)

    db = await connect_to_db(appli)

    tasks_count = await queries.count_tasks(db)
    if tasks_count == 0:
        logger.warning(
            "There is no tasks in the database. "
            'Please launch the command "argos server reload-config"'
        )

    yield

    appli.state.db.close()


app = get_application()
