import asyncio
import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

os.environ["ARGOS_YAML_FILE"] = "tests/config.yaml"


@pytest.fixture
def db() -> Session:  # type: ignore[misc]
    from argos.server import models

    app = _create_app()
    models.Base.metadata.create_all(bind=app.state.engine)
    yield app.state.SessionLocal()
    models.Base.metadata.drop_all(bind=app.state.engine)


@pytest.fixture
def app() -> FastAPI:  # type: ignore[misc]
    from argos.server import models

    app = _create_app()
    models.Base.metadata.create_all(bind=app.state.engine)
    yield app
    models.Base.metadata.drop_all(bind=app.state.engine)


@pytest.fixture
def authorized_client(app):
    with TestClient(app) as client:
        token = app.state.config.service.secrets[0]
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client


def _create_app() -> FastAPI:
    from argos.server.main import (  # local import for testing purpose
        get_application,
        setup_database,
        connect_to_db,
    )

    app = get_application()

    setup_database(app)
    asyncio.run(connect_to_db(app))
    return app
