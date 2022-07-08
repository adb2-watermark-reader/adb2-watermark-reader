import zlib

import bitarray.util as bit_util
import cv2 as cv
import numpy as np
from bitarray import bitarray


def gammaCorrection(src, gamma):
    invGamma = 1 / gamma
 
    table = [((i / 255) ** invGamma) * 255 for i in range(256)]
    table = np.array(table, np.uint8)
 
    return cv.LUT(src, table)


def reduce(bins, resized):
    """
    returns bins with the reduced resized array added to it
    """
    for i in range(len(bins)):
        bins[i] += (resized == i).sum()
    return bins


def number_of_different_bits(bit_array: bitarray, reference: bitarray) -> int:
    return abs(bit_array.count(True), reference.count(True))

def print_to_file(messages: list):
    with open("messages.json", "w") as f:
        f.write('[')
        for dictionary, i in zip(messages, range(len(messages))):
            f.write('{')
            j = 0
            for key, value in dictionary.items():
                f.write('"%s":"%s"\n' % (key, str(value)))
                j+=1
                if j < len(dictionary.items()):
                    f.write(',')
            f.write('}')
            if i < len(messages)-1:
                f.write(',')
        f.write(']')