'''
Python script to define the drop-down for all the post-processing algorithms
'''
from PySide6.QtWidgets import QComboBox
from utils.globals import POST_PROCESSING_OPTIONS
from PySide6.QtCore import Signal

class PostProcessingDropdown(QComboBox):
    valueChanged = Signal(str) 
    def __init__(self, parent = None):
        super().__init__(parent)

        self.parent = parent
        self.addItems(POST_PROCESSING_OPTIONS.keys())
        self.currentTextChanged.connect(self.valueChanged.emit)
