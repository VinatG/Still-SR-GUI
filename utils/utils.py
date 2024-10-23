import os
import sys
import cv2
import numpy as np
from utils.preprocessings import histogram_equalize_image
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
    return histogram_equalize_image(input_array)
    
    
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
    ey = min(int(cy + 50), h)
    ret = array[sy: ey, sx : ex, :]
    return ret

def process_views(display_image, crop, pixellated_crop, sr_crop, scale = 4):
  processed_frame = np.ones((1080, 1920, 3), dtype = np.uint8) * 255
  inp_img_h, inp_img_w, _ = display_image.shape
  
  x1, y1 = (492 - int(inp_img_w / 2)), (540 - int(inp_img_h / 2) - 1)
  x2, y2 = x1 + inp_img_w, y1 + inp_img_h
  processed_frame[y1 : y2, x1 : x2, :] = display_image[:, :, :3]
  processed_frame[489: 489 + 100, 984 : 984 + 100, :] = crop[:, :, :3][:, :, ::-1]
  processed_frame[339: 339 + 400, 1096 : 1096 + 400, :] = pixellated_crop[:, :, :3][:, :, ::-1]
  processed_frame[339: 339 + 400, 1508 : 1508 + 400, :] = sr_crop[:, :, ::-1]

  return processed_frame

def frames_to_video(save_path, img_array):
    print(f'Number of frames = {len(img_array)}')
    out = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (1920, 1080))
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

def save_image(save_image_path, inp_img, sr_image):
    processed_frame = process_views(inp_img, sr_image)
    cv2.imwrite(save_image_path, processed_frame)