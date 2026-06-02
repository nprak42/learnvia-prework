# Limit Practice — Calculus Drill App

A Streamlit app that generates randomized calculus limit problems and checks student answers symbolically. Built as a pre-work drill for students entering a calculus course.

**Live demo: calculus-drill.streamlit.app** 

---

## What it does

Each problem asks the student to evaluate:

$$\lim_{x \to -1} \sqrt{\dfrac{x + 1}{x^2 + cx + b}}$$

The student types a numeric answer (fraction or decimal), gets immediate feedback, and can reveal a full step-by-step explanation.

---

## Design choices

### Problem generation: guaranteeing a clean answer

The quadratic denominator is constructed so that:
1. `x = -1` is always a root (enabling cancellation with the numerator `x + 1`)
2. The limit resolves to `1/a` for a random integer `a`

Given a random integer `a ∈ [2, 99]`, the problem is built as:

```
c = a² + 2
b = c - 1  →  x² + cx + b = (x + 1)(x + a²+1)
```

After cancelling `(x + 1)`, the simplified expression is `1 / (x + a²+1)`. Evaluating at `x = -1` gives `1 / a²`, and taking the square root gives `1 / a` — always a clean rational answer. This avoids the need to validate or reject generated problems; every `a` produces a valid, well-formed problem with an exact closed-form answer.

### Answer checking: symbolic + numeric fallback

Student input is passed through two checks in sequence:

1. **Symbolic equality via `sympy`** — `sympify` parses the input and `simplify(student - true_answer) == 0` checks exact equivalence. This accepts `1/7`, `sqrt(1/49)`, and equivalent expressions without hardcoding formats.
2. **Numeric fallback** — `math.isclose(..., abs_tol=0.01)` catches valid decimal approximations that symbolic simplification might not recognize as equal (e.g. `0.142857`).

Inputs that fail parsing return `"unparseable"` rather than `"incorrect"` — a deliberate UX distinction so students aren't penalized for typos.

### Step-by-step explanation

The explanation is shown only after a submission (correct or incorrect) and is collapsed behind an expander by default. This prevents students from reading ahead before attempting the problem.

The explanation reconstructs the full factoring and cancellation steps from the stored problem parameters, so it always matches the specific problem on screen.

### Session state

Streamlit reruns the entire script on every interaction. Problem state is stored in `st.session_state` to survive these reruns. The `last_result` and `last_input` fields let the feedback message and explanation persist after the student submits, without re-triggering the check on the next rerender.

---

## Constraints and tradeoffs

- **No persistence** — scores and attempts are not tracked across sessions. This is intentional for a simple drill tool; adding a backend would require auth and a database for minimal benefit at this scope.
- **Single problem type** — the app only generates one class of limit (0/0 indeterminate form resolved by factoring). Extending to other limit types would require a more general problem representation and matching explanation renderer.
- **`sympy` startup cost** — `sympify` is relatively slow on first call. For a low-traffic drill app this is acceptable; a high-traffic deployment might pre-warm a process pool.
- **Input is arbitrary code** — `sympify` evaluates strings. SymPy mitigates this, but for a production deployment the input should be sanitized or restricted to a safe subset.

---

## Running locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
