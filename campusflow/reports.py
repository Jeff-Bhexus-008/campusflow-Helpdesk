# campusflow/reports.py

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

STATUSES = (
    "open",
    "in_progress",
    "resolved",
)

PRIORITIES = (
    "critical",
    "high",
    "medium",
    "low",
)

CATEGORIES = (
    "Network",
    "Hardware",
    "Software",
    "Other",
)


def _get_value(ticket, field):
    """Read a field from a dictionary or Ticket object."""
    if isinstance(ticket, dict):
        return ticket[field]

    return getattr(ticket, field)


def get_work_queue(tickets):
    """
    Return only open tickets.

    Sort by critical, high, medium, low,
    then by ascending numeric ticket ID.
    """

    open_tickets = [
        ticket
        for ticket in tickets
        if _get_value(ticket, "status") == "open"
    ]

    def sort_key(ticket):
        priority = _get_value(ticket, "priority")
        ticket_id = _get_value(ticket, "id")

        if priority not in PRIORITY_ORDER:
            raise ValueError(
                f"Invalid priority: {priority!r}"
            )

        if (
            not isinstance(ticket_id, str)
            or len(ticket_id) < 2
            or not ticket_id[1:].isdigit()
        ):
            raise ValueError(
                f"Invalid ticket ID: {ticket_id!r}"
            )

        return (
            PRIORITY_ORDER[priority],
            int(ticket_id[1:]),
        )

    return sorted(open_tickets, key=sort_key)


def generate_report(tickets):
    """Generate the required ticket statistics."""

    tickets = list(tickets)

    by_status = {
        status: 0
        for status in STATUSES
    }

    by_priority = {
        priority: 0
        for priority in PRIORITIES
    }

    by_category = {
        category: 0
        for category in CATEGORIES
    }

    for ticket in tickets:
        status = _get_value(ticket, "status")
        priority = _get_value(ticket, "priority")
        category = _get_value(ticket, "category")

        if status not in by_status:
            raise ValueError(
                f"Invalid status in report: {status!r}"
            )

        if priority not in by_priority:
            raise ValueError(
                f"Invalid priority in report: {priority!r}"
            )

        if category not in by_category:
            raise ValueError(
                f"Invalid category in report: {category!r}"
            )

        by_status[status] += 1
        by_priority[priority] += 1
        by_category[category] += 1

    total_tickets = len(tickets)
    resolved_count = by_status["resolved"]

    unresolved_count = (
        by_status["open"]
        + by_status["in_progress"]
    )

    resolution_percentage = (
        resolved_count / total_tickets * 100
        if total_tickets
        else 0.0
    )

    return {
        "total_tickets": total_tickets,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "unresolved_count": unresolved_count,
        "resolved_count": resolved_count,
        "resolution_percentage": resolution_percentage,
    }


def display_report(tickets, output_fn=None):
    """Generate and display the report."""

    if output_fn is None:
        output_fn = print

    report = generate_report(tickets)

    output_fn("\n========== CAMPUSFLOW REPORT ==========")
    output_fn(f"Total tickets: {report['total_tickets']}")

    output_fn("\nTickets by status:")

    for status, count in report["by_status"].items():
        output_fn(f"  {status}: {count}")

    output_fn("\nTickets by priority:")

    for priority, count in report["by_priority"].items():
        output_fn(f"  {priority}: {count}")

    output_fn("\nTickets by category:")

    for category, count in report["by_category"].items():
        output_fn(f"  {category}: {count}")

    output_fn(
        f"\nUnresolved tickets: {report['unresolved_count']}"
    )

    output_fn(
        f"Resolved tickets: {report['resolved_count']}"
    )

    output_fn(
        "Resolution percentage: "
        f"{report['resolution_percentage']:.2f}%"
    )

    output_fn("=======================================")

    return report