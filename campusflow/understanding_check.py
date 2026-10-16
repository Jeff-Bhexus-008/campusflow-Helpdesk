# campusflow/understanding_check.py

QUESTIONS = [
    {
        "question": (
            "T001 is open and unassigned. "
            "What happens if a user tries to move it "
            "to in_progress?"
        ),
        "options": {
            "A": "Accept the transition",
            "B": "Reject and preserve all data",
            "C": "Resolve it automatically",
            "D": "Delete the ticket",
        },
        "answer": "B",
    },
    {
        "question": (
            "The application contains zero tickets. "
            "What should the resolution percentage be?"
        ),
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "answer": "C",
    },
    {
        "question": (
            "A user searches for title='wifi', "
            "category='Network', status='open'. "
            "Which tickets should match?"
        ),
        "options": {
            "A": "Any ticket matching one filter",
            "B": "Only tickets matching all supplied filters",
            "C": "Every Network ticket",
            "D": "Every open ticket",
        },
        "answer": "B",
    },
    {
        "question": (
            "A resolved ticket receives an Add Note request. "
            "What should happen?"
        ),
        "options": {
            "A": "Append the note anyway",
            "B": "Delete the old notes",
            "C": "Reject until the ticket is reopened",
            "D": "Change the status silently",
        },
        "answer": "C",
    },
    {
        "question": (
            "A JSON file contains two tickets with the same ID. "
            "What should loading do?"
        ),
        "options": {
            "A": "Keep both tickets",
            "B": "Replace memory with duplicate tickets",
            "C": "Reject the load without changing current memory",
            "D": "Rename the IDs silently",
        },
        "answer": "C",
    },
    {
        "question": (
            "A pull request changes validation but has "
            "no negative-case tests. What is the best review action?"
        ),
        "options": {
            "A": "Approve because the application runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge immediately",
            "D": "Ask AI to approve it",
        },
        "answer": "B",
    },
]


def collect_answer(question, input_fn=None, output_fn=None):
    """Display a question and retry until A/B/C/D is supplied."""

    if input_fn is None:
        input_fn = input

    if output_fn is None:
        output_fn = print

    output_fn(question["question"])

    for letter, option in question["options"].items():
        output_fn(f"{letter}. {option}")

    while True:
        answer = input_fn("Choose A, B, C, or D: ")
        answer = answer.strip().upper()

        if answer in question["options"]:
            return answer

        output_fn("Invalid choice. Enter A, B, C, or D.")


def calculate_score(questions, answers):
    """Return the number of correct answers."""

    if len(questions) != len(answers):
        raise ValueError(
            "The number of answers must match the questions."
        )

    score = 0

    for question, answer in zip(questions, answers):
        if answer == question["answer"]:
            score += 1

    return score


def run_understanding_check(input_fn=None, output_fn=None):
    """Run the quiz, calculate the score, and collect explanations."""

    if input_fn is None:
        input_fn = input

    if output_fn is None:
        output_fn = print

    output_fn("\n=== Engineering Understanding Check ===")

    answers = []

    for number, question in enumerate(QUESTIONS, start=1):
        output_fn(f"\nQuestion {number} of {len(QUESTIONS)}")

        answer = collect_answer(
            question,
            input_fn=input_fn,
            output_fn=output_fn,
        )

        answers.append(answer)

    score = calculate_score(QUESTIONS, answers)

    output_fn(f"\nYour final score: {score}/6")

    explanations = []

    for index in (0, 1):
        output_fn(
            f"\nExplain why your answer to Question {index + 1} "
            "is correct."
        )

        explanation = input_fn("Your explanation: ").strip()

        explanations.append({
            "question_number": index + 1,
            "answer": answers[index],
            "explanation": explanation,
        })

    output_fn("\n=== Your Explanations ===")

    for item in explanations:
        output_fn(
            f"Question {item['question_number']}: "
            f"{item['explanation']}"
        )

    return {
        "answers": answers,
        "score": score,
        "explanations": explanations,
    }