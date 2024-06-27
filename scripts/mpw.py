import cv2
import numpy as np
from araviq6.qt_compat import QtGui
from PySide6.QtCore import Qt, QUrl, QThread, Signal, QObject
import qimage2ndarray
from scripts import execute_sr
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from araviq6 import (
    ArrayWorker,
    ArrayProcessor,
    NDArrayLabel,
)
from scripts import utils

#Global variables that are shared across classes 
center_x, center_y = -1, -1
do_pre_processing = False
scale = 4 #Current model scale
width, height = 400, 400


#Worker class that will execute Super Resolution on a separate thread
#Emits the super-resolved output during progress followed by the finished signal
class Worker(QObject):
    finished = Signal()
    progress = Signal(object)
    
    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()
        #Parameters required for computing the super-resolution execution
        self.inp_img_array = None
        self.sess = None
        self.sr_model_name = None
        
    def run(self):
        out_mat = execute_sr.execute_sr(self.sess, self.inp_img_array, self.sr_model_name)
        out_mat = np.ascontiguousarray(out_mat, dtype=np.uint8)
        self.progress.emit(out_mat) #Emitting the super-resolved image as progress signal
        self.finished.emit() #Emitting the finish signal after the execution is completed
        
    #Function to set the parameters require for super-resolution execution
    def set_parameters(self, inp_img_array, sess, sr_model_name):
        self.inp_img_array, self.sess, self.sr_model_name = inp_img_array, sess, sr_model_name

#Modified NDArray label to accept mouse press events on the input side.
class InputNDArrayLabel(NDArrayLabel):
    finished = Signal()
    def __init__(self, parent = None):
        super().__init__(parent)
        self.cropMode = False
        
    def setCropMode(self, mode: bool):
        self.cropMode = mode
        
    def mousePressEvent(self, event):
        global center_x, center_y
        video_width, video_height = self.pixmap().size().width(), self.pixmap().size().height()
        widget_width, widget_height = self.size().width(), self.size().height()
        x, y = utils.calculate_video_position(widget_width, widget_height, video_width, video_height)
        pos_x, pos_y = event.pos().x(), event.pos().y()
        rel_x , rel_y = pos_x - x, pos_y - y

        if rel_x < 0 or rel_x > video_width or rel_y < 0 or rel_y > video_height:
            rel_x, rel_y = -1, -1
        else:
            rel_x = rel_x / video_width
            rel_y = rel_y / video_height

        center_x, center_y = rel_x, rel_y
        self.finished.emit()

    def setArray(self, arg):
        full_display_image, cropped_image =  arg
        array = None
        
        if self.cropMode:
            array = cropped_image
        else:
            array = full_display_image
        if array.size > 0:
            pixmap = QtGui.QPixmap.fromImage(qimage2ndarray.array2qimage(array))
        else:
            pixmap = QtGui.QPixmap()
        self.setPixmap(pixmap)
        
#Array worker class for the input array
class InputWorker(ArrayWorker):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arr = None

    def processArray(self, array: np.ndarray) -> np.ndarray:
        global center_x, center_y, do_pre_processing, width, height
        h, w, c = array.shape
        full_display_image, cropped_image = array.copy(), None
        cropped_image = utils.generate_cropped_image(array, center_x, center_y)
 
        if h > height or w > width:
            full_display_image = utils.scale_to_fit_canvas(array, height, width)
    
        if do_pre_processing: 
            full_display_image = utils.perform_pre_processing(full_display_image)
            cropped_image = utils.perform_pre_processing(cropped_image)

        return full_display_image, cropped_image

#Array worker class for the middle view array
class DuplicateWorker(ArrayWorker):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arr = None 

    def processArray(self, array: np.ndarray) -> np.ndarray:              
        array = np.repeat(np.repeat(array, scale, axis=0), scale, axis=1)

        return array

#Main widget conisting of the 3 views and the 2 buttons
class MediaPlayerWidget(QWidget):
    def __init__(self, sess, modelName, parent=None):
        super().__init__(parent)
        
        self.currentSession = sess
        self.currentModelName = modelName
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        #Initialising the 3 arryas that will be accesed and updated by the 3 views and the array workers.
        self.currentProcessedDisplayImage = np.empty((0, 0, 0), dtype=np.uint8)
        self.currentStillImage = np.empty((0, 0, 0), dtype=np.uint8)
        self.currentProcessedCroppedImage = np.empty((0, 0, 0), dtype=np.uint8)
        
        #Input view setup
        self.inputArrayProcessor = ArrayProcessor()
        self.inputWorker = InputWorker()
        self.input_label = InputNDArrayLabel()
        self.input_label.setCursor(Qt.CrossCursor) #So that the cursor looks like a cross when hovered over input view to select the center of crops
        self.inputArrayProcessor.setWorker(self.inputWorker)
        
        #Setting up duplicated display
        self.duplicateWorker = DuplicateWorker()
        self.duplicateArrayProcessor = ArrayProcessor()
        self.duplicated_input_label = NDArrayLabel()
        self.duplicateArrayProcessor.setWorker(self.duplicateWorker)
        
        #Setting up the output display
        self.output_label = NDArrayLabel() 
 
        #Setting up the connections between the Slots and Signals of the array workers
        self.inputArrayProcessor.arrayProcessed.connect(self.input_label.setArray)
        self.duplicateArrayProcessor.arrayProcessed.connect(self.duplicated_input_label.setArray) 
        self.input_label.finished.connect(self.pointerUsed)

        #Setting up the buttons
        self.cropButton = QPushButton('Pixel2Pixel')
        self.cropButton.setCheckable(True)
        self.pre_processing_button = QPushButton("Pre-process")
        self.pre_processing_button.setCheckable(True)
        self.scale_toggle_button = QPushButton("2x", self)
        self.cropButton.toggled.connect(self.onCropButtonToggle)
        self.pre_processing_button.toggled.connect(self.pre_processing_button_toggle)

        #Setting up the alignment, Views and the Widgets
        
        #Setting the alignment
        self.input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.duplicated_input_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #Setting up the views
        self.views_layout = QHBoxLayout()
        self.views_layout.addWidget(self.input_label)
        self.views_layout.addWidget(self.duplicated_input_label)
        self.views_layout.addWidget(self.output_label)       
        #Setting up the buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.cropButton)
        self.button_layout.addWidget(self.pre_processing_button)
        self.button_layout.addWidget(self.scale_toggle_button)
        #Combining the views and the widgets into one
        layout = QVBoxLayout()
        layout.addLayout(self.views_layout)
        layout.addLayout(self.button_layout)
        self.setLayout(layout)

    def pointerUsed(self):
        self.run_still_execution()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        # Check if the dropped data contains URLs, and if yes, accept the event
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def setModelName(self, name):
        self.currentModelName = name

    def setSession(self, s):
        self.currentSession = s

    def pre_processing_button_toggle(self, state: bool):
        global do_pre_processing
        do_pre_processing = state
        if state:
            self.pre_processing_button.setText("No Pre-processing")
        else:
            self.pre_processing_button.setText("Pre-processing")
        self.run_still_execution()

    def dropEvent(self, event: QDropEvent):
        # Handle the drop event
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # We're interested in the first URL only (you could extend this to support multiple files)
            if urls and urls[0].isLocalFile():
                video_path = urls[0].toLocalFile()
                self.setSource(QUrl.fromLocalFile(video_path))
            event.acceptProposedAction()
        else:
            event.ignore()

    def onCropButtonToggle(self, state: bool):
        if state:
            self.cropButton.setText('Full-scale')
        else:
            self.cropButton.setText('Pixel2Pixel')
        self.input_label.setCropMode(state)
        self.input_label.setArray((self.currentProcessedDisplayImage, self.currentProcessedCroppedImage))

    def _storeLastCroppedImage(self, array: np.ndarray):
        self._lastCroppedImage = array.copy()

    def setScale(self, s):
        global scale
        scale = s

    def updateDuplicateLabel(self):
        self.duplicated_input_label.setArray(self.duplicateWorker.processArray(self.currentProcessedCroppedImage))
    
    #Function to perform Super-Resolution on the input in a separate thread
    def run_still_execution(self):
        
        array = self.currentStillImage
        self.currentProcessedDisplayImage, self.currentProcessedCroppedImage = self.inputWorker.processArray(array)
        self.input_label.setArray((self.currentProcessedDisplayImage, self.currentProcessedCroppedImage))
        self.input_label.show()
        
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.set_parameters(self.currentProcessedCroppedImage, self.currentSession, self.currentModelName)
        self.thread.start()

        self.worker.progress.connect(self.updateOutputLabel)
        self.worker.finished.connect(self.updateDuplicateLabel)

    def setStillImage(self, array):
        self.currentStillImage = array

    def updateOutputLabel(self, sr_image): 
        self.output_label.setArray(sr_image)
        self.output_label.show()

    def setStillSource(self, image_path):
        #Converting image path to image and displaying
        img_path = image_path.replace('/', '\\')[1:] #Converting string path with / to path with \\
        img = cv2.imread(img_path)
        array = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.setStillImage(array)
        self.run_still_execution()

    def setSource(self, url: QUrl):
        global center_x, center_y, do_pre_processing
        do_pre_processing, center_x, center_y = False, -1, -1

        if QUrl.fileName(url).rsplit('.', 1)[1] in ['bmp', 'jpg', 'jpeg', 'png']:
            self.setStillSource(QUrl.path(url))

