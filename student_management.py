"""Student Management System.

A small, menu-driven CLI application with JSON file persistence.
Run with:

    python student_management.py
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable


DATA_FILE = Path(
    os.environ.get("STUDENT_DATA_FILE", Path(__file__).with_name("students.json"))
)


@dataclass
class Student:
    """The information stored for one student."""

    student_id: str
    name: str
    age: int
    email: str
    course: str


class StudentManager:
    """Coordinates student records and persistence."""

    def __init__(self, data_file: Path = DATA_FILE) -> None:
        self.data_file = Path(data_file)
        self.students: list[Student] = []
        self.load()

    def load(self) -> None:
        """Load records from JSON, using an empty list when no file exists."""
        if not self.data_file.exists():
            self.students = []
            return

        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                raw_records = json.load(file)
            self.students = [Student(**record) for record in raw_records]
        except (json.JSONDecodeError, TypeError, KeyError, OSError) as error:
            print(f"\nWarning: could not read {self.data_file.name}: {error}")
            print("Starting with an empty in-memory student list.\n")
            self.students = []

    def save(self) -> None:
        """Save records atomically so an interrupted write does not corrupt JSON."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_file.parent,
                prefix=f".{self.data_file.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                json.dump(
                    [asdict(student) for student in self.students],
                    file,
                    indent=2,
                )
                file.write("\n")
                temporary_path = Path(file.name)
            temporary_path.replace(self.data_file)
        except OSError as error:
            if temporary_path and temporary_path.exists():
                temporary_path.unlink()
            raise RuntimeError(f"Could not save student data: {error}") from error

    def add(self, student: Student) -> None:
        """Add a student if the ID is not already in use."""
        if self.find_by_id(student.student_id):
            raise ValueError("A student with that ID already exists.")
        self.students.append(student)
        self.save()

    def find_by_id(self, student_id: str) -> Student | None:
        """Return one student by exact, case-insensitive ID."""
        normalized_id = student_id.strip().casefold()
        return next(
            (
                student
                for student in self.students
                if student.student_id.casefold() == normalized_id
            ),
            None,
        )

    def search(self, query: str) -> list[Student]:
        """Find records whose ID, name, email, or course contains the query."""
        query = query.strip().casefold()
        return [
            student
            for student in self.students
            if query in " ".join(
                (
                    student.student_id,
                    student.name,
                    str(student.age),
                    student.email,
                    student.course,
                )
            ).casefold()
        ]

    def update(self, student_id: str, updated_student: Student) -> None:
        """Replace a student record while keeping the original ID."""
        existing = self.find_by_id(student_id)
        if existing is None:
            raise ValueError("Student not found.")

        if (
            updated_student.student_id.casefold() != existing.student_id.casefold()
            and self.find_by_id(updated_student.student_id)
        ):
            raise ValueError("A student with that ID already exists.")

        index = self.students.index(existing)
        self.students[index] = updated_student
        self.save()

    def delete(self, student_id: str) -> None:
        """Delete a student by ID."""
        existing = self.find_by_id(student_id)
        if existing is None:
            raise ValueError("Student not found.")
        self.students.remove(existing)
        self.save()


def print_header(title: str) -> None:
    """Print a consistent section heading."""
    print("\n" + "=" * 68)
    print(f"{title:^68}")
    print("=" * 68)


def display_students(students: Iterable[Student]) -> None:
    """Display records in a readable table."""
    students = list(students)
    if not students:
        print("\nNo student records found.")
        return

    headers = ("ID", "Name", "Age", "Email", "Course")
    rows = [
        (
            student.student_id,
            student.name,
            str(student.age),
            student.email,
            student.course,
        )
        for student in students
    ]
    widths = [
        min(18, max(len(headers[index]), *(len(row[index]) for row in rows)))
        for index in range(len(headers))
    ]

    def format_row(row: tuple[str, ...]) -> str:
        cells = [
            cell if len(cell) <= width else cell[: width - 1] + "…"
            for cell, width in zip(row, widths)
        ]
        return " | ".join(cell.ljust(width) for cell, width in zip(cells, widths))

    separator = "-+-".join("-" * width for width in widths)
    print()
    print(format_row(headers))
    print(separator)
    for row in rows:
        print(format_row(row))
    print(f"\n{len(rows)} record(s) shown.")


def prompt_non_empty(label: str, input_fn: Callable[[str], str] = input) -> str:
    """Prompt until the user enters a non-empty value."""
    while True:
        value = input_fn(f"{label}: ").strip()
        if value:
            return value
        print("This field cannot be empty.")


def prompt_text(
    label: str,
    default: str,
    input_fn: Callable[[str], str] = input,
) -> str:
    """Prompt for text while allowing Enter to keep an existing value."""
    value = input_fn(f"{label} [{default}]: ").strip()
    return default if not value else value


def prompt_age(
    label: str = "Age",
    default: int | None = None,
    input_fn: Callable[[str], str] = input,
) -> int:
    """Prompt for a sensible age, optionally accepting a default."""
    while True:
        suffix = f" [{default}]" if default is not None else ""
        value = input_fn(f"{label}{suffix}: ").strip()
        if not value and default is not None:
            return default
        try:
            age = int(value)
            if 5 <= age <= 120:
                return age
            print("Please enter an age between 5 and 120.")
        except ValueError:
            print("Please enter a whole number.")


def prompt_email(
    label: str = "Email",
    default: str | None = None,
    input_fn: Callable[[str], str] = input,
) -> str:
    """Prompt for a basic email format."""
    while True:
        suffix = f" [{default}]" if default else ""
        value = input_fn(f"{label}{suffix}: ").strip()
        if not value and default:
            return default
        if "@" in value and "." in value.rsplit("@", 1)[-1]:
            return value
        print("Please enter a valid email address, such as student@example.com.")


def collect_student(
    input_fn: Callable[[str], str] = input,
    student_id: str | None = None,
    existing: Student | None = None,
) -> Student:
    """Collect and validate student details from the user."""
    if existing:
        student_id = existing.student_id
        name = prompt_text("Name", existing.name, input_fn)
        age = prompt_age(default=existing.age, input_fn=input_fn)
        email = prompt_email(default=existing.email, input_fn=input_fn)
        course = prompt_text("Course", existing.course, input_fn)
    else:
        student_id = student_id or prompt_non_empty("Student ID", input_fn)
        name = prompt_non_empty("Name", input_fn)
        age = prompt_age(input_fn=input_fn)
        email = prompt_email(input_fn=input_fn)
        course = prompt_non_empty("Course", input_fn)

    return Student(student_id, name, age, email, course)


def handle_add(manager: StudentManager) -> None:
    print_header("Add Student")
    try:
        student = collect_student()
        manager.add(student)
        print(f"\nStudent {student.student_id} added successfully.")
    except (ValueError, RuntimeError) as error:
        print(f"\nError: {error}")


def handle_view(manager: StudentManager) -> None:
    print_header("All Students")
    display_students(manager.students)


def handle_search(manager: StudentManager) -> None:
    print_header("Search Students")
    query = prompt_non_empty("Search term")
    display_students(manager.search(query))


def handle_update(manager: StudentManager) -> None:
    print_header("Update Student")
    student_id = prompt_non_empty("Enter student ID to update")
    existing = manager.find_by_id(student_id)
    if existing is None:
        print("\nError: Student not found.")
        return

    print("Press Enter to keep the current value. Type [current value] for text fields.")
    try:
        updated = collect_student(existing=existing)
        manager.update(student_id, updated)
        print(f"\nStudent {existing.student_id} updated successfully.")
    except (ValueError, RuntimeError) as error:
        print(f"\nError: {error}")


def handle_delete(manager: StudentManager) -> None:
    print_header("Delete Student")
    student_id = prompt_non_empty("Enter student ID to delete")
    existing = manager.find_by_id(student_id)
    if existing is None:
        print("\nError: Student not found.")
        return

    print(f"\nStudent: {existing.name} ({existing.student_id})")
    confirmation = input("Are you sure you want to delete this record? (y/n): ")
    if confirmation.strip().casefold() != "y":
        print("Delete cancelled.")
        return

    try:
        manager.delete(student_id)
        print("Student deleted successfully.")
    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}")


def show_menu() -> None:
    print_header("Student Management System")
    print("1. Add student")
    print("2. View all students")
    print("3. Search students")
    print("4. Update student")
    print("5. Delete student")
    print("6. Exit")


def run() -> None:
    """Run the interactive application."""
    manager = StudentManager()
    print(f"Data file: {manager.data_file}")

    actions = {
        "1": lambda: handle_add(manager),
        "2": lambda: handle_view(manager),
        "3": lambda: handle_search(manager),
        "4": lambda: handle_update(manager),
        "5": lambda: handle_delete(manager),
    }

    while True:
        show_menu()
        choice = input("\nChoose an option (1-6): ").strip()

        if choice == "6":
            print("\nThank you for using Student Management System. Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("\nInvalid option. Please choose a number from 1 to 6.")
            continue

        try:
            action()
        except (EOFError, KeyboardInterrupt):
            print("\n\nInput interrupted. Goodbye!")
            break
        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    run()