from campusflow.tickets import create_ticket
from campusflow.storage import load_tickets, save_tickets
from campusflow.workflow import (
    assign_ticket,
    update_ticket_status,
    get_queue,
    generate_report,
)
from campusflow.search import (
    search_tickets,
    search_tickets_cli,
    sort_search_results,
)

from campusflow.reports import display_report

from campusflow.notes_cli import (
    add_follow_up_note,
    view_ticket_notes,
)

from campusflow.understanding_check import (
    run_understanding_check,
)
from campusflow.notes import add_note
from campusflow.workflow import (
    assign_ticket,
    update_ticket_status,
    get_queue,
    generate_report,
    find_ticket,
)


def save_follow_up_note(tickets, ticket_id, author, message):
    """Create a note and save the updated tickets."""
    note_id = add_note(tickets, ticket_id, author, message)
    save_tickets(tickets)
    return note_id

def display_tickets(tickets):
    """Display tickets in priority order."""
    if not tickets:
        print("\nNo tickets found.")
        return

    for ticket in get_queue(tickets):
        print(
            f"\nID: {ticket['id']}"
            f"\nTitle: {ticket['title']}"
            f"\nCategory: {ticket['category']}"
            f"\nPriority: {ticket['priority']}"
            f"\nStatus: {ticket['status']}"
            f"\nAssigned to: {ticket['assigned_to']}"
        )


def create_new_ticket(tickets):
    """Collect information and create a ticket."""
    try:
        title = input("Ticket title: ")
        category = input("Category (Network/Hardware/Software/Other): ")
        urgency = input("Urgency (low/medium/high): ")
        affected_users = input("Number of affected users: ")

        ticket = create_ticket(
            title, category, urgency, affected_users, tickets
        )

        save_tickets(tickets)
        print(f"\nTicket {ticket['id']} created successfully!")

    except ValueError as error:
        print(f"\nError: {error}")


def assign_existing_ticket(tickets):
    """Assign a ticket to a staff member."""
    ticket_id = input("Ticket ID: ")
    staff_name = input("Staff member's name: ")

    if assign_ticket(tickets, ticket_id, staff_name):
        save_tickets(tickets)
        print("Ticket assigned successfully.")
    else:
        print("Assignment failed. Check the ticket ID and staff name.")


def change_ticket_status(tickets):
    """Update a ticket's status."""
    ticket_id = input("Ticket ID: ")
    status = input("New status (open/in_progress/resolved): ")

    if update_ticket_status(tickets, ticket_id, status):
        save_tickets(tickets)
        print("Ticket status updated successfully.")
    else:
        print("Update failed. Check the ticket ID and status.")


def show_report(tickets):
    """Display complete ticket statistics exactly once."""
    return display_report(tickets)

def main():
    """Run the CampusFlow Helpdesk application."""
    try:
        tickets = load_tickets()
    except (ValueError, OSError) as error:
        print(f"Could not load tickets: {error}")
        return

    while True:
        print("\n===== CAMPUSFLOW HELPDESK =====")
        print("1. Create ticket")
        print("2. View tickets")
        print("3. Assign ticket")
        print("4. Update ticket status")
        print("5. View report")
        print("6. Search tickets")
        print("7. Engineering Understanding Check")
        print("8. View Ticket Notes")
        print("9. Add Follow-up Note")
        print("10. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            create_new_ticket(tickets)
        elif choice == "2":
            display_tickets(tickets)
        elif choice == "3":
            assign_existing_ticket(tickets)
        elif choice == "4":
            change_ticket_status(tickets)
        elif choice == "5":
            show_report(tickets)
        elif choice == "6":
            search_tickets_cli(tickets)
        
        elif choice == "7":
            run_understanding_check()

        elif choice == "8":
            view_ticket_notes(
                lambda ticket_id: find_ticket(tickets, ticket_id)
            )

        elif choice == "9":
            add_follow_up_note(
                lambda ticket_id, author, message:
                    save_follow_up_note(
                        tickets, ticket_id, author, message
                    ),
                lambda ticket_id: find_ticket(tickets, ticket_id),
            )

        elif choice == "10":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please choose 1 to 10.")


if __name__ == "__main__":
    main()