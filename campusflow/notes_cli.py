# campusflow/notes_cli.py


def _get_value(ticket, field):
    """Read a field from a dictionary or Ticket object."""
    if isinstance(ticket, dict):
        if field == "notes":
            return ticket.get(field, [])
        return ticket[field]

    if field == "notes":
        return getattr(ticket, field, [])
    return getattr(ticket, field)


def view_ticket_notes(
    find_ticket_by_id,
    input_fn=None,
    output_fn=None,
):
    """Ask for a ticket ID and display its notes."""
    if input_fn is None:
        input_fn = input
    if output_fn is None:
        output_fn = print

    ticket_id = input_fn("Enter ticket ID: ").strip()
    if not ticket_id:
        output_fn("Ticket ID cannot be empty.")
        return False

    ticket = find_ticket_by_id(ticket_id)
    if ticket is None:
        output_fn("Ticket not found.")
        return False

    notes = _get_value(ticket, "notes")
    if not isinstance(notes, list):
        output_fn("Could not display notes: ticket notes are invalid.")
        return False

    try:
        notes = sorted(notes, key=lambda note: int(note["note_id"][1:]))
    except (KeyError, TypeError, ValueError, IndexError):
        output_fn("Could not display notes: note data is invalid.")
        return False

    if not notes:
        output_fn(f"No notes found for {ticket_id}.")
        return True

    output_fn(f"\nNotes for {ticket_id}:")
    for note in notes:
        output_fn(f"Note ID: {note['note_id']}")
        output_fn(f"Author: {note['author']}")
        output_fn(f"Message: {note['message']}")
        output_fn("-" * 30)
    return True


def add_follow_up_note(
    add_note,
    find_ticket_by_id,
    input_fn=None,
    output_fn=None,
):
    """Collect note details and delegate creation to Engineer A."""
    if input_fn is None:
        input_fn = input
    if output_fn is None:
        output_fn = print

    ticket_id = input_fn("Enter ticket ID: ").strip()
    if not ticket_id:
        output_fn("Ticket ID cannot be empty.")
        return False

    ticket = find_ticket_by_id(ticket_id)
    if ticket is None:
        output_fn("Ticket not found.")
        return False

    author = input_fn("Enter your name or staff label: ")
    message = input_fn("Enter follow-up note: ")

    try:
        result = add_note(ticket_id, author, message)
    except (ValueError, TypeError) as error:
        output_fn(f"Could not add note: {error}")
        return False

    output_fn("Follow-up note added successfully.")
    if result is not None:
        output_fn(f"Result: {result}")
    return True
