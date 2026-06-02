# Limit Practice App

A Streamlit app that generates randomized calculus limit problems of a specific indeterminate form and checks student answers symbolically. Built as a pre-work drill for students entering a calculus course.

[Live demo](https://calculus-drill.streamlit.app)

---

## What it does

Each problem asks the student to evaluate:

$$\lim_{x \to -1} \sqrt{\dfrac{x + 1}{x^2 + cx + b}}$$

A single integer `a` is drawn at random from [2, 12]. The coefficients `c` and `b` are derived from it:

```
c = a² + 2
b = c − 1
```

This construction guarantees that the denominator factors as `(x + 1)(x + a² + 1)`, so `(x + 1)` always cancels with the numerator. After cancellation the expression simplifies to `√(1 / (x + a² + 1))`, which evaluates cleanly at x = −1 to `1/a`. Every generated problem therefore has an exact rational answer and requires no post-generation validation. The range [2, 12] keeps the coefficients legible and the answers (1/2 through 1/12) pedagogically appropriate for a Calculus I drill.

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
2. **Numeric fallback** — `math.isclose(..., abs_tol=1e-4)` catches valid decimal approximations (e.g. `0.142857` for 1/7). Absolute tolerance is used because the answer range is bounded (1/2 down to 1/39); `1e-4` is tight enough to reject neighbouring wrong answers while accepting any reasonable 4+ decimal-place input a student would type. The old `abs_tol=0.01` was dangerously loose — at `a=39`, answers `1/38` and `1/39` are only `~6.7e-4` apart, which the old tolerance would have passed.

Inputs that fail parsing return `"unparseable"` rather than `"incorrect"` which is a deliberate UX distinction so students aren't penalized for typos.

### Error-specific hints

Because the problem structure is fixed, the most common wrong answers are enumerable. The app checks symbolically for two specific mistakes before falling back to progressive hints:

- **Forgot the square root** — answer equals `1/a²` (the value inside the radical before taking the root)
- **Inverted the fraction** — answer equals `a` instead of `1/a`

Both checks use exact symbolic comparison (`simplify(student − wrong) == 0`), so they fire only when the match is unambiguous. Unmatched wrong answers trigger escalating generic hints based on attempt count.

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
