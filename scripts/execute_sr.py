#Script defining the function to execute Super-Resolution on the input data
import numpy as np

#Function to map the model name to the window size
model_name_window_size_mapping = {'realworldsr-diffirs2-ganx4-v2' : 8, 'realworldsr-diffirs2-ganx2-v2' : 16}
model_name_scale_map = {'realworldsr-diffirs2-ganx4-v2' : 4, 'realworldsr-diffirs2-ganx2-v2' : 2}

#Function to convert the input image to numpy array suitable for the onnx model
def img2nmp(image):
    image_array = np.asarray(image, dtype=np.float32) / 255.0
    image_array = image_array[...,::-1]
    image_array = np.transpose(image_array, (2,0,1))
    image_array=np.expand_dims(image_array,0)
    return image_array

#Perform super-resolution and pad the input according to the appropriate window size
def output_on_pad_image(sess, output_name, inputs, window_size, scale):
    mod_pad_h, mod_pad_w = 0, 0
    _, _, h, w = inputs.shape
    if h % window_size != 0:
        mod_pad_h = window_size - h % window_size
    if w % window_size != 0:
        mod_pad_w = window_size - w % window_size

    pad_width = ((0, 0), (0, 0),(0, mod_pad_h), (0, mod_pad_w))
    lq = np.pad(inputs, pad_width, mode='reflect')
    lq,mod_pad_h,mod_pad_w

    #Running the onnx model
    out_mat = sess.run([output_name], {'input': lq})[0]
    _, _, h, w = out_mat.shape

    out_mat = out_mat[:, :, 0:h - mod_pad_h * scale, 0:w - mod_pad_w * scale]
    out_mat = np.squeeze(out_mat,0)
    out_mat = np.transpose(out_mat, (1,2,0))
    out_mat = out_mat * 255.0
 
    return out_mat

def execute_sr(sess, inp_image, sr_model_name):
    inputs = img2nmp(inp_image[:, :, ::-1])
    output_name = sess.get_outputs()[0].name
    window_size = model_name_window_size_mapping[sr_model_name]
    out_mat = output_on_pad_image(sess ,output_name ,inputs ,window_size, model_name_scale_map[sr_model_name])
    out_mat = (np.rint(out_mat)).astype(int)
    out_mat = np.clip(out_mat, a_min=0, a_max=255)
    out_mat = out_mat.astype(np.uint8)

    return out_mat