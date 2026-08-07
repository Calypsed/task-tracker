# 📋 Task Tracker CLI

A lightweight command-line task tracker written in **Python**.

This project was built as a solution for the **roadmap.sh Task Tracker** challenge. It allows you to manage tasks directly from the terminal using a simple CLI interface while storing all data in a JSON file.

> **Project URL:** https://roadmap.sh/projects/task-tracker

---

## ✨ Features

- ➕ Add new tasks
- 📋 List all tasks
- 🔍 Filter tasks by status (`todo`, `in-progress`, `done`)
- ✏️ Update task descriptions
- 🗑️ Delete tasks
- 🚀 Change task status
- 💾 Persistent JSON storage
- 📦 No external dependencies

---

## 🛠 Requirements

- Python **3.10** or higher
- No third-party libraries

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/Calypsed/task-tracker.git
```

Navigate to the project directory:

```bash
cd task-tracker
```

---

## 🚀 Usage

### Add a task

```bash
python tt.py add "Buy groceries"
```

### List all tasks

```bash
python tt.py list
```

### List tasks by status

```bash
python tt.py list todo
python tt.py list in-progress
python tt.py list done
```

### Update a task description

```bash
python tt.py update 1 "Buy groceries and cook dinner"
```

### Delete a task

```bash
python tt.py delete 1
```

### Mark a task as in progress

```bash
python tt.py mark-in-progress 1
```

### Mark a task as done

```bash
python tt.py mark-done 1
```

### Show help

```bash
python tt.py help
```

---

## 📸 Example

```console
$ python tt.py add "Complete project report"
Task added successfully (ID: 1)

$ python tt.py list
1) Complete project report | todo

$ python tt.py mark-done 1
Task status updated to 'done' successfully!

$ python tt.py list done
1) Complete project report | done
```

---

## 📂 Data Storage

All tasks are stored in **`tasks.json`**.

The file is automatically created the first time the application is launched.

### Task Properties

| Property | Description |
|----------|-------------|
| `task_id` | Unique task identifier |
| `description` | Task description |
| `status` | `todo`, `in-progress`, or `done` |
| `createdAt` | Creation timestamp |
| `updatedAt` | Last modification timestamp |

### Example JSON

```json
{
    "nextID": 1,
    "deletedIDs": [],
    "tasks": [
        {
            "task_id": 0,
            "description": "Buy groceries",
            "status": "done",
            "createdAt": "2026-08-07T14:30:45.123456",
            "updatedAt": "2026-08-07T14:35:20.987654"
        }
    ]
}
```

---

## 📁 Project Structure

```text
task-tracker/
├── tt.py              # Main application
├── README.md          # Project documentation
├── LICENSE            # MIT License
├── .gitignore
├── .black
├── .flake8
├── tasks.json         # Auto-generated
└── screenshots/
    └── demo.png
```

---

## 🛠 Code Quality

This project follows common Python formatting standards.

### Format code

```bash
black tt.py
```

### Run linting

```bash
flake8 tt.py
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/amazing-feature
```

3. Commit your changes.

```bash
git commit -m "Add amazing feature"
```

4. Push your branch.

```bash
git push origin feature/amazing-feature
```

5. Open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for more information.

---

## 🙏 Acknowledgments

- Built as part of the **roadmap.sh** project-based learning path.
- Inspired by the **Task Tracker** challenge:
  https://roadmap.sh/projects/task-tracker