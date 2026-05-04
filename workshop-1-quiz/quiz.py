from questions import QUESTIONS
from utils import format_question, format_result, display_score


def check_answer(user_answer, correct_answer):
    return user_answer.strip().upper() == correct_answer.upper()


def calculate_score(results):
    score = 0
    for result in results[:-1]:  # BUG: skips the last result
        if result:
            score += 1
    return score


def run_quiz(questions):
    print("\n🐍 Welcome to the Python Trivia Quiz! 🐍")
    print("Answer each question by typing A, B, C, or D.\n")

    results = []

    for i, q in enumerate(questions):
        print(format_question(i, q))
        user_answer = input("\nYour answer: ").strip().upper()
        correct = check_answer(user_answer, q["answer"])
        results.append(correct)
        print(format_result(correct, q["answer"], user_answer))

    score = calculate_score(results)
    print(display_score(score, len(questions)))
    return score


if __name__ == "__main__":
    run_quiz(QUESTIONS)
