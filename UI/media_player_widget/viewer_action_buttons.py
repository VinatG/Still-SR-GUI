from PySide6.QtWidgets import (
    QPushButton, QHBoxLayout, QCheckBox
)
from UI.media_player_widget.post_processing_drop_down import PostProcessingDropdown
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

        self.post_processing_drop_down = PostProcessingDropdown()#self)
        self.post_processing_drop_down.valueChanged.connect(self.set_post_processing_algorithm)

        self.default_media_toggle_button = ToggleSwitchWidget()
        self.default_media_toggle_button.toggle_slider.positionChanged.connect(self.on_slider_changed)

        self.addWidget(self.ocr_checkbox)
        self.addStretch(3)
        self.addWidget(self.play_button)
        self.addWidget(self.pause_button)
        self.addStretch(3)
        self.addWidget(self.post_processing_drop_down)
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
    
    def set_post_processing_algorithm(self, alg : str):
        self.parent.post_processing_algorithm = alg
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