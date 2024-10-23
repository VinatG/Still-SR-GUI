# histogram_equalize_image is the main function to which the input image is passed

import numpy as np
import math


def calculate_histogram(image):
    # Convert the image to grayscale using equal weights for R, G, B channels
    grayscale = np.dot(image[..., :3], [1/3, 1/3, 1/3])
    # Calculate the histogram
    histogram, bins = np.histogram(grayscale, bins=256, range=(0, 256))
    return histogram

#Function inspired from ImageJ java code where they take the square root for values>=2
def get_weighted_value(histogram, i, classic_equalization = False):
    h = histogram[i]
    if h < 2 or classic_equalization:
        return float(h)
    return math.sqrt(float(h))

#Main function to which the image is passed
def histogram_equalize_image(image):
    histogram = calculate_histogram(image)
    max = 255
    range_variable = 255
    sum = get_weighted_value(histogram, 0)
    for i in range(1, max):
        sum += 2 * get_weighted_value(histogram, i)
    sum += get_weighted_value(histogram, max)
    scale = range_variable / sum

    # lut -> Look up table
    lut = [0] * (range_variable + 1)

    lut[0] = 0

    sum = get_weighted_value(histogram, 0)

    for i in range(1, max):
        delta =  get_weighted_value(histogram, i)
        sum += delta
        lut[i] = int(round(sum * scale))
        sum += delta

    lut[max] = max 
    lut = np.array(lut, dtype = np.uint8)
    return lut[image]