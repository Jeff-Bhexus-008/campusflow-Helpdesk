# tests/test_engineer_b.py

import unittest

from campusflow.search import (
    search_tickets,
    sort_search_results,
)

from campusflow.reports import (
    generate_report,
    get_work_queue,
)

from campusflow.understanding_check import (
    QUESTIONS,
    calculate_score,
    run_understanding_check,
)

from campusflow.notes_cli import (
    add_follow_up_note,
    view_ticket_notes,
)


class TestEngineerB(unittest.TestCase):

    def setUp(self):
        """Create sample tickets for each test."""

        self.tickets = [
            {
                "id": "T001",
                "title": "Wi-Fi not working",
                "category": "Network",
                "priority": "critical",
                "status": "open",
                "assigned_to": "Ada",
                "notes": [],
            },
            {
                "id": "T002",
                "title": "Wi-Fi password reset",
                "category": "Network",
                "priority": "medium",
                "status": "resolved",
                "assigned_to": "John",
                "notes": [],
            },
            {
                "id": "T010",
                "title": "Laptop screen damaged",
                "category": "Hardware",
                "priority": "high",
                "status": "in_progress",
                "assigned_to": "Grace",
                "notes": [],
            },
            {
                "id": "T003",
                "title": "Software installation",
                "category": "Software",
                "priority": "low",
                "status": "open",
                "assigned_to": "",
                "notes": [],
            },
        ]

    def test_title_search_ignores_case(self):
        results = search_tickets(
            self.tickets,
            title="WI-FI",
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T001", "T002"],
        )

    def test_combined_filters_use_and(self):
        results = search_tickets(
            self.tickets,
            title="wifi",
            category="Network",
            status="open",
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T001"],
        )

    def test_invalid_category_filter_is_rejected(self):
        with self.assertRaises(ValueError):
            search_tickets(
                self.tickets,
                category="Transport",
            )

    def test_search_does_not_modify_tickets(self):
        before = [
            ticket.copy()
            for ticket in self.tickets
        ]

        search_tickets(
            self.tickets,
            title="wifi",
            status="open",
        )

        self.assertEqual(self.tickets, before)

    def test_search_results_sort_by_priority_and_numeric_id(self):
        results = sort_search_results([
            self.tickets[3],  # T003, low
            self.tickets[1],  # T002, medium
            self.tickets[0],  # T001, critical
        ])

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T001", "T002", "T003"],
        )

    def test_open_work_queue_excludes_non_open_tickets(self):
        results = get_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T001", "T003"],
        )

    def test_empty_report_returns_zero_percentage(self):
        report = generate_report([])

        self.assertEqual(report["total_tickets"], 0)
        self.assertEqual(report["resolved_count"], 0)
        self.assertEqual(report["unresolved_count"], 0)

        self.assertEqual(
            report["resolution_percentage"],
            0.0,
        )

    def test_report_counts_match_current_statuses(self):
        report = generate_report(self.tickets)

        self.assertEqual(report["total_tickets"], 4)

        self.assertEqual(
            report["by_status"],
            {
                "open": 2,
                "in_progress": 1,
                "resolved": 1,
            },
        )

        self.assertEqual(report["resolved_count"], 1)
        self.assertEqual(report["unresolved_count"], 3)

        self.assertEqual(
            report["resolution_percentage"],
            25.0,
        )

    def test_report_counts_categories(self):
        report = generate_report(self.tickets)

        self.assertEqual(
            report["by_category"],
            {
                "Network": 2,
                "Hardware": 1,
                "Software": 1,
                "Other": 0,
            },
        )

    def test_all_correct_quiz_answers_score_six(self):
        answers = [
            question["answer"]
            for question in QUESTIONS
        ]

        self.assertEqual(
            calculate_score(QUESTIONS, answers),
            6,
        )

    def test_all_incorrect_quiz_answers_score_zero(self):
        answers = ["A"] * len(QUESTIONS)

        self.assertEqual(
            calculate_score(QUESTIONS, answers),
            0,
        )

    def test_quiz_retries_invalid_answer(self):
        submitted_inputs = iter([
            "X",
            "B",
            "C",
            "B",
            "C",
            "C",
            "B",
            "The first rule protects ticket integrity.",
            "An empty report must avoid division by zero.",
        ])

        displayed_output = []

        result = run_understanding_check(
            input_fn=lambda prompt: next(submitted_inputs),
            output_fn=displayed_output.append,
        )

        self.assertEqual(result["score"], 6)

        self.assertIn(
            "Invalid choice. Enter A, B, C, or D.",
            displayed_output,
        )

        self.assertEqual(len(result["explanations"]), 2)

    def test_add_note_cli_calls_engineer_a_function(self):
        inputs = iter([
            "T001",
            "Mentor A",
            "Wi-Fi router checked",
        ])

        calls = []

        def find_ticket(ticket_id):
            return next(
                (
                    ticket
                    for ticket in self.tickets
                    if ticket["id"] == ticket_id
                ),
                None,
            )

        def add_note(ticket_id, author, message):
            calls.append((ticket_id, author, message))
            return "N001"

        output = []

        result = add_follow_up_note(
            add_note,
            find_ticket,
            input_fn=lambda prompt: next(inputs),
            output_fn=output.append,
        )

        self.assertTrue(result)

        self.assertEqual(
            calls,
            [
                (
                    "T001",
                    "Mentor A",
                    "Wi-Fi router checked",
                )
            ],
        )

        self.assertIn(
            "Follow-up note added successfully.",
            output,
        )

    def test_view_notes_displays_notes_in_id_order(self):
        self.tickets[0]["notes"] = [
            {
                "note_id": "N002",
                "author": "Mentor B",
                "message": "Switch ports investigated",
            },
            {
                "note_id": "N001",
                "author": "Mentor A",
                "message": "Router reboot attempted",
            },
        ]

        output = []

        view_ticket_notes(
            lambda ticket_id: self.tickets[0]
            if ticket_id == "T001"
            else None,
            input_fn=lambda prompt: "T001",
            output_fn=output.append,
        )

        n001_position = output.index("Note ID: N001")
        n002_position = output.index("Note ID: N002")

        self.assertLess(
            n001_position,
            n002_position,
        )


if __name__ == "__main__":
    unittest.main()