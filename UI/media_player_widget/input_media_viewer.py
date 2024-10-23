'''
Python script to define the Media Viewer using the QGraphicsView class where the media will be displayed.
The user can also zoom-in and zoom-out using the mouse scroll bar.
Mouse pointer can be used to selected the center of the 100x100 crop.
The Media Viewer also allows media selection via drag & drop.
'''
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QWheelEvent, QPainter, QMouseEvent, QPen, QColor, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt, QRect, QUrl
from utils.utils import resource_path


class InputMediaViewer(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.zoom_factor = 1.0
        self.main_window = parent

        # Set scroll bars to show only when necessary
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragEnterEvent):
        event.acceptProposedAction()
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            # Assuming the first URL for simplicity
            file_path = urls[0].toLocalFile()
            self.main_window.setSource(QUrl.fromLocalFile(resource_path(file_path)))
            
    def reset_to_default(self):
        self.main_window.current_item = None
        self.scene().clear()
        self.zoom_factor = 1.0
        self.resetTransform()
        self.resetCachedContent()
        self.zoom_factor = 1.0

        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.center_if_needed()

    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Determine the zoom change
        if event.angleDelta().y() > 0:
            zoom_change = zoom_in_factor
        else:
            zoom_change = zoom_out_factor

        # Store the position of the mouse before zooming
        old_pos = self.mapToScene(event.position().toPoint())
        
        # Apply the zoom
        self.zoom_factor *= zoom_change
        self.scale(zoom_change, zoom_change)

        # Adjust the view to focus on the mouse position
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Center the view when the window is resized
        #self.center_if_needed()
    def center_if_needed(self):
        if True: #self.horizontalScrollBar().isVisible() or self.verticalScrollBar().isVisible():
            self.centerOn(self.scene().sceneRect().center())
        
    def mousePressEvent(self, event: QMouseEvent):    
        scene_pos = self.mapToScene(event.pos())
        relative_pos = event.position().toPoint()
        self.main_window.update_crop_coordinates(scene_pos, relative_pos)        

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self._mouse_pos = event.pos()
        self.viewport().update() 
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        try: 
            if self._mouse_pos:# and self.image_item:
                painter = QPainter(self.viewport())
                red_pen = QPen(QColor(255, 0, 0))  # Red color for the square
                red_pen.setStyle(Qt.DotLine)  # Dotted line style
                red_pen.setWidth(2)  # Set the pen width for visibility
                painter.setPen(red_pen)
                # Calculate the top-left corner of the square in viewport coordinates
                top_left_x = self._mouse_pos.x() - 50
                top_left_y = self._mouse_pos.y() - 50
                # Draw a 100x100 square centered around the mouse in viewport coordinates
                painter.drawRect(QRect(top_left_x, top_left_y, 100, 100))      
        except:
            pass
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)

    def enterEvent(self, event):
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.viewport().setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

