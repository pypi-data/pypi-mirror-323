import os

from click.testing import CliRunner
from argos.commands import (
    add,
    verify_password,
    change_password,
    show,
    disable,
    enable,
    delete,
)


os.environ["ARGOS_APP_ENV"] = "test"
os.environ["ARGOS_YAML_FILE"] = "tests/config.yaml"


def test_add_user():
    runner = CliRunner()
    result = runner.invoke(add, ["--name", "foo"], input="bar\nbar\n")
    assert result.exit_code == 0
    assert result.output == "Password: \nRepeat for confirmation: \nUser foo added.\n"
    result = runner.invoke(add, ["--name", "foo"], input="bar\nbar\n")
    assert result.exit_code == 1
    assert (
        result.output
        == "Password: \nRepeat for confirmation: \nUser foo already exists.\n"
    )
    result = runner.invoke(add, ["--name", "baz", "--password", "qux"])
    assert result.exit_code == 0
    assert result.output == "User baz added.\n"


def test_user_password():
    runner = CliRunner()
    result = runner.invoke(verify_password, ["--name", "foo"], input="bar\n")
    assert result.exit_code == 0
    assert result.output == "Password: \nThe provided password is correct.\n"
    result = runner.invoke(verify_password, ["--name", "foo", "--password", "bar"])
    assert result.exit_code == 0
    assert result.output == "The provided password is correct.\n"
    result = runner.invoke(verify_password, ["--name", "quux", "--password", "corge"])
    assert result.exit_code == 1
    assert result.output == "User quux does not exist.\n"
    result = runner.invoke(verify_password, ["--name", "foo", "--password", "grault"])
    assert result.exit_code == 2
    assert result.output == "Wrong password!\n"


def test_change_password():
    runner = CliRunner()
    result = runner.invoke(verify_password, ["--name", "foo", "--password", "grault"])
    assert result.exit_code == 2
    assert result.output == "Wrong password!\n"
    result = runner.invoke(change_password, ["--name", "foo"], input="grault\ngrault\n")
    assert result.exit_code == 0
    assert (
        result.output
        == "Password: \nRepeat for confirmation: \nPassword of user foo changed.\n"
    )
    result = runner.invoke(verify_password, ["--name", "foo", "--password", "grault"])
    assert result.exit_code == 0
    assert result.output == "The provided password is correct.\n"
    result = runner.invoke(change_password, ["--name", "foo", "--password", "bar"])
    assert result.exit_code == 0
    assert result.output == "Password of user foo changed.\n"
    result = runner.invoke(verify_password, ["--name", "foo", "--password", "bar"])
    assert result.exit_code == 0
    assert result.output == "The provided password is correct.\n"
    result = runner.invoke(verify_password, ["--name", "quux", "--password", "bar"])
    assert result.exit_code == 1
    assert result.output == "User quux does not exist.\n"


def test_show():
    runner = CliRunner()
    result = runner.invoke(show)
    assert result.exit_code == 0
    assert (
        result.output
        == "✅ means that the user is enabled.\n❌ means that the user is disabled.\n"
        "✅ baz, last login: None\n✅ foo, last login: None\n"
    )


def test_disable():
    runner = CliRunner()
    result = runner.invoke(disable, ["--name", "quux"])
    assert result.exit_code == 1
    assert result.output == "User quux does not exist.\n"
    result = runner.invoke(disable, ["--name", "foo"])
    assert result.exit_code == 0
    assert result.output == "User foo disabled.\n"
    result = runner.invoke(disable, ["--name", "foo"])
    assert result.exit_code == 2
    assert result.output == "User foo is already disabled.\n"
    result = runner.invoke(show)
    assert result.exit_code == 0
    assert (
        result.output
        == "✅ means that the user is enabled.\n❌ means that the user is disabled.\n"
        "✅ baz, last login: None\n❌ foo, last login: None\n"
    )


def test_enable():
    runner = CliRunner()
    result = runner.invoke(enable, ["--name", "quux"])
    assert result.exit_code == 1
    assert result.output == "User quux does not exist.\n"
    result = runner.invoke(enable, ["--name", "foo"])
    assert result.exit_code == 0
    assert result.output == "User foo enabled.\n"
    result = runner.invoke(enable, ["--name", "foo"])
    assert result.exit_code == 2
    assert result.output == "User foo is already enabled.\n"
    result = runner.invoke(show)
    assert result.exit_code == 0
    assert (
        result.output
        == "✅ means that the user is enabled.\n❌ means that the user is disabled.\n"
        "✅ baz, last login: None\n✅ foo, last login: None\n"
    )


def test_delete():
    runner = CliRunner()
    result = runner.invoke(delete, ["--name", "quux"])
    assert result.exit_code == 1
    assert result.output == "User quux does not exist.\n"
    result = runner.invoke(delete, ["--name", "foo"])
    assert result.exit_code == 0
    assert result.output == "User foo deleted.\n"
    result = runner.invoke(delete, ["--name", "foo"])
    assert result.exit_code == 1
    assert result.output == "User foo does not exist.\n"
    result = runner.invoke(show)
    assert result.exit_code == 0
    assert (
        result.output
        == "✅ means that the user is enabled.\n❌ means that the user is disabled.\n"
        "✅ baz, last login: None\n"
    )
    result = runner.invoke(delete, ["--name", "baz"])
    assert result.exit_code == 0
    assert result.output == "User baz deleted.\n"
    result = runner.invoke(show)
    assert result.exit_code == 1
    assert result.output == "There is no users in database.\n"
