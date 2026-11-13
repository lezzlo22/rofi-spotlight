import contextlib
import io
import os
import unittest
from unittest.mock import patch

from actions import calculate, destination, main


class ActionsTest(unittest.TestCase):
    def test_calculator(self):
        for expression, expected in [
            ("12*7+3", "87"), ("(10+5)/3", "5"), ("2^8", "256"),
            ("-5+2", "-3"), ("10%3", "1"), ("1e3/4", "250"),
            ("50%", "0.5"), ("200*10%", "20"), ("(10+5)%", "0.15"),
            ("50%^2", "0.25"), ("50% + 25%", "0.625"),
            ("1e-2%", "0.0001"), ("-50%", "-0.5"),
            ("(50% + 25%)%", "0.00625"), ("10 % (3)", "1"),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(calculate(expression), expected)

    def test_relative_percentages(self):
        for expression, expected in [
            ("50-10%", "45"), ("50+10%", "55"),
            ("200+10%", "220"), ("50-(5+5)%", "45"),
            ("50-(10%)", "45"), ("50+-10%", "45"),
            ("50-10%-10%", "40.5"), ("(50-10%)*2", "90"),
            ("50-10/100", "49.9"), ("50/10%", "500"),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(calculate(expression), expected)

    def test_invalid_or_unbounded_calculations(self):
        for expression in ["1/0", "2**100000000", "9**9**9", "1e999", "(-1)**0.5",
                           "__import__('os').system('true')", "[1]*100", "True", "1+",
                           "%", "(10+5%", "10+5)%", "~10"]:
            with self.subTest(expression=expression):
                with self.assertRaises((ValueError, SyntaxError, ArithmeticError)):
                    calculate(expression)

    def test_destinations(self):
        cases = {
            "example.com": "https://example.com",
            "example.com?q=hello#top": "https://example.com?q=hello#top",
            "http://localhost:3000": "http://localhost:3000",
            "http://127.0.0.1:8000/a": "http://127.0.0.1:8000/a",
            "https://example.com/a b": "https://example.com/a%20b",
            "file:///home/me/My File.pdf": "file:///home/me/My%20File.pdf",
            "file:///home/me/My%20File.pdf": "file:///home/me/My%20File.pdf",
            "file://localhost/tmp/a": "file://localhost/tmp/a",
            "file:/tmp/a b.pdf": "file:///tmp/a%20b.pdf",
            '"file:///tmp/a b.pdf"': "file:///tmp/a%20b.pdf",
            "/tmp/a b.pdf": "file:///tmp/a%20b.pdf",
            "'/tmp/a b.pdf'": "file:///tmp/a%20b.pdf",
            "/tmp/100% #1?.pdf": "file:///tmp/100%25%20%231%3F.pdf",
            "hello world": "https://duckduckgo.com/?q=hello+world",
            "javascript:alert(1)": "https://duckduckgo.com/?q=javascript%3Aalert%281%29",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(destination(text), expected)
        for text in ["file://remote/tmp/a", "file:relative.pdf", "https:///missing-host"]:
            with self.assertRaises(ValueError):
                destination(text)

    def test_home_and_relative_paths(self):
        with patch.dict(os.environ, {"HOME": "/home/example"}):
            self.assertEqual(destination("~/My File.pdf"), "file:///home/example/My%20File.pdf")
        with patch("actions.os.getcwd", return_value="/tmp/work"):
            self.assertEqual(destination("./My File.pdf"), "file:///tmp/work/My%20File.pdf")
            self.assertEqual(destination("../file.pdf"), "file:///tmp/file.pdf")

    def test_file_paths_open_in_default_app(self):
        path = "/tmp/claude-1000/-home-lesley-Documents-Operum-operum-control/9698f267-0869-46f6-8145-414f74c154f8/scratchpad/contracts/p2d-a.pdf"
        for text in [path, "/123", "./123"]:
            with self.subTest(text=text), patch("actions.subprocess.Popen") as opener:
                self.invoke(text, ROFI_RETV="2")
                self.assertEqual(opener.call_args.args[0], ["xdg-open", destination(text)])
                self.assertTrue(opener.call_args.args[0][1].startswith("file:///"))
                self.assertNotIn("shell", opener.call_args.kwargs)

    def test_search_uses_duckduckgo(self):
        with patch("actions.subprocess.Popen") as opener:
            self.invoke("hello world", ROFI_RETV="2")
            self.assertEqual(opener.call_args.args[0], ["xdg-open", "https://duckduckgo.com/?q=hello+world"])

    def invoke(self, text, **env):
        output = io.StringIO()
        with patch("sys.argv", ["actions.py", text]), patch.dict(os.environ, env, clear=True), contextlib.redirect_stdout(output):
            main()
        return output.getvalue()

    def test_calculator_protocol_and_copy(self):
        with patch("actions.subprocess.Popen") as opener:
            result = self.invoke("= 12*7+3", ROFI_RETV="2")
            self.assertIn("87\0icon\x1faccessories-calculator\x1finfo\x1fcalc:87", result)
            self.assertIn("info\x1fcalc:20", self.invoke("200*10%", ROFI_RETV="2"))
            self.assertIn("info\x1fcalc:45", self.invoke("50-10%", ROFI_RETV="2"))
            self.assertIn("Cannot process input", self.invoke("= 1/0", ROFI_RETV="2"))
            opener.assert_not_called()
        with patch("actions.shutil.which", return_value="/usr/bin/xclip"), patch("actions.subprocess.run") as copy:
            self.assertEqual(self.invoke("87", ROFI_RETV="1", ROFI_INFO="calc:87"), "")
            self.assertEqual(copy.call_args.kwargs["input"], b"87")

    def test_url_open_does_not_use_a_shell(self):
        with patch("actions.subprocess.Popen") as opener:
            self.invoke("file:///tmp/a b", ROFI_RETV="2")
            self.assertEqual(opener.call_args.args[0], ["xdg-open", "file:///tmp/a%20b"])
            self.assertNotIn("shell", opener.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
