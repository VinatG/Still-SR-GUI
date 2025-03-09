'''
Python script to process the imge with the algorithm chosen by the user.
apply_post_processing function expects the image and the algorithm name.
It outputs the processed image
'''
from utils.histogram_equalization import histogram_equalize_image
from utils.globals import POST_PROCESSING_OPTIONS

def no_processing(image):
    """Returns the image as is (No Post-Processing)."""
    return image

def identity(image):
    """Identity function (returns the original image, same as no_processing)."""
    return image

def apply_post_processing(image, processing_type):
    """
    Applies the selected post-processing to the image.
    
    :param image: Input image (numpy array).
    :param processing_type: The name of the post-processing (string).
    :return: Processed image.
    """
    processing_functions = {
        "no_processing": no_processing,
        "histogram_equalization": histogram_equalize_image,
        "identity": identity
    }

    # Get the function name from global mapping
    func_name = POST_PROCESSING_OPTIONS.get(processing_type, "no_processing")

    # Get the function itself and apply it
    return processing_functions.get(func_name, no_processing)(image)
