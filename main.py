"""
N-Queens Solver Visualizer
依赖: pip install PySide6 matplotlib
运行: python main.py
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from nqueens_viz.window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#f5f6fa"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#2c3e50"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#e8edf5"))
    pal.setColor(QPalette.ColorRole.Text, QColor("#2c3e50"))
    pal.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor("#2c3e50"))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
