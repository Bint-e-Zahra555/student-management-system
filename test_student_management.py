import json
import tempfile
import unittest
from pathlib import Path

from student_management import Student, StudentManager


class StudentManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "students.json"
        self.manager = StudentManager(self.data_file)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_and_reload_persists_record(self) -> None:
        student = Student("S001", "Ayesha Khan", 20, "ayesha@example.com", "Python")
        self.manager.add(student)

        reloaded = StudentManager(self.data_file)
        self.assertEqual(reloaded.students, [student])

    def test_duplicate_ids_are_rejected_case_insensitively(self) -> None:
        self.manager.add(Student("S001", "Ayesha", 20, "a@example.com", "Python"))

        with self.assertRaises(ValueError):
            self.manager.add(Student("s001", "Bilal", 21, "b@example.com", "Java"))

    def test_search_matches_multiple_fields(self) -> None:
        self.manager.add(Student("S001", "Ayesha Khan", 20, "ayesha@example.com", "Python"))
        self.manager.add(Student("S002", "Bilal Ahmed", 21, "bilal@example.com", "Java"))

        self.assertEqual(len(self.manager.search("python")), 1)
        self.assertEqual(self.manager.search("s002")[0].name, "Bilal Ahmed")
        self.assertEqual(len(self.manager.search("example.com")), 2)

    def test_update_and_delete(self) -> None:
        original = Student("S001", "Ayesha", 20, "a@example.com", "Python")
        updated = Student("S001", "Ayesha Khan", 21, "ayesha@example.com", "Data Science")
        self.manager.add(original)
        self.manager.update("s001", updated)
        self.assertEqual(self.manager.find_by_id("S001"), updated)

        self.manager.delete("S001")
        self.assertIsNone(self.manager.find_by_id("S001"))

    def test_corrupt_json_starts_empty(self) -> None:
        self.data_file.write_text("{not valid json", encoding="utf-8")
        manager = StudentManager(self.data_file)
        self.assertEqual(manager.students, [])


if __name__ == "__main__":
    unittest.main()