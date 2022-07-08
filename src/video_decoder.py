import sys
from typing import IO

import cv2 as cv
import numpy as np
from utils import reduce, disassemble_bitarray_into_components, check_crc, print_to_file
from bitarray import bitarray
import bitarray.util as bit_util
import time

WIDTH = 1280
FRAMERATE = 50 # frames per second
MAXTIME = 300
MAXFRAMES = MAXTIME * FRAMERATE
# video.ts video watermarks carries only extended_vp1_messages (i.e. wp_message_id = 0x07)
FILE = 'video.ts'
PARITY_WHITENING_SEQUENCE = 0b00111001110010100111100011110000011100101001100100011011110100100010011111000
PAYLOAD_WHITENING_SEQUENCE = 0b11001001110100011101011100010010011001110101101100
LUMA_THRESHOLD = 3


def handle_video_pipe(pipe: IO, video_resolution):
    while True:
        in_bytes = pipe.read(video_resolution[0] * video_resolution[1] * 3)

        if not in_bytes or len(in_bytes) < video_resolution[0] * video_resolution[1] * 3:
            break

        img = np.frombuffer(in_bytes, np.uint8).reshape((video_resolution[0], video_resolution[1], 3))

        try:
            video_payload = decode(img)
            if video_payload:
                print(video_payload)
        except Exception as err:
            print(err, file=sys.stderr)


def find_run_in_pattern(resized, run_in_pattern = "eb52"):
    """
    primitive algorithm for finding a reasonable threshold for luma values
    returns None if run-in-pattern wasnt found
    """
    for i in range(3):
        threshold = 1+i
        byte_array = np.packbits(resized > threshold).tobytes()
        if byte_array.hex().startswith(run_in_pattern):
            return byte_array
    return None


def decode(img):
    first_row_luma = cv.cvtColor(img, cv.COLOR_BGR2YCR_CB)[0, :, 0][None]
    resized = cv.resize(first_row_luma, (30 * 8, 1), interpolation=cv.INTER_LINEAR)
    byte_array = np.packbits(resized > LUMA_THRESHOLD).tobytes()
    print(byte_array.hex())
    if not byte_array.hex().startswith('eb52'):
        return None
    bits = bitarray()
    bits.frombytes(byte_array)
    disassembled_message = disassemble_bitarray_into_components(bits)
    if check_crc(disassembled_message):
        return disassembled_message


def from_file_to_messages(file: str) -> dict:
    i = 0
    count_header_not_detected = 0
    count_duplicates = 0
    count_wrong_crc = 0
    bins = np.zeros(256, dtype = int)
    cap = cv.VideoCapture(file)
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
            byte_array = find_run_in_pattern(resized) # early error correction
            if byte_array != None:
                bits = bitarray()
                try:
                    bits.frombytes(byte_array)
                    disassembled_message = disassemble_bitarray_into_components(bits)
                    if check_crc(disassembled_message):
                        if disassembled_message["version"] != old_message_version: # duplicate check
                            old_message_version = disassembled_message["version"] 
                            messages.append(disassembled_message)
                        else:
                            count_duplicates += 1
                    else:
                        count_wrong_crc += 1
                        # TODO: late error correction
                except ValueError as e:
                    print(f'ValueError \"{e}\" in iteration {i} with bytearray {byte_array.hex()}. (Probably error in messagelength)')
                    print(f'wrong bitarrays: {bits}')
            else:
                count_header_not_detected += 1
    print(f'''Out of {MAXFRAMES} frames: 
    - {count_header_not_detected} with wrong header 
    - {count_duplicates} duplicate messages
    - {count_wrong_crc} messages with errors
    - {len(messages)} correct messages\n''')
    return messages


def main():
    t0 = time.time()
    messages = from_file_to_messages(FILE)    
    print_to_file(messages)
    print(f'Elapsed time: {time.time()-t0} for {MAXTIME} seconds video.')
    
    # TODO: concat messages


if __name__ == '__main__':
    main()
