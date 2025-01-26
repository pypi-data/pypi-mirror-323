from datetime import datetime, timedelta

import pytest

from argos import schemas
from argos.server import queries
from argos.server.models import Result, Task, User


@pytest.mark.asyncio
async def test_remove_old_results(db, ten_tasks):  #  pylint: disable-msg=redefined-outer-name
    for _task in ten_tasks:
        for _ in range(5):
            result = Result(
                submitted_at=datetime.now(),
                status="success",
                context={"foo": "bar"},
                task=_task,
                agent_id="test",
                severity="ok",
            )
            db.add(result)
    db.commit()

    # So we have 5 results per tasks
    assert db.query(Result).count() == 50
    # Keep only 2
    deleted = await queries.remove_old_results(db, 2)
    assert deleted == 30
    assert db.query(Result).count() == 20
    for _task in ten_tasks:
        assert db.query(Result).filter(Result.task == _task).count() == 2


@pytest.mark.asyncio
async def test_remove_old_results_with_empty_db(db):
    assert db.query(Result).count() == 0
    deleted = await queries.remove_old_results(db, 2)
    assert deleted == 0


@pytest.mark.asyncio
async def test_release_old_locks(db, ten_locked_tasks, ten_tasks):  #  pylint: disable-msg=redefined-outer-name
    assert db.query(Task).count() == 20
    released = await queries.release_old_locks(db, 10)
    assert released == 10


@pytest.mark.asyncio
async def test_release_old_locks_with_empty_db(db):
    assert db.query(Task).count() == 0
    released = await queries.release_old_locks(db, 10)
    assert released == 0


@pytest.mark.asyncio
async def test_update_from_config_with_duplicate_tasks(db, empty_config):  #  pylint: disable-msg=redefined-outer-name
    # We pass the same path twice
    fake_path = {"path": "/", "checks": [{"body-contains": "foo"}]}
    website = schemas.config.Website(
        domain="https://example.org",
        paths=[
            fake_path,
            fake_path,
        ],
    )
    empty_config.websites = [website]

    assert db.query(Task).count() == 0
    await queries.update_from_config(db, empty_config)

    # Only one path has been saved in the database
    assert db.query(Task).count() == 2

    # Calling again with the same data works, and will not result in more tasks being
    # created.
    await queries.update_from_config(db, empty_config)


@pytest.mark.asyncio
async def test_update_from_config_db_can_remove_duplicates_and_old_tasks(
    db,
    empty_config,
    task,  #  pylint: disable-msg=redefined-outer-name
):
    # Add a duplicate in the db
    same_task = Task(
        url=task.url,
        domain=task.domain,
        ip_version="6",
        check=task.check,
        expected=task.expected,
        frequency=task.frequency,
    )
    db.add(same_task)
    db.commit()
    assert db.query(Task).count() == 2

    website = schemas.config.Website(
        domain=task.domain,
        paths=[
            {
                "path": "https://another-example.com",
                "checks": [{task.check: task.expected}],
            },
            {"path": task.url, "checks": [{task.check: task.expected}]},
        ],
    )
    empty_config.websites = [website]

    await queries.update_from_config(db, empty_config)
    assert db.query(Task).count() == 4

    website = schemas.config.Website(
        domain=task.domain,
        paths=[
            {
                "path": "https://another-example.com",
                "checks": [{task.check: task.expected}],
            }
        ],
    )
    empty_config.websites = [website]

    await queries.update_from_config(db, empty_config)
    assert db.query(Task).count() == 2


@pytest.mark.asyncio
async def test_update_from_config_db_updates_existing_tasks(db, empty_config, task):  #  pylint: disable-msg=redefined-outer-name
    assert db.query(Task).count() == 1

    website = schemas.config.Website(
        domain=task.domain,
        paths=[{"path": task.url, "checks": [{task.check: task.expected}]}],
    )
    empty_config.websites = [website]

    await queries.update_from_config(db, empty_config)
    assert db.query(Task).count() == 2


@pytest.mark.asyncio
async def test_reschedule_all(
    db,
    ten_tasks,
    ten_warning_tasks,
    ten_critical_tasks,
    ten_ok_tasks,  #  pylint: disable-msg=redefined-outer-name
):
    assert db.query(Task).count() == 40
    assert db.query(Task).filter(Task.severity == "unknown").count() == 10
    assert db.query(Task).filter(Task.severity == "warning").count() == 10
    assert db.query(Task).filter(Task.severity == "critical").count() == 10
    assert db.query(Task).filter(Task.severity == "ok").count() == 10

    one_hour_ago = datetime.now() - timedelta(hours=1)
    assert db.query(Task).filter(Task.next_run <= one_hour_ago).count() == 0

    await queries.reschedule_all(db)
    assert db.query(Task).filter(Task.next_run <= one_hour_ago).count() == 30


@pytest.mark.asyncio
async def test_add_user(db):
    users = await queries.list_users(db)
    assert users.count() == 0

    _user = await queries.add_user(db, "john", "doe")
    assert _user.username == "john"
    assert _user.password == "doe"
    assert _user.disabled == False
    assert _user.created_at is not None
    assert _user.updated_at is None
    assert _user.last_login_at is None

    _user = await queries.get_user(db, "morgan")
    assert _user is None

    _user = await queries.get_user(db, "john")
    assert _user.username == "john"
    assert _user.password == "doe"
    assert _user.disabled == False
    assert _user.created_at is not None
    assert _user.updated_at is None
    assert _user.last_login_at is None

    users = await queries.list_users(db)
    assert users.count() == 1


@pytest.mark.asyncio
async def test_remove_user(db, user):  #  pylint: disable-msg=redefined-outer-name
    users = await queries.list_users(db)
    assert users.count() == 1

    assert user.username == "jane"
    assert user.password == "doe"
    assert user.disabled == False
    assert user.created_at is not None
    assert user.updated_at is None
    assert user.last_login_at is None

    db.delete(user)
    db.commit()

    users = await queries.list_users(db)
    assert users.count() == 0


@pytest.fixture
def task(db):
    _task = Task(
        url="https://www.example.com",
        domain="https://www.example.com",
        ip_version="6",
        check="body-contains",
        expected="foo",
        frequency=1,
    )
    db.add(_task)
    db.commit()
    return _task


@pytest.fixture
def empty_config():
    return schemas.config.Config(
        general=schemas.config.General(
            db=schemas.config.DbSettings(url="sqlite:////tmp/test-argos.db"),
            cookie_secret="foo-bar-baz",
            frequency="1m",
            alerts=schemas.config.Alert(
                ok=["", ""],
                warning=["", ""],
                critical=["", ""],
                unknown=["", ""],
            ),
        ),
        service=schemas.config.Service(
            secrets=[
                "1234",
            ]
        ),
        ssl=schemas.config.SSL(thresholds=[]),
        websites=[],
    )


@pytest.fixture
def ten_results(db, task):  #  pylint: disable-msg=redefined-outer-name
    results = []
    for _ in range(10):
        result = Result(
            submitted_at=datetime.now(),
            status="success",
            context={"foo": "bar"},
            task=task,
            agent_id="test",
            severity="ok",
        )
        db.add(result)
        results.append(result)
    db.commit()
    return results


@pytest.fixture
def ten_locked_tasks(db):
    a_minute_ago = datetime.now() - timedelta(minutes=1)
    tasks = []
    for _ in range(10):
        _task = Task(
            url="https://www.example.com",
            domain="example.com",
            ip_version="6",
            check="body-contains",
            expected="foo",
            frequency=1,
            selected_by="test",
            selected_at=a_minute_ago,
        )
        db.add(_task)
        tasks.append(_task)
    db.commit()
    return tasks


@pytest.fixture
def ten_tasks(db):
    now = datetime.now()
    tasks = []
    for _ in range(10):
        _task = Task(
            url="https://www.example.com",
            domain="example.com",
            ip_version="6",
            check="body-contains",
            expected="foo",
            frequency=1,
            selected_by="test",
            selected_at=now,
        )
        db.add(_task)
        tasks.append(_task)
    db.commit()
    return tasks


@pytest.fixture
def ten_warning_tasks(db):
    now = datetime.now()
    tasks = []
    for _ in range(10):
        _task = Task(
            url="https://www.example.com",
            domain="example.com",
            ip_version="6",
            check="body-contains",
            expected="foo",
            frequency=1,
            next_run=now,
            severity="warning",
        )
        db.add(_task)
        tasks.append(_task)
    db.commit()
    return tasks


@pytest.fixture
def ten_critical_tasks(db):
    now = datetime.now()
    tasks = []
    for _ in range(10):
        _task = Task(
            url="https://www.example.com",
            domain="example.com",
            ip_version="6",
            check="body-contains",
            expected="foo",
            frequency=1,
            next_run=now,
            severity="critical",
        )
        db.add(_task)
        tasks.append(_task)
    db.commit()
    return tasks


@pytest.fixture
def ten_ok_tasks(db):
    now = datetime.now()
    tasks = []
    for _ in range(10):
        _task = Task(
            url="https://www.example.com",
            domain="example.com",
            ip_version="6",
            check="body-contains",
            expected="foo",
            frequency=1,
            next_run=now,
            severity="ok",
        )
        db.add(_task)
        tasks.append(_task)
    db.commit()
    return tasks


@pytest.fixture
def user(db):
    _user = User(
        username="jane",
        password="doe",
        disabled=False,
    )
    db.add(_user)
    db.commit()
    return _user
