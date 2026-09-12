# Student Management System

A simple Python command-line application for managing student records. It
supports all CRUD operations, stores data in a JSON file, and validates common
input errors.

## Features

- Add a student with a unique ID, name, age, email, and course
- View all saved students in a readable table
- Search by ID, name, age, email, or course
- Update existing records
- Delete records with a confirmation prompt
- Persist data in `students.json`
- Handle invalid menu choices, ages, email addresses, duplicate IDs, missing
  students, corrupt JSON, and interrupted input
- Atomic JSON writes to reduce the chance of losing data during a save

## Requirements

- Python 3.10 or newer
- No third-party packages

## Run the application

```bash
python student_management.py
```

The application creates `students.json` next to the Python file when the first
record is saved. To use another data file without changing the source:

```bash
STUDENT_DATA_FILE=/path/to/students.json python student_management.py
```

On Windows PowerShell:

```powershell
$env:STUDENT_DATA_FILE="C:\path\to\students.json"
python student_management.py
```

## Run the tests

```bash
python -m unittest -v
```

## Demo

The included [`demo_screenshot.png`](demo_screenshot.png) shows the menu and
student table. [`DEMO_TRANSCRIPT.md`](DEMO_TRANSCRIPT.md) records an end-to-end
run covering add, view, search, update, delete, validation, and exit.

## Menu

```text
1. Add student
2. View all students
3. Search students
4. Update student
5. Delete student
6. Exit
```

## Project structure

| File | Purpose |
| --- | --- |
| `student_management.py` | Main application and menu-driven interface |
| `test_student_management.py` | Automated tests for persistence and CRUD logic |
| `students.json` | Runtime data file, created automatically |

## Submission checklist

- [x] Python source code
- [x] Clear menu-driven interface
- [x] Create, read, update, and delete operations
- [x] JSON file handling
- [x] Input validation and error handling
- [x] Automated tests
- [ ] Push this folder to GitHub and add the repository URL
- [x] Include a screenshot and demonstration transcript