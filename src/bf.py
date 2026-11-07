"""Brainfuck 解释器（对应《奇怪的书》一题）。

设计要点：
1. 只把 8 个关键字当作指令，其余字符（空格、换行、注释）全部忽略，
   这样题目里那种一行一个符号的排版也能直接跑。
2. 每个单元是 0~255 的无符号字节，加过头回到 0，减过头回到 255（题目规定的溢出行为）。
3. 纸带按需向右扩展，指针不允许走到负数下标。
4. '[' 和 ']' 的跳转位置在运行前先用栈配对好，循环体不必每次重新扫描，
   复杂度从 O(n^2) 降到 O(n)。
"""

# 8 个关键字，与题目表格一致
KEYWORDS = "+-<>[].,"


def load(path):
    """从文件读入程序源码。"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def tokenize(source):
    """过滤掉注释，只留下 8 个关键字。"""
    return [ch for ch in source if ch in KEYWORDS]


def build_jump_table(code):
    """把每个 '[' 与它配对的 ']' 的下标互相记下来。

    返回 dict：{位置: 配对位置}
    """
    jump = {}
    stack = []
    for i, ch in enumerate(code):
        if ch == "[":
            stack.append(i)
        elif ch == "]":
            if not stack:
                raise SyntaxError(f"第 {i} 个字符处出现了多余的 ']'")
            left = stack.pop()
            jump[left] = i
            jump[i] = left
    if stack:
        raise SyntaxError(f"第 {stack[-1]} 个字符处的 '[' 没有闭合")
    return jump


class Brainfuck:
    """一个小而完整的 Brainfuck 虚拟机。"""

    def __init__(self, source, taillen=30000):
        self.code = tokenize(source)
        self.jump = build_jump_table(self.code)
        self.tape = [0] * taillen
        self.ptr = 0

    def _grow(self):
        """指针越界时向右扩容，避免崩溃。"""
        if self.ptr >= len(self.tape):
            self.tape.extend([0] * max(len(self.tape), 1024))

    def run(self, inputs=""):
        """执行程序。

        inputs: 供 ',' 读取的字符串（模拟键盘输入），读完视为 EOF（补 0）。
        返回程序用 '.' 输出的字符串。
        """
        out = []
        pc = 0
        feed = list(inputs)
        code, tape, jump = self.code, self.tape, self.jump
        while pc < len(code):
            op = code[pc]
            if op == "+":
                self._grow()
                tape[self.ptr] = (tape[self.ptr] + 1) & 0xFF
            elif op == "-":
                self._grow()
                tape[self.ptr] = (tape[self.ptr] - 1) & 0xFF
            elif op == ">":
                self.ptr += 1
                self._grow()
            elif op == "<":
                if self.ptr == 0:
                    raise IndexError("指针已经停在最左边的单元，不能再左移")
                self.ptr -= 1
            elif op == ".":
                out.append(chr(tape[self.ptr]))
            elif op == ",":
                tape[self.ptr] = ord(feed.pop(0)) if feed else 0
            elif op == "[":
                if tape[self.ptr] == 0:
                    pc = jump[pc]
            elif op == "]":
                if tape[self.ptr] != 0:
                    pc = jump[pc]
            pc += 1
        return "".join(out)


def run_source(source, inputs=""):
    """一次性执行一段源码，便于在脚本和测试里调用。"""
    return Brainfuck(source).run(inputs)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python bf.py 程序文件.bf [要喂给逗号的输入]")
        raise SystemExit(1)
    src = load(sys.argv[1])
    stdin = sys.argv[2] if len(sys.argv) > 2 else ""
    print(run_source(src, stdin), end="")
