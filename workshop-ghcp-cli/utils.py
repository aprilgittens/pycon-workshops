def format_question(index, question_data):
    lines = [f"\nQ{index + 1}: {question_data['question']}"]
    for choice in question_data["choices"]:
        lines.append(f"  {choice}")
    return "\n".join(lines)


def format_result(correct, answer, user_answer):
    if correct:
        return "✅ Correct!"
    return f"❌ Wrong! The correct answer was {answer}, you answered {user_answer}."


def display_score(score, total):
    percentage = (score / total) * 100
    bar_filled = int(percentage / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
    return (
        f"\n{'='*40}\n"
        f"  Final Score: {score}/{total}  [{bar}]  {percentage:.0f}%\n"
        f"{'='*40}"
    )
