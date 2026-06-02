"""
Pure logic tests for streamlit_app.py.
UI flow (session_state, rendering) tested manually.
"""
from sympy import sqrt, Rational, simplify

from streamlit_app import check_answer, generate_problem, get_diagnostic_hint


# ---------------------------------------------------------------------------
# check_answer: input-format matrix (a=7, correct answer 1/7)
# ---------------------------------------------------------------------------

class TestCheckAnswer:
    def test_exact_fraction(self):
        assert check_answer("1/7", 7) == "correct"

    def test_decimal_approximation(self):
        # 0.142857 is 1/7 truncated to 6 places; off by ~1.4e-7 < abs_tol=1e-4
        assert check_answer("0.142857", 7) == "correct"

    def test_sympy_sqrt_expression(self):
        assert check_answer("sqrt(1/49)", 7) == "correct"

    def test_whitespace_stripped(self):
        assert check_answer("  1/7  ", 7) == "correct"

    def test_empty_string(self):
        assert check_answer("", 7) == "unparseable"

    def test_whitespace_only(self):
        assert check_answer("   ", 7) == "unparseable"

    def test_bare_variable_name(self):
        # sympify("abc") returns a Symbol, not a number — must be unparseable
        assert check_answer("abc", 7) == "unparseable"

    def test_wrong_integer(self):
        assert check_answer("2", 7) == "incorrect"

    def test_wrong_fraction(self):
        assert check_answer("1/8", 7) == "incorrect"

    def test_fraction_at_boundary_a(self):
        # Lowest valid a; answer is 1/2
        assert check_answer("1/2", 2) == "correct"

    def test_negative_answer_rejected(self):
        # Principal square root is positive; -1/7 must be incorrect
        # Verify the float path also rejects it: math.isclose(-0.1428, 0.1428) is False
        assert check_answer("-1/7", 7) == "incorrect"

    def test_zero_rejected(self):
        assert check_answer("0", 7) == "incorrect"


# ---------------------------------------------------------------------------
# Tolerance: abs_tol=1e-4 accepts reasonable decimals, rejects close neighbours
# ---------------------------------------------------------------------------

class TestTolerance:
    def test_six_decimal_place_approximation_accepted(self):
        # 0.14285714 ≈ 1/7, error ≈ 2e-9 << 1e-4
        assert check_answer("0.14285714", 7) == "correct"

    def test_neighbouring_fraction_rejected(self):
        # a=40 is the top of the generated range: |1/39 - 1/40| ≈ 6.4e-4 > abs_tol=1e-4,
        # so 1/39 must be rejected when the answer is 1/40.
        assert check_answer("1/39", 40) == "incorrect"

    def test_exact_fraction_at_high_a(self):
        # a=40 is the top of the generated range; confirm the grader accepts it.
        assert check_answer("1/40", 40) == "correct"


# ---------------------------------------------------------------------------
# Generation invariant: test the actual generate_problem() function
# ---------------------------------------------------------------------------

class TestGenerationInvariant:
    def _assert_invariants(self, problem):
        a, b, c = problem["a"], problem["b"], problem["c"]
        # c and b derived solely from a
        assert c == a**2 + 2, f"c invariant failed for a={a}"
        assert b == c - 1,    f"b invariant failed for a={a}"
        # At x=-1, both numerator and denominator are 0
        assert (-1) + 1 == 0
        assert (-1)**2 + c * (-1) + b == 0, f"denominator not 0 at x=-1 for a={a}"
        # After cancellation: 1/(c-2) == 1/a²
        assert c - 2 == a**2, f"simplified denominator wrong for a={a}"
        # Limit equals 1/a
        limit = sqrt(Rational(1, c - 2))
        assert simplify(limit - Rational(1, a)) == 0, f"limit != 1/a for a={a}"

    def test_invariants_hold_across_full_range(self):
        # Run enough samples to cover the full a range many times over.
        # Because generate_problem() picks randomly, 200 draws gives P(missing
        # any single value from range(2,40)) < (37/38)^200 < 0.5%.
        for _ in range(200):
            self._assert_invariants(generate_problem())

    def test_a_within_declared_range(self):
        for _ in range(200):
            a = generate_problem()["a"]
            assert 2 <= a <= 40, f"a={a} outside [2, 40]"

    def test_check_answer_accepts_correct_string_for_full_range(self):
        # Verify the grader agrees with the generator for every possible a.
        for a in range(2, 41):
            assert check_answer(f"1/{a}", a) == "correct", f"grader rejected 1/{a}"


# ---------------------------------------------------------------------------
# Diagnostic hints
# ---------------------------------------------------------------------------

def _problem_for(a: int) -> dict:
    c = a**2 + 2
    return {"a": a, "c": c, "b": c - 1}


class TestDiagnosticHints:
    def test_forgot_square_root_hint(self):
        p = _problem_for(7)
        hint = get_diagnostic_hint("1/49", p)   # 1/49 == 1/a²
        assert hint is not None
        assert "square root" in hint.lower()

    def test_inverted_fraction_hint(self):
        p = _problem_for(7)
        hint = get_diagnostic_hint("7", p)      # 7 == a instead of 1/7
        assert hint is not None
        assert "1/7" in hint

    def test_no_hint_for_unrecognised_wrong_answer(self):
        assert get_diagnostic_hint("1/3", _problem_for(7)) is None

    def test_no_hint_for_correct_answer(self):
        assert get_diagnostic_hint("1/7", _problem_for(7)) is None

    def test_hints_consistent_across_a_values(self):
        # Spot-check a few other a values so hints aren't hardcoded to a=7
        for a in [2, 5, 12]:
            p = _problem_for(a)
            forgot_root = get_diagnostic_hint(f"1/{a**2}", p)
            inverted    = get_diagnostic_hint(str(a), p)
            assert forgot_root is not None, f"forgot-root hint missing for a={a}"
            assert inverted    is not None, f"inverted hint missing for a={a}"
