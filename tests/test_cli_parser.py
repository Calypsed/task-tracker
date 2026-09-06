import pytest
from task_tracker.main_cli import create_parser


def test_parser_parses_add_command():
    parser = create_parser()
    args = parser.parse_args(["add", "Task description"])

    assert args.command == "add"
    assert args.description == "Task description"


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
