import ast
import html
import math
import operator
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, quote_plus, urlsplit, urlunsplit


OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}


def expand_percentages(expression):
    position = 0
    while match := re.search(r"%(?!\s*[\d.(])", expression[position:]):
        end = position + match.start()
        operand = expression[:end].rstrip()
        start = len(operand)
        if operand.endswith(")"):
            depth = 1
            start -= 1
            while start and depth:
                start -= 1
                depth += (operand[start] == ")") - (operand[start] == "(")
            if depth:
                raise ValueError("Unmatched parentheses")
        else:
            number = re.search(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$", operand)
            if not number:
                raise ValueError("Percentage needs a number or parentheses")
            start = number.start()
        # Preserve percentage nodes for relative addition and subtraction.
        replacement = "(~(" + operand[start:] + "))"
        expression = expression[:start] + replacement + expression[end + 1:]
        position = start + len(replacement)
    return expression


def calculate(expression):
    if len(expression) > 256:
        raise ValueError("Expression is too long")
    if "~" in expression:
        raise ValueError("Use % for percentages")
    tree = ast.parse(expand_percentages(expression).replace("^", "**"), mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 100:
        raise ValueError("Expression is too complex")

    def is_percentage(node):
        while isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            node = node.operand
        return isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert)

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
            value = visit(node.operand) / 100
        elif isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub)) and is_percentage(node.right):
                right *= left
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent must be between -100 and 100")
            value = OPERATORS[type(node.op)](left, right)
        else:
            raise ValueError("Use numbers, parentheses, and + - * / // % ^")
        if isinstance(value, complex) or not math.isfinite(value) or abs(value) > 1e100:
            raise ValueError("Result is outside the supported range")
        return value

    value = visit(tree.body)
    return str(value) if isinstance(value, int) else format(value, ".15g")


def destination(text):
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1]
    if text.startswith(("/", "~/", "./", "../")):
        return Path(os.path.abspath(os.path.expanduser(text))).as_uri()
    # Only these URI schemes are launchable; other input remains a web search.
    if re.match(r"^(?:https?://|file:)", text, re.I):
        parts = urlsplit(text)
        if parts.scheme.lower() == "file":
            if parts.netloc.lower() not in ("", "localhost") or not parts.path.startswith("/"):
                raise ValueError("Use a local file URL: file:///absolute/path")
        elif not parts.hostname or re.search(r"\s", parts.netloc):
            raise ValueError("URL needs a valid host")
        return urlunsplit((parts.scheme, parts.netloc,
                          quote(parts.path, safe="/%:@!$&'()*+,;=-._~"),
                          quote(parts.query, safe="%=&?/:;+,$@!()*'-._~"),
                          quote(parts.fragment, safe="%/?@:!$&'()*+,;=-._~")))
    if re.fullmatch(r"(?:localhost|(?:[\w-]+\.)+[a-zA-Z]{2,}|(?:\d{1,3}\.){3}\d{1,3})(?::\d+)?(?:[/?#][^\s]*)?", text):
        return "https://" + text
    return "https://duckduckgo.com/?q=" + quote_plus(text)


def message(text):
    print("\0message\x1f" + html.escape(text))


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        return
    text = sys.argv[1].strip()
    info = os.environ.get("ROFI_INFO", "")
    if os.environ.get("ROFI_RETV") == "1" and info.startswith("calc:"):
        value = info.removeprefix("calc:")
        if shutil.which("xclip"):
            subprocess.run(["xclip", "-selection", "clipboard"], input=value.encode(),
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        else:
            message("Install xclip to copy results; result: " + value)
            print(value + "\0info\x1fcalc:" + value)
        return

    explicit = text.startswith("=")
    arithmetic = not text.startswith(("/", "./", "../")) and re.fullmatch(r"[\d\s.eE+*/%()^\-]+", text) and re.search(r"\d", text) and re.search(r"[+*/%()^\-]", text)
    try:
        if explicit or arithmetic:
            value = calculate(text[1:].strip() if explicit else text)
            message(text + " = " + value + " — Enter to copy")
            print(value + "\0icon\x1faccessories-calculator\x1finfo\x1fcalc:" + value)
        else:
            subprocess.Popen(["xdg-open", destination(text)], start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    except (ValueError, SyntaxError, ArithmeticError) as error:
        message("Cannot process input: " + str(error).splitlines()[0])
        print("Edit your input and try again\0nonselectable\x1ftrue")


if __name__ == "__main__":
    main()
