import sys
import subprocess


def test_cli_displays_help():
    result = subprocess.run(
        [
            sys.executable,
            "main_cli.py",
            "--help",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Task Tracker CLI" in result.stdout


def test_cli_rejects_unknown_command():
    result = subprocess.run(
        [sys.executable, "main_cli.py", "banana"], capture_output=True, text=True
    )

    assert result.returncode == 2
    assert "invalid choice" in result.stderr


def test_cli_rejects_missing_command():
    result = subprocess.run(
        [sys.executable, "main_cli.py"], capture_output=True, text=True
    )

    assert result.returncode == 2
    assert "required: command" in result.stderr


def test_cli_rejects_non_integer_task_id():
    result = subprocess.run(
        [sys.executable, "main_cli.py", "delete", "banana"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "invalid int value" in result.stderr


def test_cli_rejects_missing_task_id():
    result = subprocess.run(
        [
            sys.executable,
            "main_cli.py",
            "delete",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "following arguments are required: task_id" in result.stderr


def test_cli_rejects_missing_description_for_add():
    result = subprocess.run(
        [
            sys.executable,
            "main_cli.py",
            "add",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "following arguments are required: description" in result.stderr


def test_cli_rejects_missing_description_for_update():
    result = subprocess.run(
        [
            sys.executable,
            "main_cli.py",
            "update",
            "1",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "following arguments are required: description" in result.stderr


def test_cli_rejects_status_not_in_choices():
    result = subprocess.run(
        [sys.executable, "main_cli.py", "list", "banana"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "invalid choice" in result.stderr
