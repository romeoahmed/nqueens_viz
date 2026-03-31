def queens_steps(n: int):
    """
    基于 bit-mask 的逐步生成器。每次 yield (event, board, state):
      'place'     – 递归进入下一行（yield from _solve）
      'solution'  – 找到完整解（yield board）
      'backtrack' – 从递归返回，准备尝试下一个 bit
    state 包含当前帧的变量快照，供侧边面板使用。
    """
    limit = (1 << n) - 1

    def _solve(cols: int, diag_l: int, diag_r: int, board: tuple[int, ...], depth: int):
        if cols == limit:
            yield (
                "solution",
                board,
                {
                    "line": 10,
                    "depth": depth,
                    "n": n,
                    "cols": cols,
                    "diag_l": diag_l,
                    "diag_r": diag_r,
                    "board": board,
                },
            )
            return
        available = limit & ~(cols | diag_l | diag_r)
        while available:
            bit = available & -available
            available ^= bit
            nb = board + (bit.bit_length() - 1,)
            yield (
                "place",
                nb,
                {
                    "line": 19,
                    "depth": depth,
                    "n": n,
                    "cols": cols,
                    "diag_l": diag_l,
                    "diag_r": diag_r,
                    "available": available,
                    "bit": bit,
                    "board": nb,
                },
            )
            yield from _solve(
                cols | bit, (diag_l | bit) << 1, (diag_r | bit) >> 1, nb, depth + 1
            )
            yield (
                "backtrack",
                board,
                {
                    "line": 17,
                    "depth": depth,
                    "n": n,
                    "cols": cols,
                    "diag_l": diag_l,
                    "diag_r": diag_r,
                    "available": available,
                    "bit": bit,
                    "board": board,
                },
            )

    yield from _solve(0, 0, 0, (), 0)


def attacked_squares(board: tuple[int, ...], n: int) -> set[tuple[int, int]]:
    """返回当前所有皇后可以攻击到的格子集合（行、列、对角线）。"""
    attacked: set[tuple[int, int]] = set()
    for r, c in enumerate(board):
        attacked.update((r, i) for i in range(n))  # 行
        attacked.update((i, c) for i in range(n))  # 列
        attacked.update(  # 四条对角线
            (r + d * dr, c + d * dc)
            for d in range(1, n)
            for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1))
            if 0 <= r + d * dr < n and 0 <= c + d * dc < n
        )
    return attacked
