import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campusflow.storage import load_tickets, save_tickets


class TestStorage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "tickets.json"

        self.patcher = patch(
            "campusflow.storage.DATA_FILE",
            self.data_file,
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(), [])

    def test_save_and_load_tickets(self):
        tickets = [
            {
                "id": "T001",
                "title": "Wi-Fi down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            }
        ]

        save_tickets(tickets)

        self.assertEqual(load_tickets(), tickets)

    def test_invalid_json_is_rejected(self):
        self.data_file.write_text("{invalid", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets()

    def test_json_list_is_required(self):
        self.data_file.write_text(
            json.dumps({"id": "T001"}),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_tickets()

    def test_each_ticket_must_be_a_dictionary(self):
        self.data_file.write_text(
            json.dumps(["not a ticket"]),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_tickets()


if __name__ == "__main__":
    unittest.main()