from PaddleOCR.tools.infer.predict_system import paddleocr_predict as paddle_ocr_predict
import numpy as np
import onnxruntime as rt
import utils.globals

class OCRProcessor:
    def __init__(self):
        self.load_session()

    def load_session(self, ocr_det_model_path = utils.globals.ocr_det_model_path, rec_det_model_path = utils.globals.ocr_rec_model_path, provider = utils.globals.providers):
        self.ocr_det_sess = rt.InferenceSession(ocr_det_model_path,  providers = provider)
        self.ocr_rec_sess = rt.InferenceSession(rec_det_model_path,  providers = provider)

    def perform_ocr(self, input_mat):
        return paddle_ocr_predict(input_mat, self.ocr_det_sess, self.ocr_rec_sess)
    
class SRProcessor:
    def __init__(self):
        self.model_name_window_size_mapping = {4 : 8, 2 : 16}
        self.set_scale()

    def set_scale(self, scale = 4):
        self.current_model_scale = scale
        self.load_session()

    def load_session(self, sr_model_path = utils.globals.sr_model_paths[4], provider = utils.globals.providers):
        self.sr_sess = rt.InferenceSession(sr_model_path,  providers = provider) 

    # Function to convert the input image to numpy array suitable for the onnx model
    def img2nmp(self, image):
        image_array = np.asarray(image, dtype=np.float32) / 255.0
        image_array = image_array[...,::-1]
        image_array = np.transpose(image_array, (2, 0, 1))
        image_array = np.expand_dims(image_array, 0)
        return image_array

    # Perform super-resolution and pad the input according to the appropriate window size
    def output_on_pad_image(self, sess, output_name, inputs, window_size):
        mod_pad_h, mod_pad_w = 0, 0
        _, _, h, w = inputs.shape
        if h % window_size != 0:
            mod_pad_h = window_size - h % window_size
        if w % window_size != 0:
            mod_pad_w = window_size - w % window_size

        pad_width = ((0, 0), (0, 0),(0, mod_pad_h), (0, mod_pad_w))
        lq = np.pad(inputs, pad_width, mode = 'reflect')

        #Running the onnx model
        out_mat = sess.run([output_name], {'input' : lq})[0]
        _, _, h, w = out_mat.shape

        out_mat = out_mat[:, :, 0 : h - mod_pad_h * self.current_model_scale, 0 : w - mod_pad_w * self.current_model_scale]
        out_mat = np.squeeze(out_mat, 0)
        out_mat = np.transpose(out_mat, (1, 2, 0))
        out_mat = out_mat * 255.0
    
        return out_mat


    def perform_sr(self, inp_image):
        inputs = self.img2nmp(inp_image[:, :, ::-1])
        output_name = self.sr_sess.get_outputs()[0].name
        window_size = self.model_name_window_size_mapping[self.current_model_scale]
        out_mat = self.output_on_pad_image(self.sr_sess, output_name, inputs, window_size)
        out_mat = (np.rint(out_mat)).astype(int)
        out_mat = np.clip(out_mat, a_min = 0, a_max = 255)
        out_mat = out_mat.astype(np.uint8)

        return out_mat