import re

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# 原始 queens(n) 源码 — block 编号对应 state["line"]
SOURCE_CODE = """\
def queens(n: int):
    limit = (1 << n) - 1

    def _solve(
        cols: int,
        diag_l: int,
        diag_r: int,
        board: tuple[int, ...],
    ):
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

    yield from _solve(0, 0, 0, ())"""

# QTextFormat::FullWidthSelection — 让高亮延伸到整行宽度
_FULL_WIDTH_SEL = QTextFormat.Property.FullWidthSelection

_KW_RE = re.compile(r"\b(yield\s+from|yield|def|return|while|if)\b")


def _mono_font() -> QFont:
    f = QFont()
    f.setFamilies(["JetBrains Mono", "Fira Code", "Consolas", "Monospace"])
    f.setPointSize(10)
    return f


def _bin(val: int, n: int) -> str:
    s = format(val, f"0{n}b")
    groups = [s[max(0, i - 4) : i] for i in range(len(s), 0, -4)][::-1]
    return " ".join(groups)


def _board_str(board: tuple) -> str:
    if not board:
        return "()"
    return "(" + ", ".join(str(c + 1) for c in board) + ")"


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("section_lbl")
    lbl.setFixedHeight(22)
    return lbl


class _PythonHL(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        self._fmt = QTextCharFormat()
        self._fmt.setForeground(QColor("#0057b8"))
        self._fmt.setFontWeight(700)

    def highlightBlock(self, text: str):
        for m in _KW_RE.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), self._fmt)


class CodePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(460)
        self.setMaximumWidth(600)

        mono = _mono_font()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        title = QLabel("  Algorithm Trace")
        title.setObjectName("panel_title")
        title.setFixedHeight(36)
        root.addWidget(title)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, stretch=1)

        # ── 源码面板 ───────────────────────────────────────────────────
        src_box = QWidget()
        sl = QVBoxLayout(src_box)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)
        sl.addWidget(_section_label("Source — queens(n)"))

        self._source = QPlainTextEdit(SOURCE_CODE)
        self._source.setReadOnly(True)
        self._source.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, False)
        self._source.setFont(mono)
        self._source.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._source.setCursorWidth(0)
        sl.addWidget(self._source)
        splitter.addWidget(src_box)

        self._hl = _PythonHL(self._source.document())

        # ── 变量面板 ───────────────────────────────────────────────────
        vars_box = QWidget()
        vl = QVBoxLayout(vars_box)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)
        vl.addWidget(_section_label("Variables"))

        self._vars = QTableWidget(0, 3)
        self._vars.setHorizontalHeaderLabels(["var", "value", "binary (n bits)"])
        self._vars.setAlternatingRowColors(True)
        hh = self._vars.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._vars.verticalHeader().setVisible(False)
        self._vars.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._vars.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._vars.setFont(mono)
        vl.addWidget(self._vars)
        splitter.addWidget(vars_box)

        # ── 调用栈面板 ─────────────────────────────────────────────────
        stack_box = QWidget()
        kl = QVBoxLayout(stack_box)
        kl.setContentsMargins(0, 0, 0, 0)
        kl.setSpacing(0)
        kl.addWidget(_section_label("Call Stack"))

        self._stack = QListWidget()
        self._stack.setFont(mono)
        self._stack.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        kl.addWidget(self._stack)
        splitter.addWidget(stack_box)

        splitter.setSizes([320, 180, 140])

        self.set_state(None)

    # ── 公开接口 ───────────────────────────────────────────────────────

    def set_state(self, state: dict | None):
        if state is None:
            self._source.setExtraSelections([])
            self._vars.setRowCount(0)
            self._stack.clear()
            return
        self._update_source(state["line"])
        self._update_vars(state)
        self._update_stack(state)

    # ── 私有方法 ───────────────────────────────────────────────────────

    def _update_source(self, line_no: int):
        block = self._source.document().findBlockByNumber(line_no)

        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(QColor("#fff8e1"))
        sel.format.setProperty(_FULL_WIDTH_SEL, True)
        sel.cursor = QTextCursor(block)
        self._source.setExtraSelections([sel])

        cur = QTextCursor(block)
        self._source.setTextCursor(cur)
        self._source.ensureCursorVisible()

    def _update_vars(self, s: dict):
        n = s["n"]
        depth = s["depth"]
        board = s["board"]
        has_avail = "available" in s

        rows: list[tuple[str, str, str]] = [
            ("board", _board_str(board), f"row {depth}"),
            ("depth", str(depth), ""),
            ("cols", str(s["cols"]), _bin(s["cols"], n)),
            ("diag_l", str(s["diag_l"]), _bin(s["diag_l"] & ((1 << n) - 1), n)),
            ("diag_r", str(s["diag_r"]), _bin(s["diag_r"] & ((1 << n) - 1), n)),
        ]
        if has_avail:
            col = s["bit"].bit_length() - 1
            rows += [
                ("available", str(s["available"]), _bin(s["available"], n)),
                (
                    "bit",
                    f"{s['bit']}  (col {col + 1}, {chr(65 + col)})",
                    _bin(s["bit"], n),
                ),
            ]

        BG_BOARD = QColor("#e8f5e9")
        FG_BOARD = QColor("#2e7d32")
        FG_VAR = QColor("#6a0dad")
        FG_BIN = QColor("#1565c0")

        self._vars.setRowCount(len(rows))
        for r, (name, val, binary) in enumerate(rows):
            ni, vi, bi = (QTableWidgetItem(x) for x in (name, val, binary))
            bi.setForeground(FG_BIN)
            if r == 0:
                for it in (ni, vi, bi):
                    it.setBackground(BG_BOARD)
                ni.setForeground(FG_BOARD)
                vi.setForeground(FG_BOARD)
            else:
                ni.setForeground(FG_VAR)
            self._vars.setItem(r, 0, ni)
            self._vars.setItem(r, 1, vi)
            self._vars.setItem(r, 2, bi)

    def _update_stack(self, s: dict):
        depth = s["depth"]
        board = s["board"]

        self._stack.clear()
        for d in range(depth + 1):
            item = QListWidgetItem(f"#{d}  _solve({_board_str(board[:d])}…)")
            if d == depth:
                item.setBackground(QColor("#e8f0fe"))
                item.setForeground(QColor("#1565c0"))
                font = self._stack.font()
                font.setBold(True)
                item.setFont(font)
            self._stack.addItem(item)
        self._stack.scrollToBottom()
