"""Unit tests for VERSION 3.  Run:  python -m unittest test_evaluator -v"""
import unittest
from stack_evaluator import Stack, ExpressionEvaluator, FileProcessor, EvaluationError


class TestStack(unittest.TestCase):
    def test_push_pop_order(self):
        s = Stack(); s.push(1); s.push(2)
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)

    def test_peek_does_not_remove(self):
        s = Stack(); s.push(5)
        self.assertEqual(s.peek(), 5)
        self.assertEqual(s.size(), 1)

    def test_empty_errors(self):
        s = Stack()
        with self.assertRaises(IndexError): s.pop()
        with self.assertRaises(IndexError): s.peek()


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.p = FileProcessor()

    def check(self, expr, expected):
        self.assertEqual(self.p.process_line(expr), expected)

    def test_handout_examples(self):
        self.check("3 + 5 * 2", "13")
        self.check("(8 / 4) + 7 * 2", "16")
        self.check("10 - (2 + 3) * 4", "-10")

    def test_left_to_right(self):
        self.check("100 / 4 / 5", "5")
        self.check("10 - 4 - 3", "3")

    def test_brackets(self):
        self.check("((2 + 3) * (4 - 1)) / 5", "3")

    def test_negatives(self):
        self.check("-5 + 12", "7")
        self.check("2 * -3", "-6")
        self.check("-(2 + 3) * 2", "-10")

    def test_decimals_exact(self):
        self.check("0.1 + 0.2", "0.3")
        self.check("7 / 2", "3.5")

    def test_errors(self):
        self.check("8 / (4 - 4)", "Error: division by zero")
        self.check("(3 + 4", "Error: mismatched parentheses")
        self.check("3 + 4)", "Error: mismatched parentheses")
        self.check("3 + * 4", "Error: malformed expression")
        self.check("3 4", "Error: malformed expression")
        self.check("abc", "Error: invalid character 'a'")

    def test_separator_and_blank_kept(self):
        self.check("-----", "-----")
        self.check("", "")


class TestMoreCases(unittest.TestCase):
    def setUp(self):
        self.p = FileProcessor()

    def test_whitespace_ignored(self):
        self.assertEqual(self.p.process_line("   7*  6   "), "42")

    def test_nested_brackets(self):
        self.assertEqual(self.p.process_line("2 * (3 + (4 - (5 - 6)))"), "16")

    def test_big_numbers(self):
        self.assertEqual(self.p.process_line("1000000 * 1000000"), "1000000000000")

    def test_rounding_to_four_places(self):
        self.assertEqual(self.p.process_line("22 / 7"), "3.1429")
        self.assertEqual(self.p.process_line("1 / 3 + 1 / 3 + 1 / 3"), "1")

    def test_invalid_number(self):
        self.assertEqual(self.p.process_line("1.2.3 + 4"), "Error: invalid number '1.2.3'")

    def test_evaluator_raises_error_type(self):
        with self.assertRaises(EvaluationError):
            ExpressionEvaluator().evaluate("4 / 0")


class TestFiles(unittest.TestCase):
    def test_round_trip_keeps_separators(self):
        import os, tempfile
        with tempfile.TemporaryDirectory() as d:
            src, dst = os.path.join(d, "in.txt"), os.path.join(d, "out.txt")
            with open(src, "w") as f:
                f.write("3 + 5 * 2\n-----\n(8 / 4) + 7 * 2\n-----\n4 / 0\n")
            answers, errors = FileProcessor().run(src, dst)
            with open(dst) as f:
                lines = f.read().splitlines()
            self.assertEqual(lines, ["13", "-----", "16", "-----", "Error: division by zero"])
            self.assertEqual((answers, errors), (2, 1))


if __name__ == "__main__":
    unittest.main()
