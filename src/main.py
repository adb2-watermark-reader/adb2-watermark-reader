import subprocess as sp
import sys
import threading
from tracemalloc import get_object_traceback
from typing import IO

import cv2
import numpy as np
import audio_spec_constants as consts

import audio_decoder
import video_decoder


def audio(pipe: IO):
    buffer = bytearray()

    while True:
        in_bytes = pipe.read(int(samplerate * consts.sec_per_vp1_cell * 2))  # 1 cell

        if not in_bytes:
            break
        buffer.extend(in_bytes)

        buffer = buffer[-int(samplerate * consts.sec_per_vp1_cell * 3 * 2):]  # 4.5 seconds or 3 cells

        try:
            audio_payload = audio_decoder.decode(np.frombuffer(buffer, dtype='<i2'), samplerate)
            print(audio_payload)
        except Exception as err:
            print(err, file=sys.stderr)


def video(pipe: IO):
    while True:
        in_bytes = pipe.read(video_resolution[0] * video_resolution[1] * 3)

        if not in_bytes or len(in_bytes) < video_resolution[0] * video_resolution[1] * 3:
            break

        # TODO replace with the code for detection
        img = np.frombuffer(in_bytes, np.uint8).reshape((video_resolution[0], video_resolution[1], 3))

        try:
            video_payload = video_decoder.decode(img)
            if not video_payload == None:
                print(video_payload)
        except Exception as err:
            print(err, file=sys.stderr)

        # cv2.imshow("hmm", img)
        # cv2.waitKey(0)


# pipes based on https://stackoverflow.com/a/71057629

if __name__ == "__main__":
    # in_filename = "rtsp://localhost/live"
    in_filename = "tcp://localhost:1234"
    # in_filename = "https://f111.rndfnk.com/ard/wdr/1live/diggi/mp3/128/stream.mp3?sid=2B1eCeSmJXOZEEiPpOnnykFYHP4&token=pGly4HjCjIPjybbqtozZnU3Oh1m-eP9YiXr5ya-83LI&tvf=zRZyqral-xZmMTExLnJuZGZuay5jb20"
    # in_filename = "video.ts"

    samplerate = 48000
    video_resolution = (720, 1280)
    # video_resolution = (1080, 1920)

    process = sp.Popen(
        'ffmpeg -hide_banner -loglevel error '  # Set loglevel to error for disabling the prints ot stderr
        # '-rtsp_transport tcp '              # needed when using obs over rtsp
        f'-i {in_filename} '
        '-vcodec rawvideo -pix_fmt rgb24 '  # Raw video codec with rgb24 pixel format                               
        '-map 0:v -f:v rawvideo pipe:2 '  # rawvideo format is mapped to stderr pipe
        f'-acodec pcm_s16le -ar {samplerate} -ac 1 '  # Audio codec pcm_s16le (-ar 16k has no affect)
        '-map 0:a -f:a s16le pipe:1 '  # s16le audio format is mapped to stdout pipe
        # '-report'  # Create a log file (because we can't the statuses that are usually printed to stderr).
        , stdout=sp.PIPE, stderr=sp.PIPE, shell=True)

    threading.Thread(target=audio, args=(process.stdout,)).start()
    threading.Thread(target=video, args=(process.stderr,)).start()
