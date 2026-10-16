# campusflow/search.py

ALLOWED_CATEGORIES = {
    "Network",
    "Hardware",
    "Software",
    "Other",
}

ALLOWED_STATUSES = {
    "open",
    "in_progress",
    "resolved",
}

ALLOWED_PRIORITIES = {
    "critical",
    "high",
    "medium",
    "low",
}


def _get_value(ticket, field):
    """Read a field from either a dictionary or a Ticket object."""
    if isinstance(ticket, dict):
        return ticket[field]

    return getattr(ticket, field)


def _normalise_filter(value, allowed_values, field_name):
    """Validate an optional filter and return its canonical value."""
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(f"{field_name} filter must be text.")

    value = value.strip()

    if not value:
        return None

    for allowed_value in allowed_values:
        if value.casefold() == allowed_value.casefold():
            return allowed_value

    choices = ", ".join(sorted(allowed_values))

    raise ValueError(
        f"Invalid {field_name}: {value}. "
        f"Choose one of: {choices}."
    )


def search_tickets(
    tickets,
    title="",
    category=None,
    status=None,
    priority=None,
):
    """
    Return tickets matching every supplied filter.

    Search is case-insensitive and does not modify tickets.
    """

    if not isinstance(title, str):
        raise ValueError("Title search must be text.")

    search_text = title.strip().casefold().replace("-", "")

    category = _normalise_filter(
        category,
        ALLOWED_CATEGORIES,
        "category",
    )

    status = _normalise_filter(
        status,
        ALLOWED_STATUSES,
        "status",
    )

    priority = _normalise_filter(
        priority,
        ALLOWED_PRIORITIES,
        "priority",
    )

    results = []

    for ticket in tickets:
        ticket_title = (
            _get_value(ticket, "title")
            .casefold()
            .replace("-", "")
        )

        if search_text not in ticket_title:
            continue

        if (
            category is not None
            and _get_value(ticket, "category") != category
        ):
            continue

        if (
            status is not None
            and _get_value(ticket, "status") != status
        ):
            continue

        if (
            priority is not None
            and _get_value(ticket, "priority") != priority
        ):
            continue

        results.append(ticket)

    return results

def sort_search_results(tickets):
    """Sort search results by priority, then numeric ticket ID."""

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    def sort_key(ticket):
        ticket_id = _get_value(ticket, "id")

        if (
            not isinstance(ticket_id, str)
            or len(ticket_id) < 2
            or not ticket_id[1:].isdigit()
        ):
            raise ValueError(
                f"Invalid ticket ID: {ticket_id!r}"
            )

        ticket_priority = _get_value(ticket, "priority")

        if ticket_priority not in priority_order:
            raise ValueError(
                f"Invalid ticket priority: {ticket_priority!r}"
            )

        numeric_id = int(ticket_id[1:])

        return (
            priority_order[ticket_priority],
            numeric_id,
        )

    return sorted(tickets, key=sort_key)


def _prompt_filter(
    prompt,
    allowed_values,
    field_name,
    input_fn,
    output_fn,
):
    """Prompt until the user supplies a valid filter or leaves it blank."""

    while True:
        value = input_fn(prompt).strip()

        if not value:
            return None

        try:
            return _normalise_filter(
                value,
                allowed_values,
                field_name,
            )
        except ValueError as error:
            output_fn(str(error))
            output_fn("Please try again.")


def search_tickets_cli(
    tickets,
    input_fn=None,
    output_fn=None,
):
    """Collect search criteria, search tickets, and display results."""

    if input_fn is None:
        input_fn = input

    if output_fn is None:
        output_fn = print

    output_fn("\n========== SEARCH TICKETS ==========")

    title = input_fn(
        "Title contains (press Enter to skip): "
    )

    category = _prompt_filter(
        "Category (Network/Hardware/Software/Other): ",
        ALLOWED_CATEGORIES,
        "category",
        input_fn,
        output_fn,
    )

    status = _prompt_filter(
        "Status (open/in_progress/resolved): ",
        ALLOWED_STATUSES,
        "status",
        input_fn,
        output_fn,
    )

    priority = _prompt_filter(
        "Priority (critical/high/medium/low): ",
        ALLOWED_PRIORITIES,
        "priority",
        input_fn,
        output_fn,
    )

    results = search_tickets(
        tickets,
        title=title,
        category=category,
        status=status,
        priority=priority,
    )

    if not results:
        output_fn("No matching tickets found.")
        return results

    output_fn(f"\nFound {len(results)} matching ticket(s).")

    for ticket in results:
        output_fn("-" * 40)
        output_fn(f"ID: {_get_value(ticket, 'id')}")
        output_fn(f"Title: {_get_value(ticket, 'title')}")
        output_fn(f"Category: {_get_value(ticket, 'category')}")
        output_fn(f"Priority: {_get_value(ticket, 'priority')}")
        output_fn(f"Status: {_get_value(ticket, 'status')}")

        assigned_to = _get_value(ticket, "assigned_to")
        output_fn(f"Assigned to: {assigned_to or 'Unassigned'}")

    output_fn("-" * 40)

    return results