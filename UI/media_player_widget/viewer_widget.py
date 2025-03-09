import cv2
from PySide6.QtWidgets import (
    QGraphicsScene, QVBoxLayout, QWidget, QFileDialog, QGraphicsPixmapItem,
    QLabel, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt, QThread, QUrl
from PySide6.QtCore import QRect, QPoint
import numpy as np

from UI.media_player_widget.input_media_viewer import InputMediaViewer
from utils import utils, worker_classes, model_processors
from UI.media_player_widget.viewer_action_buttons import ViewerButtons
from utils.image_processing import apply_post_processing
import copy

class MediaPlayerWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMaximumHeight(540)
        self.parent = parent

        self.ocr_processor = model_processors.OCRProcessor()
        self.sr_processor = model_processors.SRProcessor()
        
        self.crop_center_x, self.crop_center_y = None, None
        self.video_w, self.video_h = None, None
        self.current_video_pixmap = None
        self.processed_frames_counter = 0
        self.post_processing_algorithm = 'No Post-Processing'
        self.video_recording_images_list = []
        self.isRecordingOn = False
        self.isMediaVideo = False
        self.isMediaImage = False
        self.sr_result = None
        self.do_ocr = False
        
        self.currentProcessedDisplayImage = np.empty((0, 0, 0), dtype = np.uint8)
        self.current_pixellated_image = np.empty((0, 0, 0), dtype = np.uint8)
        self.currentProcessedCroppedImage = np.empty((0, 0, 0), dtype = np.uint8)
        self.current_cropped_image = np.empty((0, 0, 0), dtype = np.uint8)
        
        # Initialize the images
        self.scene = QGraphicsScene(self)

        self.view = InputMediaViewer(self.scene, self)
        self.image_crop_label = QLabel(self)
        self.pixellated_crop_label = QLabel(self)
        self.output_pixmap_label = QLabel(self)
        self.load_images() 
        
        self.video_thread = QThread()
        self.video_worker = worker_classes.SR_Video_Worker(self.run_video_execution)
        self.video_worker.moveToThread(self.video_thread)
        self.video_thread.started.connect(self.video_worker.run)
        self.video_worker.finished.connect(self.video_thread.quit)
        
        self.video_worker.progress.connect(self.set_output_label)
        
        self.cap = None
        self.current_item = None  # To store the current frame item
        self.current_frame = None  # To store the current frame as an image        

        # Handle window resize
        self.resizeEvent(None)
        viewer_layout = QHBoxLayout()
        viewer_layout.addWidget(self.view)
        viewer_layout.addWidget(self.image_crop_label)
        viewer_layout.addWidget(self.pixellated_crop_label)
        viewer_layout.addWidget(self.output_pixmap_label)

        viewer_layout.setStretch(0, 48)  # self.view occupies 1 unit (half of the width)
        viewer_layout.setStretch(1, 5)  # self.image_crop_label, self.pixellated_crop_label, and self.output_pixmap_label share the other half
        viewer_layout.setStretch(2, 20)
        viewer_layout.setStretch(3, 20)

        self.buttons_layout = ViewerButtons(self)
        main_layout = QVBoxLayout()
        main_layout.addLayout(viewer_layout)
        main_layout.addLayout(self.buttons_layout)
        self.setLayout(main_layout)
              
    def run_video_execution(self, progress_callback):
        while self.isMediaVideo: 

            if self.current_cropped_image.shape == (0, 0, 0):
                continue
            out_mat = self.sr_processor.perform_sr(self.current_cropped_image) 

            out_mat = np.ascontiguousarray(out_mat, dtype = np.uint8)
            if self.isRecordingOn:
                processed_views = utils.process_views(self.currentProcessedDisplayImage, self.currentProcessedCroppedImage, self.current_pixellated_image, out_mat)
                self.video_recording_images_list.append(processed_views)
            progress_callback.emit(out_mat)
            self.processed_frames_counter += 1 
            
    def set_output_label(self, out_mat):
        if self.do_ocr:
            out_mat = self.ocr_processor.perform_ocr(out_mat) 

        
        out_mat = apply_post_processing(out_mat, self.post_processing_algorithm)#perform_post_processing(out_mat)
        self.sr_result = out_mat
        height, width, _ = out_mat.shape
        bytes_per_line = 3 * width
        self.output_pixmap = QPixmap.fromImage(QImage(out_mat.data, width, height, bytes_per_line, QImage.Format_RGB888))
        self.output_pixmap_label.setPixmap(self.output_pixmap)

        if self.isMediaVideo:
            self.next_frame()

    def play_video(self):
        if self.cap and self.cap.isOpened():
            self.isMediaImage = False 
            self.isMediaVideo = True
            self.video_thread.start()

    def pause_video(self):
        self.isMediaImage = True 
        self.isMediaVideo = False
        
    def load_video(self, url):
        self.cap = cv2.VideoCapture(url)
        self.video_w, self.video_h = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.crop_center_x, self.crop_center_y = int(self.view.viewport().rect().size().width() / 2), int(self.view.viewport().rect().size().height() / 2)       
        self.next_frame()
        self.video_thread.start()

    def setSource(self, url: QUrl, make_change = True):
        if self.do_ocr:
            self.buttons_layout.ocr_checkbox.setChecked(False)
        self.crop_center_x, self.crop_center_y = -1, -1
        self.pause_video()
        self.view.reset_to_default()
        
        if make_change:
            self.buttons_layout.default_media_toggle_button.toggle_slider.setPosition(0.5)
        if QUrl.fileName(url).rsplit('.', 1)[1] in ['bmp', 'jpg', 'jpeg', 'png']:
            self.isMediaImage, self.isMediaVideo = True, False
            self.parent.media_buttons.save_media_button.setText("Save Image")
            self.parent.media_buttons.save_media_button.setCheckable(False)
            self.load_image(url.toLocalFile()) 
            
        else :
            self.isMediaImage, self.isMediaVideo = False, True
            self.parent.media_buttons.save_media_button.setText("Start Recording")
            self.parent.media_buttons.save_media_button.setCheckable(True)
            self.parent.media_buttons.save_media_button.setChecked(False)
            self.load_video(url.toLocalFile())  

    def load_image(self, url):
        frame_rgb = cv2.imread(url)
        frame_rgb = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        self.video_w, self.video_h = w, h
        bytes_per_line = ch * w
        
        q_img = QImage(frame_rgb, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.current_video_pixmap = pixmap
        if self.current_item:
            # Update the existing item to preserve the transformation
            self.current_item.setPixmap(pixmap)
        else:
            # First frame setup
            self.current_item = QGraphicsPixmapItem(pixmap)
            self.view.scene().addItem(self.current_item)

        # Adjust scene size based on the image size
        self.view.scene().setSceneRect(self.current_item.boundingRect())
        self.crop_center_x, self.crop_center_y = int(self.view.viewport().rect().size().width() / 2), int(self.view.viewport().rect().size().height() / 2)
        self.view.center_if_needed()
        self.set_crop()
        self.run_still_execution()
    
    def save_video(self, checked):
        if checked:
            self.isRecordingOn = True
            self.parent.media_buttons.save_media_button.setText("Stop Recording")

        elif len(self.video_recording_images_list) > 0:
            self.pause_video()
            save_video_path, _ = QFileDialog.getSaveFileName(self, "Save Video", '', "Video (*.mp4")
            if len(save_video_path) > 0:
                self.parent.media_buttons.save_media_button.setText("Start Recording")
                utils.frames_to_video(save_video_path, self.video_recording_images_list)
                self.video_recording_images_list = []
                self.isRecordingOn = False
            else:
                self.parent.media_buttons.save_media_button.setChecked(True)
            self.play_video()

    def save_image(self): 
        if self.isMediaImage:
            processed_views = utils.process_views(self.currentProcessedDisplayImage, self.currentProcessedCroppedImage, self.current_pixellated_image, self.sr_result)
            save_image_path, _ = QFileDialog.getSaveFileName(self, "Save Image", '', "Image (*.png *.jpg *.bmp *.jpeg);;All Files (*)") 
            cv2.imwrite(save_image_path, processed_views)

    def update_crop_coordinates(self, scene_pos, relative_pos):
        self.crop_center_x, self.crop_center_y = int(relative_pos.x()), int(relative_pos.y())
        if self.isMediaImage:
            self.set_crop()
            self.run_still_execution()

    def resizeEvent(self, event):
        # Get the current size of the window
        window_width = self.parent.width()
        window_height = self.parent.height()

        # Calculate scale factors based on 1920x1080 reference size
        scale_width = window_width / 1920.0
        scale_height = window_height / 1080.0
        window_width = self.width()
        window_height = self.height()
        # Calculate positions and sizes
        spacing = int(12 * scale_width)
        image_1_width = int(960 * scale_width)
        image_1_height = int(540 * scale_height)
        image_crop_size = int(100 * scale_width)
        pixellated_crop_size = int(400 * scale_width)
        output_crop_size = int(400 * scale_width)

        # Calculate total width and height for centering
        total_width = image_1_width + image_crop_size + pixellated_crop_size + output_crop_size + 3 * spacing
        max_height = max(image_1_height, image_crop_size, pixellated_crop_size, output_crop_size)
        start_x = (window_width - total_width) // 2
        center_y = (window_height - max_height) // 2

        # Position and resize the images
        self.view.setGeometry(start_x, center_y + (max_height - image_1_height) // 2, image_1_width, image_1_height)
        
        self.image_crop_label.setGeometry(start_x + image_1_width + spacing, center_y + (max_height - image_crop_size) // 2, image_crop_size, image_crop_size)
        self.pixellated_crop_label.setGeometry(start_x + image_1_width + spacing + image_crop_size+ spacing, center_y + (max_height - pixellated_crop_size) // 2, pixellated_crop_size, pixellated_crop_size)
        self.output_pixmap_label.setGeometry(start_x + image_1_width + spacing + image_crop_size + spacing + pixellated_crop_size + spacing, center_y + (max_height - output_crop_size) // 2, output_crop_size, output_crop_size)
        # Adjust the scene size in QGraphicsView
        self.image_crop_label.setMaximumHeight(image_crop_size)
        self.image_crop_label.setMaximumWidth(image_crop_size)
        self.pixellated_crop_label.setMaximumHeight(pixellated_crop_size)
        self.pixellated_crop_label.setMaximumWidth(pixellated_crop_size)
        self.output_pixmap_label.setMaximumHeight(output_crop_size)
        self.output_pixmap_label.setMaximumWidth(output_crop_size)
        # Scale images 2, 3, and 4 (they maintain their aspect ratio)
        self.image_crop_label.setPixmap(self.image_crop_pixmap.scaled(image_crop_size, image_crop_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pixellated_crop_label.setPixmap(self.pixellated_crop_pixmap.scaled(pixellated_crop_size, pixellated_crop_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.output_pixmap_label.setPixmap(self.output_pixmap.scaled(output_crop_size, output_crop_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.crop_center_x, self.crop_center_y = int(self.view.viewport().rect().size().width() / 2), int(self.view.viewport().rect().size().height() / 2)

    def next_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                
                q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.current_video_pixmap = pixmap
                if self.current_item:
                    # Update the existing item to preserve the transformation
                    self.current_item.setPixmap(pixmap)
                else:
                    # First frame setup
                    self.current_item = QGraphicsPixmapItem(pixmap)
                    self.view.scene().addItem(self.current_item)
                    #self.view.fitInView(self.current_item, Qt.KeepAspectRatio)
                
                    self.view.scene().setSceneRect(self.current_item.boundingRect())
                    self.view.center_if_needed()
                self.set_crop()
                
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) 

    def set_crop(self):
        x_start = int(max(self.crop_center_x - 50, 0))
        y_start = int(max(self.crop_center_y - 50, 0))
        x_end = int(min(self.crop_center_x + 50, self.view.viewport().rect().width())) #self.video_w))
        y_end = int(min(self.crop_center_y + 50, self.view.viewport().rect().width())) #self.video_h))
        visible_rect = self.view.viewport().rect()
        pixmap = QPixmap(visible_rect.size())
        painter = QPainter(pixmap)
        self.view.render(painter, target=QRect(QPoint(0, 0), pixmap.size()), source=visible_rect)
        painter.end()

        image = self.QPixmapToArray(pixmap)
        cropped_image = image[y_start:y_end, x_start:x_end,  :]
        cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        cropped_image = np.ascontiguousarray(cropped_image)
        pixellated_image = np.repeat(np.repeat(cropped_image, 4, axis = 0), 4, axis = 1)  
        p_cropped_image = copy.deepcopy(cropped_image)

        if self.do_ocr:
            p_cropped_image = self.ocr_processor.perform_ocr(p_cropped_image)

        self.currentProcessedDisplayImage = image
        self.current_pixellated_image = pixellated_image
        self.currentProcessedCroppedImage = cropped_image
        self.current_cropped_image = cropped_image
        height, width, _ = cropped_image.shape
        bytes_per_line = 3 * width
        cropped_pixmap = QPixmap.fromImage(QImage(p_cropped_image.data, width, height, bytes_per_line, QImage.Format_RGB888))        
        height, width, _ = pixellated_image.shape
        bytes_per_line = 3 * width
        self.pixellated_crop_pixmap = QPixmap.fromImage(QImage(pixellated_image.data, width, height, bytes_per_line, QImage.Format_RGB888))
        self.pixellated_crop_label.setPixmap(self.pixellated_crop_pixmap)
        self.image_crop_pixmap = cropped_pixmap
        self.image_crop_label.setPixmap(cropped_pixmap)
                
    def run_still_execution(self):
        self.thread = QThread()
        self.worker = worker_classes.Worker(self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.set_parameters(self.currentProcessedCroppedImage, self.sr_processor)
        self.thread.start()
        self.worker.progress.connect(self.set_output_label)  

    def load_images(self):
        # Load and resize images
        self.image_crop_pixmap = QPixmap()
        self.pixellated_crop_pixmap = QPixmap()
        self.output_pixmap = QPixmap()
        self.image_crop_label.setPixmap(self.image_crop_pixmap)
        self.pixellated_crop_label.setPixmap(self.pixellated_crop_pixmap)
        self.output_pixmap_label.setPixmap(self.output_pixmap)

    def QPixmapToArray(self, pixmap):
        ## Get the size of the current pixmap
        size = pixmap.size()
        h = size.width()
        w = size.height()

        ## Get the QImage Item and convert it to a byte string
        qimg = pixmap.toImage()
        byte_str = qimg.bits().tobytes()

        ## Using the np.frombuffer function to convert the byte string into an np array
        img = np.frombuffer(byte_str, dtype=np.uint8).reshape((w,h,4))
        return img
    
    def save_current_view(self, filename, x, y):
        # Get the visible area of the view
        visible_rect = self.view.viewport().rect()
        visible_rect = self.view.viewport().rect()
        # Create a pixmap with the same size as the visible area
        pixmap = QPixmap(visible_rect.size())
        painter = QPainter(pixmap)
        self.view.render(painter, target=QRect(QPoint(0, 0), pixmap.size()), source=visible_rect)
        painter.end()

        image = self.QPixmapToArray(pixmap)
        video_h, video_w, _ = image.shape
        x_start = max(x - 50, 0)
        y_start = max(y - 50, 0)
        x_end = min(x + 50, video_w)
        y_end = min(y + 50, video_h)
        cv2.imwrite('crop/current_view_crop.jpg', image[y_start:y_end, x_start:x_end,  :])
        # Save the pixmap to a file

    def change_video_source(self, selected_index):
        # Stop the current video stream
        if self.cap:
            self.cap.release()
     
        if selected_index == 0:
            # Reset for manual video selection
            self.parent.media_buttons.select_media_button.setEnabled(True)
        # Get the selected source
        else:
            self.view.reset_to_default()
            self.parent.media_buttons.select_media_button.setEnabled(False)
            self.isMediaImage = False
            self.isMediaVideo = True
            # Start streaming from the selected source
            self.cap = cv2.VideoCapture(selected_index - 1)
            self.video_w, self.video_h = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.crop_center_x, self.crop_center_y = int(self.view.viewport().rect().size().width() / 2), int(self.view.viewport().rect().size().height() / 2)
            
            if self.cap and self.cap.isOpened():
                self.next_frame()
                self.video_thread.start()
                
    def closeEvent(self, event):
        self.isMediaVideo = False