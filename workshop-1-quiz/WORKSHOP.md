# 🐍 Fix It With Copilot
### A 10-minute hands-on workshop · PyCon

You've inherited a Python quiz game. It runs — but something's wrong.  
Your mission: use **GitHub Copilot CLI** to document it, test it, and find the bug.  
You won't write a single line of code yourself.

---

## Before You Start

Open a terminal in this Codespace. Then verify Copilot CLI is ready:

```bash
copilot --version
```

Start an interactive Copilot CLI session:

```bash
copilot
```

> 💡 You'll be chatting with Copilot in natural language from here on.  
> It may ask to use tools (like running shell commands or editing files) — **review and approve each one**.

---

## Step 1 — Understand the Code (2 min)

The project has three files: `quiz.py`, `utils.py`, and `questions.py`.  
None of the functions have docstrings, which makes them hard to reason about.

Ask Copilot to fix that:

> *"Add docstrings to every function in @quiz.py and @utils.py that is missing one."*

Review the changes Copilot proposes before approving. Once done, take a quick look at the docstrings — do they match what you'd expect each function to do?

---

## Step 2 — Plan a Test Suite (4 min)

Now that the code is documented, switch Copilot to **plan mode** before asking it to write tests.

Press **`Shift + Tab`** to toggle into plan mode.

Then prompt:

> *"Create a pytest test suite for this project. Write tests for check_answer, calculate_score, format_result, and display_score. Cover normal cases and edge cases."*

Copilot will ask clarifying questions and build a plan. **Read the plan carefully** before approving execution.

Once you approve, Copilot will create a `test_quiz.py` file. Run the tests:

```bash
python -m pytest test_quiz.py -v
```

> ❓ Did all the tests pass? If not — which one failed, and why?

---

## Step 3 — Fix the Bug (2 min)

Press **`Shift + Tab`** to switch back to normal mode.

Tell Copilot what you found:

> *"The tests are failing. Based on the test output, find and fix the bug."*

Once Copilot applies the fix, run the tests again:

```bash
python -m pytest test_quiz.py -v
```

All tests should pass. ✅

---

## Step 4 — Reflect (2 min)

Try playing the (now fixed) quiz:

```bash
python quiz.py
```

Think about what just happened:

- The bug was in `calculate_score` — a single character caused every quiz score to be undercounted by one.
- There were no tests, so it shipped undetected.
- The missing docstrings made the code ambiguous — even for an AI.

**The workflow you just used:**  
`Document → Plan → Test → Fix`  
is the same loop professionals use. Copilot just helped you do it in 10 minutes.

---

## 🎟️ Congratulations!

Collect your ticket and present it at the prize booth for some swag!

