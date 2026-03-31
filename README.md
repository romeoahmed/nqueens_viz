# ♛ N-Queens Visualizer

基于 bitmask 回溯算法的 N 皇后求解可视化工具，带有 Python Tutor 风格的实时算法追踪面板。

## 功能

- **交互式棋盘** — matplotlib 渲染，实时显示皇后放置、攻击范围与回溯过程
- **算法追踪面板** — 右侧显示 `queens(n)` 源码，高亮当前执行行、变量快照（二进制位表示）和调用栈
- **逐步 / 自动 / 全量** 三种运行模式，速度可调
- 支持 N = 1–15

## 依赖

- Python ≥ 3.14
- PySide6 ≥ 6.11
- matplotlib ≥ 3.10

## 安装与运行

```bash
# 克隆
git clone <repo-url> && cd nqueens_viz

# 使用 uv（推荐）
uv sync
uv run python main.py

# 或手动
python -m venv .venv && source .venv/bin/activate
pip install .
python main.py
```

## 项目结构

```
main.py                  # 入口，创建 QApplication
nqueens_viz/
├── algorithm.py         # bitmask 回溯生成器 queens_steps()
├── canvas.py            # matplotlib 棋盘画布
├── code_panel.py        # 算法追踪面板（源码 / 变量 / 调用栈）
├── palette.py           # 颜色常量
└── window.py            # 主窗口布局与控制逻辑
```

## 算法

核心为 bitmask 回溯法，用三个整数 `cols`、`diag_l`、`diag_r` 分别表示列占用、左对角线占用和右对角线占用，通过位运算在 O(1) 内计算可用位置：

```python
def queens(n: int):
    limit = (1 << n) - 1
    def _solve(cols, diag_l, diag_r, board):
        if cols == limit:
            yield board
            return
        available = limit & ~(cols | diag_l | diag_r)
        while available:
            bit = available & -available
            available ^= bit
            yield from _solve(
                cols | bit,
                (diag_l | bit) << 1,
                (diag_r | bit) >> 1,
                board + (bit.bit_length() - 1,),
            )
    yield from _solve(0, 0, 0, ())
```

## License

[MIT](LICENSE)
