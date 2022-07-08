import sys
import traceback
from typing import IO

import cv2 as cv
import numpy as np
from bitarray import bitarray

from watermark_message import WatermarkMessage


def handle_video_pipe(pipe: IO, video_resolution):
    while True:
        in_bytes = pipe.read(video_resolution[0] * video_resolution[1] * 3)

        if not in_bytes or len(in_bytes) < video_resolution[0] * video_resolution[1] * 3:
            break

        img = np.frombuffer(in_bytes, np.uint8).reshape((video_resolution[0], video_resolution[1], 3))

        try:
            video_payload = decode(img)
            if video_payload:
                print(f"video {video_payload.extended_vp1_message.vp1_message.packet.vp1_payload}")
        except Exception as err:

            # _, _, tb = sys.exc_info()
            # traceback.print_tb(tb)  # Fixed format
            # tb_info = traceback.extract_tb(tb)
            # filename, line, func, text = tb_info[-1]
            #
            # print('An error occurred on line {} in statement {}'.format(line, text))

            print(err, file=sys.stderr)


def decode(img):
    luma_threshold = 3

    first_row_luma = cv.cvtColor(img, cv.COLOR_BGR2YCR_CB)[0, :, 0][None]
    resized = cv.resize(first_row_luma, (30 * 8, 1), interpolation=cv.INTER_LINEAR)
    byte_array = np.packbits(resized > luma_threshold).tobytes()
    # print(byte_array.hex())
    if not byte_array.hex().startswith('eb52'):
        return None
    bits = bitarray()
    bits.frombytes(byte_array)
    disassembled_message = WatermarkMessage(bits)
    if disassembled_message.has_valid_crc:
        return disassembled_message
