"""
DCOMP320 Individual Assignment - Stacks Implementation
VERSION 3: Object-oriented design, exact decimal arithmetic, unit tests

Classes:
    Stack                - the LIFO data structure
    Tokenizer            - turns text into tokens
    ExpressionEvaluator  - evaluates tokens with two stacks
    FileProcessor        - reads input.txt and writes output.txt

Uses Python's Decimal so 0.1 + 0.2 gives exactly 0.3 (floats give 0.30000000000000004).
Tests: python -m unittest test_evaluator -v

Author: Abdulai Bah
"""

import os
import sys
from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 28


class EvaluationError(Exception):
    """Raised for any problem with an expression (message shown in output.txt)."""


class Stack:
    """Last In, First Out container."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def size(self):
        return len(self._items)

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return "Stack(%r)" % (self._items,)


class Tokenizer:
    """Splits an expression into Decimal numbers, operators and brackets."""

    OPERATORS = "+-*/"

    def tokenize(self, text):
        tokens = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch.isspace():
                i += 1
            elif ch.isdigit() or ch == ".":
                j = i
                while j < len(text) and (text[j].isdigit() or text[j] == "."):
                    j += 1
                try:
                    tokens.append(Decimal(text[i:j]))
                except InvalidOperation:
                    raise EvaluationError("invalid number '%s'" % text[i:j])
                i = j
            elif ch in self.OPERATORS:
                if self._operand_expected(tokens):
                    if ch == "-":
                        tokens.append("neg")
                    elif ch != "+":
                        raise EvaluationError("malformed expression")
                else:
                    tokens.append(ch)
                i += 1
            elif ch in "()":
                tokens.append(ch)
                i += 1
            else:
                raise EvaluationError("invalid character '%s'" % ch)
        return tokens

    @staticmethod
    def _operand_expected(tokens):
        """True if the next thing must be a number, '(' or a negative sign."""
        return not tokens or not (isinstance(tokens[-1], Decimal) or tokens[-1] == ")")


class ExpressionEvaluator:
    """Evaluates an expression using a value stack and an operator stack."""

    PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}

    def __init__(self):
        self.tokenizer = Tokenizer()

    def evaluate(self, text):
        tokens = self.tokenizer.tokenize(text)
        if not tokens:
            raise EvaluationError("empty expression")
        values, ops = Stack(), Stack()
        for tok in tokens:
            if isinstance(tok, Decimal):
                values.push(tok)
            elif tok in ("(", "neg"):
                ops.push(tok)
            elif tok == ")":
                while not ops.is_empty() and ops.peek() != "(":
                    self._apply(ops, values)
                if ops.is_empty():
                    raise EvaluationError("mismatched parentheses")
                ops.pop()
            else:
                while (not ops.is_empty() and ops.peek() != "("
                       and (ops.peek() == "neg"
                            or self.PRECEDENCE[ops.peek()] >= self.PRECEDENCE[tok])):
                    self._apply(ops, values)
                ops.push(tok)
        while not ops.is_empty():
            if ops.peek() == "(":
                raise EvaluationError("mismatched parentheses")
            self._apply(ops, values)
        if len(values) != 1:
            raise EvaluationError("malformed expression")
        return values.pop()

    @staticmethod
    def _apply(ops, values):
        op = ops.pop()
        if op == "neg":
            if values.is_empty():
                raise EvaluationError("malformed expression")
            values.push(-values.pop())
            return
        if len(values) < 2:
            raise EvaluationError("malformed expression")
        b, a = values.pop(), values.pop()
        if op == "+":
            values.push(a + b)
        elif op == "-":
            values.push(a - b)
        elif op == "*":
            values.push(a * b)
        else:
            if b == 0:
                raise EvaluationError("division by zero")
            values.push(a / b)


class FileProcessor:
    """Reads an input file and writes the results, keeping separator lines."""

    def __init__(self, evaluator=None):
        self.evaluator = evaluator or ExpressionEvaluator()

    @staticmethod
    def format_result(x):
        text = format(x.quantize(Decimal("0.0001")).normalize(), "f")
        return text if text != "-0" else "0"

    @staticmethod
    def is_separator(line):
        s = line.strip()
        return len(s) >= 3 and set(s) == {"-"}

    def process_line(self, line):
        if self.is_separator(line) or not line.strip():
            return line.strip()
        try:
            return self.format_result(self.evaluator.evaluate(line))
        except EvaluationError as e:
            return "Error: %s" % e

    def run(self, in_path, out_path):
        """Process the file and return (answers, errors) counts."""
        with open(in_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        results = [self.process_line(l) for l in lines]
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(results) + "\n")
        errors = sum(1 for r in results if r.startswith("Error:"))
        answers = sum(1 for l, r in zip(lines, results)
                      if l.strip() and not self.is_separator(l) and not r.startswith("Error:"))
        return answers, errors


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    in_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "input.txt")
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "output.txt")
    if not os.path.exists(in_path):
        print("Error: cannot find %s\nPut input.txt next to stack_evaluator.py" % in_path)
        sys.exit(1)
    answers, errors = FileProcessor().run(in_path, out_path)
    print("Done! %d answers and %d error lines written to %s" % (answers, errors, out_path))
