import math
import random
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from sympy import sympify, simplify

st.set_page_config(page_title="Limit Practice", layout="centered")


# ---------------------------------------------------------------------------
# Problem generation & answer checking (unchanged logic)
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
# Visualization: removable discontinuity
# ---------------------------------------------------------------------------

def show_visualization(problem: dict):
    a, c = problem["a"], problem["c"]
    limit_val = 1 / a
    c_minus_1 = c - 1  # denominator of simplified function: x + (c-1)

    slider_val = st.slider(
        "Move x toward −1",
        min_value=-1.49,
        max_value=-0.51,
        value=-0.75,
        step=0.01,
        format="%.2f",
    )

    # Live readout (avoid exactly -1)
    if abs(slider_val - (-1)) < 1e-9:
        st.info("x = −1 is undefined (the hole). Approach from either side.")
    else:
        fx = 1 / (slider_val + c_minus_1)
        st.write(
            f"At x = **{slider_val:.2f}**, f(x) = **{fx:.6f}**  "
            f"(limit = {limit_val:.6f})"
        )

    st.caption(
        f"The function approaches **1/{a} = {limit_val:.4f}** near x = −1 "
        "but is undefined exactly there. That's the limit."
    )

    # --- Plot ---
    # Exclude a small window around -1 to avoid the singularity of the
    # *original* expression; we plot the simplified form 1/(x + c-1)
    x_left = np.linspace(-2.0, -1.005, 400)
    x_right = np.linspace(-0.995, 0.0, 400)
    x_all = np.concatenate([x_left, x_right])
    y_all = 1 / (x_all + c_minus_1)

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(x_all, y_all, color="#2563EB", linewidth=2)

    # Open circle at the hole (-1, 1/a)
    ax.plot(
        -1, limit_val,
        "o",
        markersize=9,
        markerfacecolor="white",
        markeredgecolor="#2563EB",
        markeredgewidth=2,
        zorder=5,
        label=f"hole at (−1, 1/{a})",
    )

    # Dashed horizontal line at y = 1/a
    ax.axhline(limit_val, color="#9CA3AF", linestyle="--", linewidth=1, label=f"y = 1/{a}")

    # Marker at the current slider position
    if abs(slider_val - (-1)) > 1e-4:
        y_slider = 1 / (slider_val + c_minus_1)
        ax.plot(slider_val, y_slider, "o", color="#DC2626", markersize=7, zorder=6, label=f"x = {slider_val:.2f}")

    # Fix y-axis so the hole is always visible regardless of a
    y_pad = limit_val * 1.5
    ax.set_ylim(max(0, limit_val - y_pad), limit_val + y_pad)
    ax.set_xlim(-2.05, 0.05)

    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(
        rf"$f(x) = \dfrac{{1}}{{x + {c_minus_1}}}$ (simplified, showing hole at x = −1)",
        fontsize=10,
    )
    ax.legend(fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


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
            st.success("Correct! Now you've worked through it — nice.")

    elif result == "incorrect":
        diagnostic = get_diagnostic_hint(answer_input, problem)
        if diagnostic:
            st.warning(diagnostic)
        else:
            attempt = st.session_state.wrong_attempts
            if attempt == 1:
                st.info("Start by substituting x = −1 directly. What form do you get?")
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
            if st.button("I've got it — give me a new one", type="primary"):
                new_problem()
                st.rerun()

    # --- Visualization expander ---
    with st.expander("Why can't I just plug in x = −1?"):
        show_visualization(problem)


if __name__ == "__main__":
    main()
