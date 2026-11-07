"""《奇怪的书》三页任务的机器验证脚本。

运行： python answers.py
它会用 bf.py 里的解释器把三页程序真正跑一遍，把结果打印出来，
避免纸上推演出错。
"""

from bf import run_source

# ---- 第一页：题目给的程序 ----
PAGE1 = ",[>+<-]>-."

# ---- 第二页：题目给的程序 ----
PAGE2 = """
++++++++++
[
>++++++++
>++++++++
<<-
]
>-.
>.
"""

# ---- 第三页：自己写的程序，要求读两个字符，输出两者 ASCII 之和 ----
# 步骤：读 a 到 0 号单元 -> 读 b 到 1 号单元 -> 回到 0 号 -> 把 0 号搬到 1 号
#       -> 右移到 1 号 -> 输出
PAGE3 = ",>,<[->+<]>."


def show(label, code, stdin="", expect=None):
    got = run_source(code, stdin)
    codes = ", ".join(str(ord(c)) for c in got)
    print(f"[{label}] 输入={stdin!r} -> 输出={got!r}  ASCII=({codes})")
    if expect is not None and got != expect:
        raise AssertionError(f"{label} 预期 {expect!r}，实际 {got!r}")
    return got


def main():
    # 第一页：输出 = 输入 ASCII 减 1
    for ch in ["A", "B", "a"]:
        show("第一页", PAGE1, ch, chr(ord(ch) - 1))

    # 第二页：固定输出 OP
    show("第二页", PAGE2, "", "OP")

    # 第三页：'H'(72) + 'e'(101) = 173，落在扩展 ASCII 之外（>127），
    # 这里用几个和不超过 127 的组合演示，另附 255 溢出的例子。
    show("第三页", PAGE3, "AB", chr(65 + 66))   # 131 -> 0x83，非打印
    show("第三页", PAGE3, " !", chr(32 + 33))   # 33+34=65 -> 'A'
    show("第三页", PAGE3, "!!", chr(33 + 33))   # 'B'
    show("第三页", PAGE3, "\x7f\x01", chr(128))  # 127+1=128，超出 ASCII 打印范围

    # 演示 255 溢出：200+100=300 -> 300 & 0xFF = 44 即 ','
    got = run_source(PAGE3, "\xc8d")  # 200, 100
    print(f"[第三页] 溢出演示 200+100=300 -> {ord(got)}(0x{ord(got):02x})")


if __name__ == "__main__":
    main()
