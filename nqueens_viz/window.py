from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QLabel,
    QSlider,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer

from .algorithm import queens_steps
from .canvas import BoardCanvas
from .code_panel import CodePanel

STYLE = """
/* ── base ── */
QMainWindow, QWidget {
    background: #f5f6fa;
    color: #2c3e50;
    font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
    font-size: 13px;
}

/* ── buttons ── */
QPushButton {
    background: #ffffff;
    color: #2c3e50;
    border: 1px solid #ccd5e0;
    border-radius: 6px;
    padding: 7px 18px;
    font-size: 13px;
    min-width: 90px;
}
QPushButton:hover   { background: #e8edf5; border-color: #4a90d9; }
QPushButton:pressed { background: #d0d8e8; }
QPushButton:disabled{ background: #eef1f5; color: #a0aab5; border-color: #dde3ea; }
QPushButton#auto_btn {
    background: #1565c0;
    border-color: #1258a8;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#auto_btn:hover   { background: #1976d2; }
QPushButton#auto_btn:checked { background: #c62828; border-color: #b71c1c; }

/* ── spinbox ── */
QSpinBox {
    background: #ffffff;
    color: #2c3e50;
    border: 1px solid #ccd5e0;
    border-radius: 5px;
    padding: 5px 8px;
    font-size: 14px;
    min-width: 55px;
}
QSpinBox::up-button, QSpinBox::down-button {
    background: #e8edf5; border: none; width: 18px;
}

/* ── labels ── */
QLabel { font-size: 12px; color: #4a5568; }
QLabel#title_lbl {
    font-size: 20px; font-weight: bold; color: #d4a017; letter-spacing: 1px;
}
QLabel#stat_sol  { color: #2e7d32; font-weight: bold; font-size: 13px; }
QLabel#stat_step { color: #1565c0; font-size: 13px; }
QLabel#stat_info { color: #6a7a90; font-size: 12px; }
QLabel#panel_title {
    font-size: 13px; font-weight: bold; color: #1565c0;
    background: #e8f0fe; padding: 0 12px;
    border-bottom: 1px solid #ccd5e0;
}
QLabel#section_lbl {
    font-size: 11px; font-weight: bold; color: #6a7a90;
    background: #f0f4ff; padding: 0 12px;
    border-bottom: 1px solid #dde3ee;
}

/* ── slider ── */
QSlider::groove:horizontal { height: 4px; background: #d0d8e8; border-radius: 2px; }
QSlider::handle:horizontal {
    background: #1565c0; width: 14px; height: 14px;
    margin: -5px 0; border-radius: 7px;
}
QSlider::sub-page:horizontal { background: #42a5f5; border-radius: 2px; }

/* ── separators ── */
QFrame#sep { color: #d0d8e8; }

/* ── source code view ── */
QPlainTextEdit {
    background: #fafbff;
    border: none;
    selection-background-color: #d0e4ff;
}

/* ── variables table ── */
QTableWidget {
    background: #ffffff;
    border: none;
    gridline-color: #eef1f5;
    alternate-background-color: #f7f9ff;
}
QHeaderView::section {
    background: #f0f4ff;
    color: #1565c0;
    font-weight: bold;
    font-size: 11px;
    padding: 4px 8px;
    border: none;
    border-right: 1px solid #dde3ee;
    border-bottom: 1px solid #ccd5e0;
}
QTableWidget::item { padding: 2px 0; }

/* ── call stack ── */
QListWidget {
    background: #ffffff;
    border: none;
    outline: none;
}
QListWidget::item { padding: 3px 12px; }
QListWidget::item:hover { background: #f0f4ff; }

/* ── splitter handles ── */
QSplitter::handle:vertical {
    background: #e0e6f0;
    height: 2px;
    margin: 1px 0;
}
QSplitter::handle:horizontal {
    background: #e0e6f0;
    width: 2px;
    margin: 0 1px;
}

/* ── slim scrollbars ── */
QScrollBar:vertical {
    width: 7px; background: transparent; border: none; margin: 0;
}
QScrollBar::handle:vertical {
    background: #c0cad8; border-radius: 3px; min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal {
    height: 7px; background: transparent; border: none; margin: 0;
}
QScrollBar::handle:horizontal {
    background: #c0cad8; border-radius: 3px; min-width: 24px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N-Queens Solver  ·  Visualizer")
        self.setMinimumSize(1100, 740)
        self.setStyleSheet(STYLE)

        self.n = 8
        self.sol_count = 0
        self.step_count = 0
        self.gen = None
        self.finished = False
        self.running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._auto_tick)

        self._build_ui()
        self._reset()

    # ── UI construction ────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── left panel (board + controls) ─────────────────────────
        left = QWidget()
        vbox = QVBoxLayout(left)
        vbox.setSpacing(10)
        vbox.setContentsMargins(18, 14, 18, 14)

        # header row
        hdr = QHBoxLayout()
        lbl_title = QLabel("♛  N-Queens Solver")
        lbl_title.setObjectName("title_lbl")
        hdr.addWidget(lbl_title)
        hdr.addStretch()
        hdr.addWidget(QLabel("N ="))
        self.spin = QSpinBox()
        self.spin.setRange(1, 15)
        self.spin.setValue(8)
        self.spin.valueChanged.connect(self._on_n_changed)
        hdr.addWidget(self.spin)
        vbox.addLayout(hdr)

        # stats row
        stats = QHBoxLayout()
        self.lbl_sol = QLabel("Solutions: 0")
        self.lbl_step = QLabel("Steps: 0")
        self.lbl_info = QLabel("Ready")
        self.lbl_sol.setObjectName("stat_sol")
        self.lbl_step.setObjectName("stat_step")
        self.lbl_info.setObjectName("stat_info")
        for w in [self.lbl_sol, QLabel("·"), self.lbl_step, QLabel("·"), self.lbl_info]:
            stats.addWidget(w)
        stats.addStretch()
        vbox.addLayout(stats)

        # canvas
        self.canvas = BoardCanvas(self.n)
        vbox.addWidget(self.canvas, stretch=1)

        # separator
        sep = QFrame()
        sep.setObjectName("sep")
        sep.setFrameShape(QFrame.Shape.HLine)
        vbox.addWidget(sep)

        # control buttons
        btns = QHBoxLayout()
        btns.setSpacing(8)
        self.btn_reset = QPushButton("↺  Reset")
        self.btn_step = QPushButton("▶  Step")
        self.btn_auto = QPushButton("▶▶ Auto")
        self.btn_auto.setObjectName("auto_btn")
        self.btn_findall = QPushButton("⏭  Find All")

        self.btn_reset.clicked.connect(self._reset)
        self.btn_step.clicked.connect(self._do_step)
        self.btn_auto.clicked.connect(self._toggle_auto)
        self.btn_findall.clicked.connect(self._find_all)

        for b in [self.btn_reset, self.btn_step, self.btn_auto, self.btn_findall]:
            btns.addWidget(b)
        vbox.addLayout(btns)

        # speed row
        spd = QHBoxLayout()
        spd.addWidget(QLabel("Speed:"))
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 30)
        self.slider.setValue(8)
        self.slider.setFixedWidth(200)
        self.slider.valueChanged.connect(self._on_speed)
        spd.addWidget(self.slider)
        self.lbl_spd = QLabel("Normal")
        self.lbl_spd.setObjectName("stat_info")
        spd.addWidget(self.lbl_spd)
        spd.addStretch()
        vbox.addLayout(spd)

        outer.addWidget(left, stretch=1)

        # ── divider ───────────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setObjectName("sep")
        outer.addWidget(div)

        # ── right panel (algorithm trace) ─────────────────────────
        self.code_panel = CodePanel()
        outer.addWidget(self.code_panel)

    # ── slots ──────────────────────────────────────────────────────

    def _on_n_changed(self, val: int):
        self.n = val
        self._reset()

    def _reset(self):
        self.timer.stop()
        self.running = False
        self.btn_auto.setText("▶▶ Auto")
        self.sol_count = 0
        self.step_count = 0
        self.gen = queens_steps(self.n)
        self.finished = False
        self.canvas.set_n(self.n)
        self.code_panel.set_state(None)
        self._refresh_stats("idle", ())
        for b in [self.btn_step, self.btn_auto, self.btn_findall]:
            b.setEnabled(True)

    def _do_step(self) -> bool:
        if self.finished or self.gen is None:
            return False
        try:
            evt, board, state = next(self.gen)
            self.step_count += 1
            if evt == "solution":
                self.sol_count += 1
            self.canvas.update_board(evt, board, self.sol_count)
            self.code_panel.set_state(state)
            self._refresh_stats(evt, board)
            return True
        except StopIteration:
            self._on_done()
            return False

    def _auto_tick(self):
        if not self._do_step():
            self.timer.stop()
            self.running = False
            self.btn_auto.setText("▶▶ Auto")

    def _toggle_auto(self):
        if self.finished:
            return
        if self.running:
            self.timer.stop()
            self.running = False
            self.btn_auto.setText("▶▶ Auto")
        else:
            self.running = True
            self.btn_auto.setText("⏸  Pause")
            self.timer.start(self._interval())

    def _find_all(self):
        self.timer.stop()
        self.running = False
        self.btn_auto.setText("▶▶ Auto")
        if self.gen is None:
            return
        last_evt, last_board, last_state = "idle", (), None
        try:
            while True:
                evt, board, state = next(self.gen)
                self.step_count += 1
                if evt == "solution":
                    self.sol_count += 1
                    last_evt, last_board, last_state = evt, board, state
        except StopIteration:
            pass
        if last_board:
            self.canvas.update_board(last_evt, last_board, self.sol_count)
        self.code_panel.set_state(last_state)
        self._refresh_stats(last_evt, last_board)
        self._on_done()

    def _on_speed(self, val: int):
        label = (
            "Slow"
            if val <= 4
            else "Normal"
            if val <= 10
            else "Fast"
            if val <= 20
            else "Turbo"
        )
        self.lbl_spd.setText(label)
        if self.running:
            self.timer.setInterval(self._interval())

    def _interval(self) -> int:
        return max(16, int(800 / self.slider.value()))

    # ── helpers ────────────────────────────────────────────────────

    def _refresh_stats(self, evt: str, board: tuple[int, ...]):
        self.lbl_sol.setText(f"Solutions: {self.sol_count}")
        self.lbl_step.setText(f"Steps: {self.step_count}")
        msg = {
            "idle": "Ready",
            "place": f"Placing queen → row {len(board)}, col {board[-1] + 1 if board else '?'}",
            "solution": f"★ Solution #{self.sol_count} found!",
            "backtrack": f"↩ Backtracking to row {len(board) + 1}",
        }.get(evt, evt)
        self.lbl_info.setText(msg)

    def _on_done(self):
        self.finished = True
        for b in [self.btn_step, self.btn_auto, self.btn_findall]:
            b.setEnabled(False)
        self.lbl_info.setText(
            f"✓ Finished — {self.sol_count} solution(s), {self.step_count} steps"
        )
        self.btn_reset.setFocus()
