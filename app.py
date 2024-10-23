import sys
import UI.links_exit_button
import UI.media_buttons
import UI.media_player_widget
import UI.source_selector
from PySide6.QtWidgets import (
    QApplication, QMainWindow,
    QVBoxLayout, QWidget
)

from PySide6.QtCore import QTimer
import utils.globals
import onnxruntime as rt
from UI.media_player_widget.viewer_widget import MediaPlayerWidget
import utils
import UI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Setting up the default model and the default scale. Initialising the 4x model on tthe CPU.
        self.sr_model = 'realworldsr-diffirs2-ganx4-v2'
        self.current_sr_model_scale = '4x'
        self.provider = rt.get_available_providers()[-1]
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Super Resolution GUI")
        self.setWindowTitle("Layout")

        self.media_player_widget = MediaPlayerWidget(self)
        self.links_exit_button = UI.links_exit_button.LinksLayout(self)
        self.media_buttons = UI.media_buttons.MediaButtons(self)
        self.source_selector = UI.source_selector.SourceSelector(self)

        self.statusBar().showMessage("Video/Still Super-Resolution")  

        #Here we want to update the status every second lesss goooooo
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_status_bar)
        
        # Main layout for the window
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.source_selector)
        main_layout.addLayout(self.media_buttons)
        main_layout.addWidget(self.media_player_widget)
        main_layout.addLayout(self.links_exit_button)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.timer.start()
        self.media_player_widget.setSource(utils.globals.default_video_path, False)

    #Here We GoTTTa make changes man. Processing FPS
    def update_status_bar(self):
        if self.media_player_widget.isMediaVideo:
            self.statusBar().showMessage(f"Processing FPS : {self.media_player_widget.processed_frames_counter}")   
            self.media_player_widget.processed_frames_counter = 0
        else:
            self.statusBar().showMessage('')
        
    def closeEvent(self, event):
        import gc
        self.media_player_widget.closeEvent(event)
        gc.collect()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(utils.globals.app_style)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
