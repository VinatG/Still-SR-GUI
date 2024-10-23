from PySide6.QtWidgets import (
    QGraphicsScene, QVBoxLayout, QWidget, QPushButton, QFileDialog, QGraphicsPixmapItem,
    QLabel, QHBoxLayout, QCheckBox
)
from UI.media_player_widget.toggle_switch import ToggleSwitchWidget
from UI import icon_button
from utils import globals

class ViewerButtons(QHBoxLayout):
    def __init__(self, parent):
        super().__init__()#parent)

        self.parent = parent

        self.ocr_checkbox = QCheckBox("Perform OCR")
        self.ocr_checkbox.stateChanged.connect(self.check_ocr_state)

        self.play_button = icon_button.SVGButton('icons/play.png')
        self.pause_button = icon_button.SVGButton('icons/pause.png')
        self.play_button.clicked.connect(self.parent.play_video) 
        self.pause_button.clicked.connect(self.parent.pause_video) 

        self.pre_processing_button = QPushButton("Pre-process")
        self.pre_processing_button.setCheckable(True)
        self.pre_processing_button.setStyleSheet(globals.pre_processing_button_style)
        self.pre_processing_button.setMinimumWidth(250)
        self.pre_processing_button.toggled.connect(self.pre_processing_button_toggle)

        self.default_media_toggle_button = ToggleSwitchWidget()
        self.default_media_toggle_button.toggle_slider.positionChanged.connect(self.on_slider_changed)

        self.addWidget(self.ocr_checkbox)
        self.addStretch(3)
        self.addWidget(self.play_button)
        self.addWidget(self.pause_button)
        self.addStretch(3)
        self.addWidget(self.pre_processing_button)
        self.addStretch(2)
        self.addWidget(self.default_media_toggle_button)
        self.addStretch(2)

    def check_ocr_state(self, state):
        if state == 2:  # 2 means checked
            self.parent.do_ocr = True
        else:
            self.parent.do_ocr = False

        if self.parent.isMediaImage:
            self.parent.set_crop()
            self.parent.run_still_execution()
    


    

    def pre_processing_button_toggle(self, state : bool):
        self.parent.do_pre_processing = state
        if state:
            self.pre_processing_button.setText("No Pre-processing")
        else:
            self.pre_processing_button.setText("Pre-processing")
        
        if self.parent.isMediaImage:
            self.parent.set_crop()
            self.parent.run_still_execution()
    
        
    def on_slider_changed(self, pos):
        if pos == 0:
            self.parent.setSource(globals.default_video_path)
        elif pos == 0.5:
            self.parent.pause_video()
        else:
            self.parent.setSource(globals.default_image_path)