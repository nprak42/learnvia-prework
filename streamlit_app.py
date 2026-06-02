import math
import random
import streamlit as st
from sympy import sympify, simplify

st.set_page_config(page_title="Limit Practice", layout="centered")


# ---------------------------------------------------------------------------
# Problem generation & answer checking
# ---------------------------------------------------------------------------

def generate_problem() -> dict:
    a = random.choice(range(2, 40))
    c = a**2 + 2
    b = c - 1
    return {"a": a, "c": c, "b": b}


def check_answer(student_str: str, a: int) -> str:
    if not student_str.strip():
        return "unparseable"
    try:
        student = sympify(student_str)
        # Reject symbolic (non-numeric) expressions — e.g. bare variable names.
        # is_number is False for anything containing free symbols.
        if not student.is_number:
            return "unparseable"
        true_answer = sympify(f"1/{a}")
        if simplify(student - true_answer) == 0:
            return "correct"
        # Numeric fallback for decimals that symbolic simplification may not recognise as equal. Uses relative tolerance to stay accurate at small answer values. float() is safe here because is_number passed.
        if math.isclose(float(student), float(true_answer), abs_tol=1e-4):
            return "correct"
        return "incorrect"
    except Exception:
        return "unparseable"


# ---------------------------------------------------------------------------
# Diagnostic hint detection
# ---------------------------------------------------------------------------

def get_diagnostic_hint(student_str: str, problem: dict) -> str | None:
    a = problem["a"]
    try:
        student = sympify(student_str)
        # Forgot the square root: answer is 1/a² (the value inside the root)
        if simplify(student - sympify(f"1/{a**2}")) == 0:
            return "Close — you found the value inside the square root. Don't forget to take the square root at the end."
        # Inverted fraction: answer is a instead of 1/a
        if simplify(student - sympify(str(a))) == 0:
            return f"Check your final step — is the limit {a} or 1/{a}? Look at where the 1 ends up after cancellation."
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------

def init_state():
    if "problem" not in st.session_state:
        st.session_state.problem = generate_problem()
        st.session_state.last_result = None
        st.session_state.last_input = ""
        st.session_state.wrong_attempts = 0
        st.session_state.explanation_opened = False
        st.session_state.solved_count = 0
        st.session_state.counted = False  # guards against double-increment on rerun


def new_problem():
    st.session_state.problem = generate_problem()
    st.session_state.last_result = None
    st.session_state.last_input = ""
    st.session_state.wrong_attempts = 0
    st.session_state.explanation_opened = False
    st.session_state.counted = False


# ---------------------------------------------------------------------------
# Step-by-step explanation
# ---------------------------------------------------------------------------

def show_explanation(problem: dict):
    a, b, c = problem["a"], problem["b"], problem["c"]
    c_minus_1 = c - 1
    c_minus_2 = c - 2

    st.write("**Step 1: Check the form at x = −1**")
    st.latex(r"\text{Numerator: } (-1) + 1 = 0")
    st.latex(
        rf"\text{{Denominator: }} (-1)^2 + {c}(-1) + {b} = 1 - {c} + {b} = 0"
    )
    st.write("Both are 0, so this is the indeterminate form 0/0. Factor to resolve it.")

    st.write("**Step 2: Factor the denominator**")
    st.latex(rf"x^2 + {c}x + {b} = (x + 1)(x + {c_minus_1})")

    st.write("**Step 3: Cancel (x + 1)**")
    st.latex(
        rf"\frac{{x + 1}}{{(x + 1)(x + {c_minus_1})}} = \frac{{1}}{{x + {c_minus_1}}}"
    )

    st.write("**Step 4: Evaluate at x = −1**")
    st.latex(rf"\frac{{1}}{{-1 + {c_minus_1}}} = \frac{{1}}{{{c_minus_2}}}")

    st.write("**Step 5: Take the square root**")
    st.latex(
        rf"\sqrt{{\frac{{1}}{{{c_minus_2}}}}} = \frac{{1}}{{\sqrt{{{c_minus_2}}}}} = \frac{{1}}{{{a}}}"
    )


# ---------------------------------------------------------------------------
# Key Insight
# ---------------------------------------------------------------------------

def show_key_insight(problem: dict):
    c, b = problem["c"], problem["b"]

    st.write(
        "When you substitute x = −1 into this expression, both the numerator "
        "and denominator equal zero, producing the indeterminate form 0/0. "
        "This means direct substitution cannot give you the limit."
    )
    st.latex(
        rf"\text{{At }} x = -1: \quad \frac{{(-1)+1}}{{(-1)^2 + {c}(-1) + {b}}} = \frac{{0}}{{0}}"
    )
    st.write(
        "A 0/0 result doesn't mean the limit doesn't exist — it means the expression "
        "is not yet in a form you can evaluate. For rational expressions like this one, "
        "0/0 at a point signals that the numerator and denominator share a common factor "
        "that can be cancelled."
    )
    st.write(
        "Once that factor is cancelled, the resulting expression is continuous at x = −1 "
        "and can be evaluated by direct substitution. The limit exists and equals a finite value."
    )
    st.write("**The method for this problem type:**")
    st.markdown(
        "1. Substitute the target value — confirm you get 0/0\n"
        "2. Factor numerator and denominator\n"
        "3. Cancel the shared factor\n"
        "4. Substitute the target value into the simplified expression\n"
        "5. Apply any remaining operations (here, the square root)"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    init_state()

    problem = st.session_state.problem
    a, b, c = problem["a"], problem["b"], problem["c"]

    # Header row: title + solved counter
    col_title, col_counter = st.columns([4, 1])
    with col_title:
        st.title("Limit Practice")
    with col_counter:
        if st.session_state.solved_count > 0:
            st.metric("Solved", st.session_state.solved_count)

    st.write("Evaluate the limit and enter your answer as a fraction or decimal.")

    # Problem display in a bordered container
    with st.container(border=True):
        st.latex(
            rf"\lim_{{x \to -1}} \sqrt{{\dfrac{{x + 1}}{{x^2 + {c}x + {b}}}}}"
        )

    answer_input = st.text_input(
        "Your answer:",
        value=st.session_state.last_input,
        key="answer_input",
        placeholder="e.g. 1/2 or 0.5",
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Submit", type="primary"):
            result = check_answer(answer_input, a)
            if result == "incorrect":
                st.session_state.wrong_attempts += 1
            st.session_state.last_result = result
            st.session_state.last_input = answer_input

    with col2:
        if st.button("New Problem"):
            new_problem()
            st.rerun()

    # --- Feedback ---
    result = st.session_state.last_result

    if result == "correct":
        if not st.session_state.counted:
            st.session_state.solved_count += 1
            st.session_state.counted = True
        if not st.session_state.explanation_opened:
            st.success(f"Correct! Well done. (Solved: {st.session_state.solved_count})")
        else:
            st.success(f"Correct! You worked through it and got there. (Solved: {st.session_state.solved_count})")

    elif result == "incorrect":
        diagnostic = get_diagnostic_hint(answer_input, problem)
        if diagnostic:
            st.warning(diagnostic)
        else:
            attempt = st.session_state.wrong_attempts
            if attempt == 1:
                st.info("Start by substituting x = −1 directly. What form do you observe?")
            elif attempt == 2:
                st.info(
                    "You should get 0/0. That means the numerator and denominator share "
                    "a factor. What cancels?"
                )
            else:
                st.info(
                    "Open 'Show explanation' below to see the full steps, "
                    "then try a fresh problem."
                )

    elif result == "unparseable":
        st.warning("Couldn't read that — enter a number or fraction like 1/2")

    # --- Explanation expander ---
    if result is not None:
        with st.expander("Show explanation"):
            st.session_state.explanation_opened = True
            show_explanation(problem)

            st.divider()
            st.markdown("**Ready to prove you've got it?**")
            if st.button("I've got it. Give me a new one", type="primary"):
                new_problem()
                st.rerun()

    # --- Key Insight expander ---
    with st.expander("Key Insight: why direct substitution fails here"):
        show_key_insight(problem)


if __name__ == "__main__":
    main()
