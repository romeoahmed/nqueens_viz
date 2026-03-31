import matplotlib

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe

from .algorithm import attacked_squares
from .palette import (
    BG,
    CELL_L,
    CELL_D,
    ATK_L,
    ATK_D,
    QUEEN_OK,
    QUEEN_BT,
    QUEEN_SOL,
    GRID_COL,
    QUEEN_CELL_SOL,
    QUEEN_CELL_BT,
    QUEEN_CELL_PLACE,
)


class BoardCanvas(FigureCanvas):
    def __init__(self, n: int = 8):
        self.fig = Figure(facecolor=BG)
        super().__init__(self.fig)
        self.setMinimumSize(420, 420)
        self.n = n
        self.board: tuple[int, ...] = ()
        self.event_type = "idle"
        self.sol_count = 0
        self._init_ax()

    def _init_ax(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(BG)
        self.fig.subplots_adjust(left=0.06, right=0.98, top=0.93, bottom=0.06)

    def set_n(self, n: int):
        self.n = n
        self.board = ()
        self.event_type = "idle"
        self.sol_count = 0
        self._init_ax()
        self.redraw()

    def update_board(self, event_type: str, board: tuple[int, ...], sol_count: int):
        self.event_type = event_type
        self.board = board
        self.sol_count = sol_count
        self.redraw()

    def redraw(self):
        ax = self.ax
        ax.clear()
        ax.set_facecolor(BG)
        n = self.n
        board = self.board
        evt = self.event_type

        queen_cells = set(enumerate(board))
        atk = attacked_squares(board, n) if board else set()

        # 按事件类型预计算颜色，避免在循环内重复判断
        _cell_fc = {"solution": QUEEN_CELL_SOL, "backtrack": QUEEN_CELL_BT}
        _qc = {"solution": QUEEN_SOL, "backtrack": QUEEN_BT}
        queen_cell_fc = _cell_fc.get(evt, QUEEN_CELL_PLACE)
        queen_edge_c = _qc.get(evt, QUEEN_OK)
        queen_color = _qc.get(evt, QUEEN_OK)
        fs = max(10, int(32 - n * 1.6))

        # ── cells + queens（单次遍历）─────────────────────────────
        for r in range(n):
            for c in range(n):
                is_queen = (r, c) in queen_cells
                if is_queen:
                    rect = mpatches.FancyBboxPatch(
                        (c + 0.05, n - 1 - r + 0.05),
                        0.9,
                        0.9,
                        boxstyle="round,pad=0.02",
                        facecolor=queen_cell_fc,
                        edgecolor=queen_edge_c,
                        linewidth=1.8,
                        zorder=3,
                    )
                    ax.add_patch(rect)
                    txt = ax.text(
                        c + 0.5,
                        n - 1 - r + 0.5,
                        "♛",
                        ha="center",
                        va="center",
                        fontsize=fs,
                        color=queen_color,
                        fontweight="bold",
                        zorder=5,
                    )
                    txt.set_path_effects(
                        [pe.withStroke(linewidth=2, foreground="white")]
                    )
                else:
                    light = (r + c) % 2 == 0
                    is_atk = (r, c) in atk
                    fc = (
                        (ATK_L if light else ATK_D)
                        if is_atk
                        else (CELL_L if light else CELL_D)
                    )
                    rect = mpatches.Rectangle(
                        (c, n - 1 - r),
                        1,
                        1,
                        facecolor=fc,
                        edgecolor=GRID_COL,
                        linewidth=0.8,
                        zorder=1,
                    )
                    ax.add_patch(rect)

        # ── solution：整板高亮边框 ────────────────────────────────
        if evt == "solution":
            border = mpatches.FancyBboxPatch(
                (-0.08, -0.08),
                n + 0.16,
                n + 0.16,
                boxstyle="round,pad=0.0",
                fill=False,
                edgecolor=QUEEN_SOL,
                linewidth=3.5,
                zorder=6,
            )
            ax.add_patch(border)

        # ── axis labels ───────────────────────────────────────────
        for i in range(n):
            ax.text(
                -0.35,
                n - 1 - i + 0.5,
                str(i + 1),
                ha="center",
                va="center",
                fontsize=8,
                color="#6a7a90",
                zorder=2,
            )
            ax.text(
                i + 0.5,
                -0.35,
                chr(65 + i),
                ha="center",
                va="center",
                fontsize=8,
                color="#6a7a90",
                zorder=2,
            )

        # ── title ─────────────────────────────────────────────────
        if evt == "solution":
            title = f"✓  Solution #{self.sol_count}  —  All {n} queens placed safely"
            tc = QUEEN_SOL
        elif not board:
            title = "Ready  ·  press  ▶ Step  or  ⚡ Auto"
            tc = "#7a8a9a"
        elif evt == "backtrack":
            title = f"↩  Backtracking  ·  {len(board)} queen(s) remain"
            tc = QUEEN_BT
        else:
            title = f"✓  Valid  ·  {len(board)}/{n} queens placed"
            tc = "#1976d2"

        ax.set_title(title, color=tc, fontsize=10, fontweight="bold", pad=6, loc="left")

        ax.set_xlim(-0.55, n + 0.1)
        ax.set_ylim(-0.55, n + 0.1)
        ax.set_aspect("equal")
        ax.axis("off")
        self.fig.patch.set_facecolor(BG)
        self.draw_idle()
