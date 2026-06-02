# Limit Practice App

A Streamlit app that generates randomized calculus limit problems of a specific indeterminate form and checks student answers symbolically. Built as a pre-work drill for students entering a calculus course.

**Live demo: calculus-drill.streamlit.app**

---

## What it does

Each problem asks the student to evaluate:

$$\lim_{x \to -1} \sqrt{\dfrac{x + 1}{x^2 + cx + b}}$$

The parameters are constructed so that the denominator always factors with `(x + 1)`, creating a removable discontinuity at x = −1. After cancellation, the expression reduces to a form that evaluates to a clean rational value — so every generated problem has an exact closed-form answer.

---

## User flow

1. A randomized limit problem is displayed
2. The student submits an answer (fraction or decimal)
3. The system checks correctness using symbolic evaluation
4. If incorrect, targeted hints are shown based on the specific error made
5. A full step-by-step solution is available in an expandable section
6. A key insight explains the reasoning pattern for this class of problems

---

## Design choices

### Answer checking: symbolic + numeric fallback

Student input is passed through two checks in sequence:

1. **Symbolic equality via `sympy`** — `sympify` parses the input and `simplify(student - true_answer) == 0` checks exact equivalence. This accepts `1/7`, `sqrt(1/49)`, and equivalent expressions without hardcoding formats.
2. **Numeric fallback** — `math.isclose(..., abs_tol=0.01)` catches valid decimal approximations that symbolic simplification might not recognize as equal (e.g. `0.142857`).

Inputs that fail parsing return `"unparseable"` rather than `"incorrect"` which is a deliberate UX distinction so students aren't penalized for typos.

### Error-specific hints

Because the problem structure is fixed, common wrong answers are enumerable. The app checks symbolically for three specific mistakes which are: forgetting the square root, inverting the fraction, and off-by-one errors in factoring. 

### Explanation and mastery loop

The step-by-step solution is collapsed by default to prevent students from reading ahead. After viewing it, a prominent call-to-action prompts the student to solve a new problem, to help close the learning loop between seeing a worked example and demonstrating independent mastery.

### Session state

Streamlit reruns the entire script on every interaction. Problem state is stored in `st.session_state` to survive these reruns, so submitting an answer never changes the displayed problem.

---

## Design constraints

- **Single problem type** This app is intentionally scoped to one class of limits to keep focus on procedural mastery rather than broad problem classification. Extending to other limit types would require a more general problem representation and matching explanation renderer.
- **No cross-session persistence** Scores reset on page reload. For a drill tool at this scope, adding a backend would introduce auth and storage complexity with minimal pedagogical benefit.
- **`sympy` startup cost** — `sympify` is slow on first call. Acceptable for low-traffic use; a high-traffic deployment might pre-warm a process pool.
- **Input evaluation** — `sympify` evaluates arbitrary strings. In this deployment (Streamlit Community Cloud, no persistent data, isolated containers) the blast radius is limited to the session. A backend deployment should restrict input to a safe character subset.

---

## Running locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
