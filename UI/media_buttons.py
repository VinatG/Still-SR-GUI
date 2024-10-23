from PySide6.QtWidgets import QHBoxLayout, QPushButton
from PySide6.QtWidgets import (
    QPushButton, QFileDialog, 
    QHBoxLayout
)

from PySide6.QtCore import QUrl
class MediaButtons(QHBoxLayout):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.select_media_button = QPushButton("Select Video/Still", parent)
        self.select_media_button.setMaximumWidth(250)
        self.select_media_button.clicked.connect(self.select_media)

        self.save_media_button = QPushButton("Save Image/Video", parent)
        self.save_media_button.setMaximumWidth(250)

        self.save_media_button.setCheckable(True)
        self.save_media_button.toggled.connect(parent.media_player_widget.save_video)
        self.save_media_button.pressed.connect(parent.media_player_widget.save_image)

        self.addWidget(self.select_media_button)
        self.addWidget(self.save_media_button)

    def select_media(self):
        self.parent.media_player_widget.pause_video()
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self.parent, "Select Video/Still", "", "Videos (*.mp4 *.avi *.mov *.mkv);;Images (*.jpg *.jpeg *.png *.bmp);;All Files (*)", options = options)
        if file_name:
            self.parent.media_player_widget.view.reset_to_default()
            url = QUrl.fromLocalFile(file_name)
            self.parent.media_player_widget.setSource(url)

        elif self.parent.media_player_widget.is_Video_processing:
            self.parent.media_player_widget.play_video()

