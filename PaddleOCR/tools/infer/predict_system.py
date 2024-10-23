# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import sys


__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))
os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

import cv2
import copy
import numpy as np

import time

import tools.infer.predict_rec as predict_rec
import tools.infer.predict_det as predict_det
#import tools.infer.predict_cls as predict_cls


#from tools.infer.utility import draw_ocr_box_txt, get_rotate_crop_image, get_minarea_rect_crop
from tools.infer.utility import get_rotate_crop_image



class TextSystem(object):
    def __init__(self, det_model_session, rec_model_session): # det_model_file_path, rec_model_file_path):
        self.text_detector = predict_det.TextDetector(det_model_session) # det_model_file_path)
        self.text_recognizer = predict_rec.TextRecognizer(rec_model_session) # rec_model_file_path)
        self.use_angle_cls = False
        self.drop_score = 0.5


        
        self.crop_image_res_index = 0

    def draw_crop_rec_res(self, output_dir, img_crop_list, rec_res):
        os.makedirs(output_dir, exist_ok=True)
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite(
                os.path.join(output_dir,
                             f"mg_crop_{bno+self.crop_image_res_index}.jpg"),
                img_crop_list[bno])

        self.crop_image_res_index += bbox_num

    def __call__(self, img, cls=True):
        time_dict = {'det': 0, 'rec': 0, 'cls': 0, 'all': 0}



        start = time.time()
        ori_im = img.copy()
        dt_boxes, elapse = self.text_detector(img)
        time_dict['det'] = elapse

        if dt_boxes is None:
       
            end = time.time()
            time_dict['all'] = end - start
            return None, None, time_dict

        img_crop_list = []

        dt_boxes = sorted_boxes(dt_boxes)

        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])

            img_crop = get_rotate_crop_image(ori_im, tmp_box)

            img_crop_list.append(img_crop)
 

        rec_res, elapse = self.text_recognizer(img_crop_list)
        time_dict['rec'] = elapse


        filter_boxes, filter_rec_res = [], []
        for box, rec_result in zip(dt_boxes, rec_res):
            text, score = rec_result[0], rec_result[1]
            if score >= self.drop_score:
                filter_boxes.append(box)
                filter_rec_res.append(rec_result)
        end = time.time()
        time_dict['all'] = end - start
        return filter_boxes, filter_rec_res, time_dict


def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        for j in range(i, -1, -1):
            if abs(_boxes[j + 1][0][1] - _boxes[j][0][1]) < 10 and \
                    (_boxes[j + 1][0][0] < _boxes[j][0][0]):
                tmp = _boxes[j]
                _boxes[j] = _boxes[j + 1]
                _boxes[j + 1] = tmp
            else:
                break
    return _boxes


def paddleocr_predict(img, det_model_session, rec_model_session): # det_model_file_path = './inference/det_onnx/model.onnx', rec_model_file_path = './inference/rec_onnx/model.onnx'):

   
    text_sys = TextSystem(det_model_session, rec_model_session) # det_model_file_path, rec_model_file_path)
    starttime = time.time()
    dt_boxes, rec_res, time_dict = text_sys(img)
    elapse = time.time() - starttime
  


    res = [{
        "transcription": rec_res[i][0],
        "points": np.array(dt_boxes[i]).astype(np.int32).tolist(),
    } for i in range(len(dt_boxes))]
  

    for i in res:
        text = i['transcription']
        points = i['points']
        x1y1 = points[0]
        x2y2 = points[2]
        w = x2y2[0] - x1y1[0]
        h = x2y2[1] - x1y1[1]
        font_scale = min( w/100,  h/100) * 2
        thickness =round( font_scale * 1.1  )#int(min(w, h) / 30) * base_thickness
    
                    
        c_image = cv2.rectangle(img, x1y1, x2y2, (255, 0, 0), 1)
        cv2.putText(c_image, text, (x1y1[0], x1y1[1] - 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0,0,255), thickness)

    return img
"""
    if is_visualize:
        image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        boxes = dt_boxes
        txts = [rec_res[i][0] for i in range(len(rec_res))]
        scores = [rec_res[i][1] for i in range(len(rec_res))]

        draw_img = draw_ocr_box_txt(
            image,
            boxes,
            txts,
            scores,
            drop_score=drop_score,
            font_path=font_path)

        save_file = image_file
    cv2.imwrite(
        os.path.join(draw_img_save_dir,
                        os.path.basename(save_file)),
        draw_img[:, :, ::-1])
"""
if __name__ == "__main__":
    det_model_file_path, rec_model_file_path = './inference/det_onnx/model.onnx', './inference/rec_onnx/model.onnx'
    image_path = 'img_12.jpg'
    img = cv2.imread(image_path)
    predict(img, det_model_file_path, rec_model_file_path)



