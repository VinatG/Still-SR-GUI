from PySide6.QtCore import Qt
from utils import globals
from PySide6.QtWidgets import QPushButton,  QLabel, QHBoxLayout

class LinksLayout(QHBoxLayout):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        # Defining the QLabels to store the links to the SR model's paper and GitHub
        self.github_link = QLabel(globals.diffir_github_link)
        self.github_link.setOpenExternalLinks(True)
        self.paper_link = QLabel(globals.diffir_paper_link)
        self.paper_link.setOpenExternalLinks(True)
        
        # Defining the exit button that will call the close function of the parent class when presed
        self.exit_button = QPushButton("EXIT")
        self.exit_button.setStyleSheet("QPushButton { background-color: #FF0000; color: white; font-weight: bold; }")
        self.exit_button.setMinimumWidth(150)
        self.exit_button.clicked.connect(self.parent.close)
        self.exit_button.setCursor(Qt.PointingHandCursor)

        # Combining the GitHub links and the exit button into one horizontal box layout
        self.addWidget(self.github_link)
        self.addStretch(1) 
        self.addWidget(self.paper_link)
        self.addStretch(23) 
        self.addWidget(self.exit_button)
        self.addStretch(1) 

