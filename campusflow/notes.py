from campusflow.workflow import find_ticket


def add_note(tickets, ticket_id, author, message):
    """Add a note to an open or in-progress ticket."""
    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValueError("Ticket not found.")

    if ticket.get("status") == "resolved":
        raise ValueError("Reopen the ticket before adding a note.")

    if not isinstance(author, str) or not author.strip():
        raise ValueError("Author cannot be blank.")

    if not isinstance(message, str) or not message.strip():
        raise ValueError("Note message cannot be blank.")

    notes = ticket.get("notes", [])
    if not isinstance(notes, list):
        raise ValueError("Ticket notes must be stored in a list.")

    highest_number = 0
    for note in notes:
        if not isinstance(note, dict):
            raise ValueError("Existing ticket notes contain invalid data.")

        note_id = note.get("note_id", "")
        if (
            isinstance(note_id, str)
            and note_id.startswith("N")
            and note_id[1:].isdigit()
        ):
            highest_number = max(highest_number, int(note_id[1:]))

    note_id = f"N{highest_number + 1:03d}"
    new_note = {
        "note_id": note_id,
        "author": author.strip(),
        "message": message.strip(),
    }

    # Only mutate the ticket after all existing notes have been checked.
    ticket["notes"] = [*notes, new_note]
    return note_id
