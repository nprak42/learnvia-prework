import math
import random
import streamlit as st
from sympy import sympify, simplify


def generate_problem() -> dict:
    a = random.choice(range(2,100))
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


def main():
    st.title("Limit Practice")
    st.write("Evaluate the limit and enter your answer as a fraction or decimal.")

    if "problem" not in st.session_state:
        st.session_state.problem = generate_problem()
        st.session_state.last_result = None
        st.session_state.last_input = ""

    problem = st.session_state.problem
    a, b, c = problem["a"], problem["b"], problem["c"]

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
        if st.button("Submit"):
            result = check_answer(answer_input, a)
            st.session_state.last_result = result
            st.session_state.last_input = answer_input

    with col2:
        if st.button("New Problem"):
            st.session_state.problem = generate_problem()
            st.session_state.last_result = None
            st.session_state.last_input = ""
            st.rerun()

    result = st.session_state.last_result
    if result == "correct":
        st.success("Correct! Well done.")
    elif result == "incorrect":
        st.error("Not quite — give it another try!")
    elif result == "unparseable":
        st.warning("Couldn't read that — enter a number or fraction like 1/2")

    if result is not None:
        with st.expander("Show explanation"):
            show_explanation(problem)


if __name__ == "__main__":
    main()
