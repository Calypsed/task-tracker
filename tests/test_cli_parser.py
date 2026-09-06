import subprocess


def run_cli(*args):
    return subprocess.run(
        ["task-tracker", *args],
        capture_output=True,
        text=True,
    )


def test_cli_displays_help():
    result = run_cli("--help")

    assert result.returncode == 0
    assert "Task Tracker CLI" in result.stdout


def test_cli_rejects_unknown_command():
    result = run_cli("banana")

    assert result.returncode == 2
    assert "invalid choice" in result.stderr


def test_cli_rejects_missing_command():
    result = run_cli()

    assert result.returncode == 2
    assert "required: command" in result.stderr


def test_cli_rejects_non_integer_task_id():
    result = run_cli("delete", "banana")

    assert result.returncode == 2
    assert "invalid int value" in result.stderr


def test_cli_rejects_missing_task_id():
    result = run_cli("delete")

    assert result.returncode == 2
    assert "following arguments are required: task_id" in result.stderr


def test_cli_rejects_missing_description_for_add():
    result = run_cli("add")

    assert result.returncode == 2
    assert "following arguments are required: description" in result.stderr


def test_cli_rejects_missing_description_for_update():
    result = run_cli("update", "1")

    assert result.returncode == 2
    assert "following arguments are required: description" in result.stderr


def test_cli_rejects_status_not_in_choices():
    result = run_cli("list", "banana")

    assert result.returncode == 2
    assert "invalid choice" in result.stderr
