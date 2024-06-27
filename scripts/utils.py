import os
import sys
from itertools import repeat
import cv2

# PyInstaller creates a temp folder and stores path in _MEIPASS
def resource_path(relative_path):
    try:
        
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#Function to return the model path using the model name
def model_path(name):
    return resource_path('ONNX_models\\new_'+name.lower()+'.onnx')

#Util scripts to be used in VPW
def scale_to_fit_canvas(image, canvas_width, canvas_height):
    image_height, image_width, _ = image.shape
    image_aspect_ratio = image_width / image_height
    canvas_aspect_ratio = canvas_width / canvas_height
    
    if image_aspect_ratio > canvas_aspect_ratio:
        scaling_factor = canvas_width / image_width
    else:
        scaling_factor = canvas_height / image_height
        
    scaled_w = image_width * scaling_factor
    scaled_h = image_height * scaling_factor
    
    array = cv2.resize(image, (int(scaled_w), int(scaled_h)), interpolation=cv2.INTER_LINEAR)
    
    return array

def calculate_video_position(widget_width, widget_height, video_width, video_height):
    # Calculate the aspect ratios of the widget and the video
    top_left_x = (widget_width - video_width) // 2
    top_left_y = (widget_height - video_height) // 2

    return top_left_x, top_left_y

def perform_pre_processing(input_array):
        img_yuv = cv2.cvtColor(input_array, cv2.COLOR_BGR2YUV)
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
        input_array = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
        return input_array
    
    
def generate_cropped_image(array, center_x, center_y):
    h, w, _ = array.shape
    if center_x < 0 or center_y < 0:
        cx = w // 2
        cy = h // 2
    else:
        cx = int(center_x * w)
        cy = int(center_y * h)
    sx = max(int ( cx - 50), 0)
    sy = max(int(cy - 50), 0)
    ex = min(int(cx + 50), w)
    ey = min(int(cy + 50), w)
    ret = array[sy: ey, sx : ex, :]
    return ret
