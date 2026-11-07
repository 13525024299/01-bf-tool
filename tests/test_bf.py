"""针对解释器的单元测试：python -m unittest discover -s tests -v"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from bf import Brainfuck, tokenize, build_jump_table, run_source  # noqa: E402


class TestInterpreter(unittest.TestCase):
    def test_tokenize_ignores_comments(self):
        self.assertEqual(tokenize("++ 注释\n--"), ["+", "+", "-", "-"])

    def test_plus_minus_wrap_8bit(self):
        # 255 加 1 回到 0，0 减 1 变成 255
        self.assertEqual(run_source("+" * 255 + "."), "\xff")
        self.assertEqual(run_source("+-."), "\x00")

    def test_output_ascii(self):
        # 72 个 '+' 得到 'H'，再 '+' 得到 'I'，中间各输出一次
        prog = "+" * 72 + ".+" + "."
        self.assertEqual(run_source(prog), "HI")

    def test_input_and_copy(self):
        # 读两个字符，把第一个搬到第二个单元，输出两者之和（65+66=131）
        self.assertEqual(run_source(",>,<[->+<]>.", "AB"), chr(131))

    def test_loop_counts(self):
        # 9 次循环，每次给第 2 个单元加 5 -> 45 即 '-'
        self.assertEqual(run_source("+++++++++[>+++++<-]>."), "-")

    def test_unbalanced_bracket(self):
        with self.assertRaises(SyntaxError):
            build_jump_table(tokenize("[+"))

    def test_pointer_underflow(self):
        with self.assertRaises(IndexError):
            run_source("<.")

    def test_page_programs(self):
        self.assertEqual(run_source(",[>+<-]>-.", "A"), "@")
        self.assertEqual(run_source("++++++++++[>++++++++>++++++++<<-]>-.>.", ""), "OP")
        self.assertEqual(run_source(",>,<[->+<]>.", "!!"), "B")


if __name__ == "__main__":
    unittest.main()
