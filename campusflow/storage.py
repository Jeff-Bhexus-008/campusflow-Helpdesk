import json
from pathlib import Path
import re

from campusflow.tickets import (
    calculate_priority,
    validate_affected_users,
    validate_category,
    validate_title,
    validate_urgency,
)

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "tickets.json"
)

REQUIRED_FIELDS = {
    "id", "title", "category", "urgency", "affected_users",
    "priority", "status", "assigned_to",
}
VALID_STATUSES = {"open", "in_progress", "resolved"}


def validate_tickets(tickets):
    """Validate a complete ticket collection before loading or saving."""
    if not isinstance(tickets, list):
        raise ValueError("Ticket storage must contain a list.")

    seen_ids = set()

    for index, ticket in enumerate(tickets):
        label = f"Ticket at position {index}"

        if not isinstance(ticket, dict):
            raise ValueError(f"{label} must be a dictionary.")

        missing = REQUIRED_FIELDS - ticket.keys()
        if missing:
            raise ValueError(
                f"{label} is missing required fields: "
                + ", ".join(sorted(missing))
            )

        ticket_id = ticket["id"]
        if (
            not isinstance(ticket_id, str)
            or re.fullmatch(r"T[0-9]+", ticket_id) is None
            or int(ticket_id[1:]) < 1
        ):
            raise ValueError(f"{label} has an invalid ticket ID.")

        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID: {ticket_id}")
        seen_ids.add(ticket_id)

        try:
            validate_title(ticket["title"])
            category = validate_category(ticket["category"])
            urgency = validate_urgency(ticket["urgency"])
            users = validate_affected_users(ticket["affected_users"])
        except (ValueError, TypeError) as error:
            raise ValueError(f"{ticket_id}: {error}") from error

        if ticket["title"] != ticket["title"].strip():
            raise ValueError(f"{ticket_id}: title must be trimmed.")

        if ticket["category"] != category:
            raise ValueError(f"{ticket_id}: category is not normalized.")

        if ticket["urgency"] != urgency:
            raise ValueError(f"{ticket_id}: urgency is not normalized.")

        if (
            isinstance(ticket["affected_users"], bool)
            or not isinstance(ticket["affected_users"], int)
            or ticket["affected_users"] != users
        ):
            raise ValueError(
                f"{ticket_id}: affected_users must be a positive integer."
            )

        expected_priority = calculate_priority(urgency, users)
        if ticket["priority"] != expected_priority:
            raise ValueError(
                f"{ticket_id}: priority must be {expected_priority!r}."
            )

        if (
            not isinstance(ticket["status"], str)
            or ticket["status"] not in VALID_STATUSES
        ):
            raise ValueError(f"{ticket_id}: invalid status.")

        assigned_to = ticket["assigned_to"]
        if assigned_to is not None and (
            not isinstance(assigned_to, str) or not assigned_to.strip()
        ):
            raise ValueError(
                f"{ticket_id}: assigned_to must be null or nonblank text."
            )

        if ticket["status"] == "in_progress" and not assigned_to:
            raise ValueError(
                f"{ticket_id}: an in-progress ticket must be assigned."
            )

        # Legacy tickets may not have notes. Treat them as having no notes.
        if "notes" in ticket:
            notes = ticket["notes"]
            if not isinstance(notes, list):
                raise ValueError(f"{ticket_id}: notes must be a list.")

            seen_note_ids = set()
            for note in notes:
                if not isinstance(note, dict):
                    raise ValueError(f"{ticket_id}: each note must be an object.")

                note_id = note.get("note_id")
                if (
                    not isinstance(note_id, str)
                    or re.fullmatch(r"N[0-9]+", note_id) is None
                    or int(note_id[1:]) < 1
                ):
                    raise ValueError(f"{ticket_id}: invalid note ID.")

                if note_id in seen_note_ids:
                    raise ValueError(
                        f"{ticket_id}: duplicate note ID {note_id}."
                    )
                seen_note_ids.add(note_id)

                for field in ("author", "message"):
                    value = note.get(field)
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError(
                            f"{ticket_id}: note {field} cannot be blank."
                        )


def load_tickets():
    """Load and validate saved ticket data."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError("Ticket storage contains invalid JSON.") from error

    validate_tickets(tickets)
    return tickets


def save_tickets(tickets):
    """Validate first, then atomically replace the saved JSON file."""
    validate_tickets(tickets)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = DATA_FILE.with_suffix(".tmp")

    try:
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=4, ensure_ascii=False)
            file.write("\n")
        temporary_file.replace(DATA_FILE)
    finally:
        if temporary_file.exists():
            temporary_file.unlink()
