PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

VALID_STATUSES = {"open", "in_progress", "resolved"}


def find_ticket(tickets, ticket_id):
    """Find a ticket using its ID."""
    for ticket in tickets:
        if str(ticket.get("id")) == str(ticket_id).strip():
            return ticket
    return None


def assign_ticket(tickets, ticket_id, assigned_to):
    """Assign an existing ticket to a support staff member."""
    ticket = find_ticket(tickets, ticket_id)

    if ticket is None or ticket.get("status") == "resolved":
        return False

    if not isinstance(assigned_to, str) or not assigned_to.strip():
        return False

    ticket["assigned_to"] = assigned_to.strip()
    return True


def update_ticket_status(tickets, ticket_id, new_status):
    """Apply allowed ticket status transitions.

    Allowed transitions:
    open -> in_progress (must be assigned)
    in_progress -> resolved
    resolved -> open (reopen)
    A ticket may remain in its current status.
    """
    ticket = find_ticket(tickets, ticket_id)
    if ticket is None or not isinstance(new_status, str):
        return False

    status = new_status.strip().lower().replace(" ", "_")
    current = ticket.get("status")

    if status not in VALID_STATUSES:
        return False

    if status == current:
        return True

    allowed = {
        "open": {"in_progress"},
        "in_progress": {"resolved"},
        "resolved": {"open"},
    }

    if status not in allowed.get(current, set()):
        return False

    if status == "in_progress" and not ticket.get("assigned_to"):
        return False

    ticket["status"] = status
    return True


def get_queue(tickets):
    """Return tickets in priority order without changing the input list."""
    return sorted(
        tickets,
        key=lambda ticket: (
            PRIORITY_ORDER.get(
                str(ticket.get("priority", "")).lower(), 99
            ),
            int(ticket["id"][1:])
            if isinstance(ticket.get("id"), str)
            and ticket["id"].startswith("T")
            and ticket["id"][1:].isdigit()
            else float("inf"),
        ),
    )


def generate_report(tickets):
    """Count tickets by status and priority."""
    report = {
        "total": len(tickets),
        "by_status": {
            "open": 0,
            "in_progress": 0,
            "resolved": 0,
        },
        "by_priority": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
    }

    for ticket in tickets:
        status = ticket.get("status", "")
        priority = ticket.get("priority", "")

        if status in report["by_status"]:
            report["by_status"][status] += 1
        if priority in report["by_priority"]:
            report["by_priority"][priority] += 1

    return report
