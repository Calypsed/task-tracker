import sys
import os
import subprocess
import re
from constants import RepositoryType


def run_cli(*args, env):
    return subprocess.run(
        [
            sys.executable,
            "main_cli.py",
            *args,
        ],
        capture_output=True,
        text=True,
        env=env,
    )


def test_cli_add_and_list_e2e(tmp_path):
    filename = tmp_path / "tasks.json"

    env = os.environ.copy()
    env["REPOSITORY_TYPE"] = RepositoryType.JSON.value
    env["JSON_FILENAME"] = str(filename)

    add_result = run_cli("add", "Learn pytest", env=env)

    list_result = run_cli("list", env=env)

    assert add_result.returncode == 0
    assert "Task added successfully" in add_result.stdout

    assert list_result.returncode == 0
    assert "Learn pytest" in list_result.stdout


def test_cli_task_lifecycle_e2e(tmp_path):
    filename = tmp_path / "tasks.json"

    env = os.environ.copy()
    env["REPOSITORY_TYPE"] = RepositoryType.JSON.value
    env["JSON_FILENAME"] = str(filename)

    add_result = run_cli("add", "Learn pytest", env=env)

    assert add_result.returncode == 0
    assert "Task added successfully" in add_result.stdout

    match = re.search(r"ID=(\d+)", add_result.stdout)
    assert match is not None

    task_id = match.group(1)

    list_result = run_cli("list", env=env)

    update_result = run_cli("update", task_id, "Learn pytest deeply", env=env)

    progress_result = run_cli("mark-in-progress", task_id, env=env)

    done_result = run_cli("mark-done", task_id, env=env)

    list_done_result = run_cli("list", "done", env=env)

    delete_result = run_cli("delete", task_id, env=env)

    list_final_result = run_cli("list", env=env)

    assert "Learn pytest" in list_result.stdout

    assert update_result.returncode == 0
    assert "Task updated successfully" in update_result.stdout
    assert progress_result.returncode == 0
    assert "Task marked as in progress" in progress_result.stdout
    assert done_result.returncode == 0
    assert "Task marked as done" in done_result.stdout

    assert "Learn pytest deeply" in list_done_result.stdout

    assert delete_result.returncode == 0
    assert "Learn pytest deeply" not in list_final_result.stdout
    assert "No tasks found" in list_final_result.stdout
