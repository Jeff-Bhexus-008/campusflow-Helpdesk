def validate_title(title):
    """Check that the ticket title is not blank."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title cannot be blank.")

    return title.strip()


def validate_category(category):
    """Check and normalize the ticket category."""
    if not isinstance(category, str):
        raise ValueError("Category must be text.")

    allowed_categories = {
        "network": "Network",
        "hardware": "Hardware",
        "software": "Software",
        "other": "Other",
    }

    normalized_category = category.strip().lower()

    if normalized_category not in allowed_categories:
        raise ValueError(
            "Category must be Network, Hardware, Software, or Other."
        )

    return allowed_categories[normalized_category]


def validate_urgency(urgency):
    """Check and normalize the ticket urgency."""
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")

    allowed_urgencies = {"low", "medium", "high"}
    normalized_urgency = urgency.strip().lower()

    if normalized_urgency not in allowed_urgencies:
        raise ValueError("Urgency must be low, medium, or high.")

    return normalized_urgency


def validate_affected_users(affected_users):
    """Require a positive whole number of affected users."""
    if isinstance(affected_users, bool):
        raise ValueError("Affected users must be a positive integer.")

    if isinstance(affected_users, int):
        number = affected_users
    elif isinstance(affected_users, str):
        value = affected_users.strip()

        if not value or not value.isdigit():
            raise ValueError("Affected users must be a positive integer.")

        number = int(value)
    else:
        raise ValueError("Affected users must be a positive integer.")

    if number <= 0:
        raise ValueError("Affected users must be greater than zero.")

    return number


def calculate_priority(urgency, affected_users):
    """Calculate priority using the assessment rules."""
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    if urgency == "high" and affected_users >= 10:
        return "critical"

    elif urgency == "high" or affected_users >= 10:
        return "high"

    elif urgency == "medium" or affected_users >= 3:
        return "medium"

    else:
        return "low"


def generate_ticket_id(tickets):
    """Generate the next available ticket ID."""
    highest_number = 0

    for ticket in tickets:
        ticket_id = ticket.get("id", "")

        if isinstance(ticket_id, str) and ticket_id.startswith("T"):
            number_part = ticket_id[1:]

            if number_part.isdigit():
                highest_number = max(
                    highest_number, int(number_part)
                )

    next_number = highest_number + 1

    while any(
        ticket.get("id") == f"T{next_number:03d}"
        for ticket in tickets
    ):
        next_number += 1

    return f"T{next_number:03d}"


def create_ticket(title, category, urgency, affected_users, tickets):
    """Validate, create, and add a ticket to the ticket list."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be stored in a list.")

    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)
    priority = calculate_priority(urgency, affected_users)

    ticket_id = generate_ticket_id(tickets)

    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    tickets.append(ticket)

    return ticket