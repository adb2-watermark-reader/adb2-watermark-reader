import sys
import time
import traceback
from typing import IO

import cv2 as cv
import numpy as np
from bitarray import bitarray

from utils import stringify_success
from watermark_message import WatermarkMessage


def handle_video_pipe(pipe: IO, video_resolution, framerate):
    frame_count = 0
    last_wm: WatermarkMessage = None
    last_wm_frame = 0
    last_print_frame = 0
    success_count = 0
    error_count = 0

    while True:
        frame_count += 1
        in_bytes = pipe.read(video_resolution[0] * video_resolution[1] * 3)

        if not in_bytes or len(in_bytes) < video_resolution[0] * video_resolution[1] * 3:
            break

        img = np.frombuffer(in_bytes, np.uint8).reshape((video_resolution[0], video_resolution[1], 3))

        try:
            video_payload = decode(img)

            last_wm = video_payload

            last_wm_frame = frame_count

        except AssertionError:
            pass
        except Exception as err:
            print("error: ", err, file=sys.stderr)

        if frame_count > last_print_frame + framerate * 1.5:
            last_print_frame = frame_count
            if frame_count > last_wm_frame + framerate * 4.5 or last_wm is None:
                error_count += 1
                print(f"video {stringify_success(success_count, error_count)}    no video watermark found",file=sys.stderr)
            else:
                success_count += 1
                print(f"video {stringify_success(success_count, error_count)}    {last_wm.extended_vp1_message.vp1_message.packet.vp1_payload}")


def decode(img):
    luma_threshold = 3

    first_row_luma = cv.cvtColor(img, cv.COLOR_BGR2YCR_CB)[0, :, 0][None]
    resized = cv.resize(first_row_luma, (30 * 8, 1), interpolation=cv.INTER_LINEAR)
    byte_array = np.packbits(resized > luma_threshold).tobytes()

    bits = bitarray()
    bits.frombytes(byte_array)

    return WatermarkMessage(bits)
