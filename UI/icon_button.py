import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

class SVGButton(QPushButton):
    def __init__(self, svg_path, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(svg_path))
        self.setIconSize(QSize(32, 32))  # Set the icon size as needed
        self.setFlat(True)  # Make the button flat (no borders)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.2);  /* Semi-transparent black on hover */
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.4);  /* Even darker color when pressed */
            }
            """
        )

class SVGButtonExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("SVG Button Example")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        button_container = QHBoxLayout()

        svg_button = SVGButton("save.svg")  # Replace with the path to your SVG icon
        button_container.addStretch(1)  # Add spacing before the button
        button_container.addWidget(svg_button)
        button_container.addStretch(1)  # Add spacing after the button

        layout.addLayout(button_container)

def main():
    app = QApplication(sys.argv)
    window = SVGButtonExample()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
