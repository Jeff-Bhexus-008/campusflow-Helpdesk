import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    update_ticket_status,
    get_queue,
    generate_report,
)


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        self.tickets = []

        create_ticket("Wi-Fi down", "Network", "high", 12, self.tickets)
        create_ticket("Broken mouse", "Hardware", "low", 1, self.tickets)
        create_ticket("App error", "Software", "medium", 4, self.tickets)

    def test_assign_ticket(self):
        result = assign_ticket(self.tickets, "T001", "Jeff")

        self.assertTrue(result)
        self.assertEqual(self.tickets[0]["assigned_to"], "Jeff")

    def test_assignment_rejects_unknown_ticket(self):
        self.assertFalse(assign_ticket(self.tickets, "T999", "Jeff"))

    def test_assignment_rejects_blank_name(self):
        self.assertFalse(assign_ticket(self.tickets, "T001", " "))

    def test_update_status(self):
        self.assertTrue(assign_ticket(self.tickets, "T001", "Jeff"))

        result = update_ticket_status(
            self.tickets, "T001", "in_progress"
        )

        self.assertTrue(result)
        self.assertEqual(self.tickets[0]["status"], "in_progress")

    def test_status_accepts_spaces(self):
        self.assertTrue(assign_ticket(self.tickets, "T001", "Jeff"))

        result = update_ticket_status(
            self.tickets, "T001", "in progress"
        )

        self.assertTrue(result)
        self.assertEqual(self.tickets[0]["status"], "in_progress")

    def test_invalid_status_is_rejected(self):
        self.assertFalse(
            update_ticket_status(self.tickets, "T001", "waiting")
        )

    def test_queue_prioritizes_critical_tickets(self):
        queue = get_queue(self.tickets)

        self.assertEqual(queue[0]["priority"], "critical")
        self.assertEqual(queue[-1]["priority"], "low")

    def test_queue_does_not_change_original_list_order(self):
        original_ids = [ticket["id"] for ticket in self.tickets]

        get_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in self.tickets],
            original_ids,
        )

    def test_report_counts_tickets(self):
        report = generate_report(self.tickets)

        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_status"]["open"], 3)
        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["by_priority"]["medium"], 1)
        self.assertEqual(report["by_priority"]["low"], 1)


if __name__ == "__main__":
    unittest.main()