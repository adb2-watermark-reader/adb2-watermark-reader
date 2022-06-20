import cv2 as cv
import numpy as np
from utils import reduce, disassemble_bitarray_into_components, check_crc, print_to_file
from bitarray import bitarray
import bitarray.util as bit_util
import time

WIDTH = 1280
FRAMERATE = 50 # frames per second
MAXTIME = 10
MAXFRAMES = MAXTIME * FRAMERATE

def find_run_in_pattern(resized, run_in_pattern = "eb52"):
    """
    primitive algorithm for finding a reasonable threshold for luma values
    returns None if run-in-pattern wasnt found
    """
    for i in range(3):
        threshold = 2+i
        byte_array = np.packbits(resized > threshold).tobytes()
        if byte_array.hex().startswith(run_in_pattern):
            return byte_array
    return None


if __name__ == '__main__':
    t0 = time.time()
    i = 0
    bins = np.zeros(256, dtype = int)
    cap = cv.VideoCapture('../video.ts')
    old_message_version = None
    messages = []
    while cap.isOpened() and i < MAXFRAMES:
        i+=1
        ret, frame = cap.read()
        if ret:
            # drop all but the first component of YCR_CB colorspace to only keep luma
            first_row_luma = cv.cvtColor(frame, cv.COLOR_BGR2YCR_CB)[0, :, 0][None]
            # 30 bytes of data
            resized = cv.resize(first_row_luma, (30 * 8, 1), interpolation=cv.INTER_LINEAR)

            bins = reduce(bins, resized) # contains the frequency of the luma values.
            byte_array = find_run_in_pattern(resized)
            if byte_array != None:
                bits = bitarray()
                try:
                    bits.frombytes(byte_array)
                    disassembled_message = disassemble_bitarray_into_components(bits)
                    if check_crc(disassembled_message):
                        if disassembled_message["version"] != old_message_version: # duplicate check
                            old_message_version = disassembled_message["version"] 
                            messages.append(disassembled_message)
                except ValueError as e:
                    print(f'ValueError \"{e}\" in iteration {i} with bytearray {byte_array.hex()}')
    print_to_file(messages)
    print(f'Elapsed time: {time.time()-t0} for {MAXTIME} seconds video.')




