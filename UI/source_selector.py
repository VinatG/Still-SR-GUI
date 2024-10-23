from PySide6.QtWidgets import QComboBox
import cv2

class SourceSelector(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.detect_video_sources()
        self.currentIndexChanged.connect(self.change_video_source)

    def detect_video_sources(self):
        self.addItem("Select Media from Device")
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                cap.release()
                break
            self.addItem(f"Camera {index}")
            cap.release()
            index += 1

    def change_video_source(self):
        selected_index = self.currentIndex()
        self.parent.media_player_widget.change_video_source(selected_index)
