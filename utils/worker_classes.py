import numpy as np
from PySide6.QtCore import Signal, QObject
from utils import execute_sr
import gc

class Worker(QObject):
    finished = Signal()
    progress = Signal(object)
    
    def __init__(self, parent):
        super(Worker, self).__init__()
        self.parent = parent
        #Parameters required for computing the super-resolution execution
        self.inp_img_array = None
        self.sr_processor = None
        
    def run(self):
        out_mat = self.sr_processor.perform_sr(self.inp_img_array)
        out_mat = np.ascontiguousarray(out_mat, dtype = np.uint8)
        self.progress.emit(out_mat) 
        self.finished.emit() 

    #Function to set the parameters require for super-resolution execution
    def set_parameters(self, inp_img_array, sr_processor):
        self.inp_img_array, self.sr_processor = inp_img_array, sr_processor

# Signals that can be emitted by the Video Worker Class
class SR_Video_WorkerSignals(QObject):
    #WorkerSignlas class is used to defined the kind of signals that will be emiited by the Worker class
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(object)

# QRubbable Worker Class for performing Super-Resolution on a Video

class SR_Video_Worker(QObject):
    finished = Signal()
    progress = Signal(object)
    
    def __init__(self, fn, *args, **kwargs):
        super(SR_Video_Worker, self).__init__()
        #Parameters required for computing the super-resolution execution
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = SR_Video_WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress
        
    def run(self):
        result = self.fn(self.progress)
        self.finished.emit()
        



        


