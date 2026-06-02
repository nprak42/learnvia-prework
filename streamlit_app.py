import math
import random
import pandas as pd
import streamlit as st
from sympy import sympify, simplify

st.set_page_config(page_title="Limit Practice", layout="centered")


# ---------------------------------------------------------------------------
# Problem generation & answer checking
# ---------------------------------------------------------------------------

def generate_problem() -> dict:
    a = random.choice(range(2, 100))
    c = a**2 + 2
    b = c - 1
    return {"a": a, "c": c, "b": b}


def check_answer(student_str: str, a: int) -> str:
    if not student_str.strip():
        return "unparseable"
    try:
        student = sympify(student_str)
        true_answer = sympify(f"1/{a}")
        if simplify(student - true_answer) == 0:
            return "correct"
        if math.isclose(float(student), float(true_answer), abs_tol=0.01):
            return "correct"
        return "incorrect"
    except Exception:
        return "unparseable"


# ---------------------------------------------------------------------------
# Diagnostic hint detection
# ---------------------------------------------------------------------------

def get_diagnostic_hint(student_str: str, problem: dict) -> str | None:
    a, c = problem["a"], problem["c"]
    try:
        student = sympify(student_str)
        # Forgot the square root: answer is 1/a^2 = 1/(c-2)
        if simplify(student - sympify(f"1/{a**2}")) == 0:
            return "Close — you found what's inside the root. Don't forget to take the square root at the end."
        # Inverted fraction: answer is a instead of 1/a
        if simplify(student - sympify(str(a))) == 0:
            return f"Check your final step — is the limit `{a}` or `1/{a}`? Look at where the 1 ends up."
        # Off-by-one in the factor: used c or c±1 instead of c-2 = a^2
        for wrong_denom in [c, c - 1, c + 1]:
            if simplify(student - sympify(f"1/{wrong_denom}")) == 0:
                return (
                    "Re-check the denominator factor: "
                    f"x² + {c}x + {c - 1} = (x + 1)(x + ?). Substitute carefully."
                )
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


def new_problem():
    st.session_state.problem = generate_problem()
    st.session_state.last_result = None
    st.session_state.last_input = ""
    st.session_state.wrong_attempts = 0
    st.session_state.explanation_opened = False


# ---------------------------------------------------------------------------
# Step-by-step explanation (unchanged logic)
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
# Substitution sandbox
# ---------------------------------------------------------------------------

def _eval_original(x: float, c: float, b: float) -> str:
    """Evaluate sqrt((x+1)/(x^2+cx+b)), returning a formatted string or 'undefined'."""
    denom = x**2 + c * x + b
    if abs(denom) < 1e-12:
        return "undefined (0/0)"
    inner = (x + 1) / denom
    if inner < 0:
        return "undefined (√ of negative)"
    return f"{math.sqrt(inner):.6f}"


def _eval_simplified(x: float, c: float) -> str:
    """Evaluate 1/(x + c-1), the cancelled form, returning a formatted string."""
    denom = x + c - 1
    if abs(denom) < 1e-12:
        return "undefined"
    val = 1 / denom
    if val < 0:
        return "undefined (negative under root)"
    return f"{math.sqrt(val):.6f}"


def show_sandbox(problem: dict):
    a, b, c = problem["a"], problem["b"], problem["c"]
    limit_val = 1 / a

    st.write(
        "Plug in x values close to −1 and watch what happens. "
        "The original expression blows up at x = −1, but the simplified form "
        "stays well-behaved — and both converge to the same limit."
    )

    x_input = st.number_input(
        "Try an x value near −1:",
        value=-0.9,
        min_value=-10.0,
        max_value=10.0,
        step=0.1,
        format="%.4f",
        key="sandbox_x",
    )

    orig = _eval_original(x_input, c, b)
    simp = _eval_simplified(x_input, c)

    col_orig, col_simp = st.columns(2)
    with col_orig:
        st.markdown("**Original expression**")
        st.latex(rf"\sqrt{{\dfrac{{x+1}}{{x^2+{c}x+{b}}}}}")
        if "undefined" in orig:
            st.error(f"x = {x_input:.4f} → {orig}")
        else:
            st.success(f"x = {x_input:.4f} → {orig}")
    with col_simp:
        st.markdown("**After cancelling (x+1)**")
        st.latex(rf"\sqrt{{\dfrac{{1}}{{x+{c-1}}}}}")
        st.success(f"x = {x_input:.4f} → {simp}")

    st.divider()

    # Convergence table: fixed x values approaching -1 from both sides
    st.markdown("**Approaching x = −1 from both sides:**")
    approach_xs = [-1.5, -1.1, -1.01, -1.001, "−1", -0.999, -0.99, -0.9, -0.5]
    rows = []
    for x in approach_xs:
        if x == "−1":
            rows.append({"x": "−1", "original": "undefined (0/0)", "simplified": "undefined (0/0)", "limit": f"{limit_val:.6f}"})
        else:
            rows.append({
                "x": f"{x:.3f}",
                "original": _eval_original(x, c, b),
                "simplified": _eval_simplified(x, c),
                "limit value": f"{limit_val:.6f}",
            })

    df = pd.DataFrame(rows)
    df.columns = ["x", "original f(x)", "simplified f(x)", f"limit = 1/{a}"]
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.caption(
        f"At x = −1 exactly, the original is 0/0. After cancelling (x+1), "
        f"the simplified form gives 1/{a} = {limit_val:.4f} everywhere else — "
        "that's the limit."
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
            if result != "unparseable":
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
        if not st.session_state.explanation_opened:
            st.session_state.solved_count += 1
            st.success(f"Correct! Well done. (Solved: {st.session_state.solved_count})")
        else:
            st.success("Correct! Now you've worked through it!")

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

    # --- Substitution sandbox expander ---
    with st.expander("Why can't I just plug in x = −1?"):
        show_sandbox(problem)


if __name__ == "__main__":
    main()
