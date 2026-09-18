import pytest
from task_tracker.main_cli import create_parser
from datetime import datetime, timezone


@pytest.mark.parametrize(
    ("argv", "expected_due_at"),
    [
        (
            ["add", "Task description"],
            None,
        ),
        (
            [
                "add",
                "Task description",
                "--due",
                datetime(2030, 1, 2, 3, 45, 6, 789, tzinfo=timezone.utc).isoformat(),
            ],
            datetime(2030, 1, 2, 3, 45, 6, 789, tzinfo=timezone.utc).isoformat(),
        ),
    ],
)
def test_parser_parses_add_command(argv, expected_due_at: str | None):
    parser = create_parser()

    parsed_args = parser.parse_args(argv)

    assert parsed_args.command == "add"
    assert parsed_args.description == "Task description"
    assert parsed_args.due_at == expected_due_at


def test_parser_parses_delete_command():
    parser = create_parser()

    args = parser.parse_args(["delete", "42"])

    assert args.command == "delete"
    assert args.task_id == 42


def test_parser_parses_update_command():
    parser = create_parser()

    args = parser.parse_args(["update", "42", "Learn pytest deeply"])

    assert args.command == "update"
    assert args.task_id == 42
    assert args.description == "Learn pytest deeply"


@pytest.mark.parametrize(
    "status",
    [
        "todo",
        "in-progress",
        "done",
    ],
)
def test_parser_parses_list_with_status(status):
    parser = create_parser()

    args = parser.parse_args(["list", status])

    assert args.command == "list"
    assert args.status == status


def test_parser_parses_list_without_status():
    parser = create_parser()

    args = parser.parse_args(["list"])

    assert args.command == "list"
    assert args.status is None


@pytest.mark.parametrize(
    "mark_command",
    [
        "mark-done",
        "mark-in-progress",
    ],
)
def test_parser_parses_mark_commands(mark_command):
    parser = create_parser()

    args = parser.parse_args([mark_command, "42"])

    assert args.command == mark_command
    assert args.task_id == 42


def test_parser_displays_help(capsys):
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])
    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "Task Tracker CLI" in captured.out


def test_parser_rejects_unknown_command(capsys):
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["banana"])
    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "invalid choice" in captured.err


def test_parser_rejects_missing_command(capsys):
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])
    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "required: command" in captured.err


@pytest.mark.parametrize(
    "cli_args",
    [
        ["delete", "banana"],
        ["update", "banana", "description"],
        ["mark-done", "banana"],
        ["mark-in-progress", "banana"],
    ],
)
def test_parser_rejects_non_integer_task_id(capsys, cli_args):
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(cli_args)
    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "invalid int value" in captured.err


@pytest.mark.parametrize(
    "cli_args",
    [
        ["delete"],
        ["update"],
        ["mark-done"],
        ["mark-in-progress"],
    ],
)
def test_parser_rejects_missing_task_id(capsys, cli_args):
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(cli_args)
    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "task_id" in captured.err


def test_parser_rejects_missing_description_for_add(capsys):
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["add"])
    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "following arguments are required: description" in captured.err


def test_parser_rejects_missing_description_for_update(capsys):
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["update", "1"])
    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "following arguments are required: description" in captured.err


def test_parser_rejects_status_not_in_choices(capsys):
    parser = create_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["list", "banana"])
    captured = capsys.readouterr()

    assert exc_info.value.code == 2
    assert "invalid choice" in captured.err
