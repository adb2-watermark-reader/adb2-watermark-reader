import ffmpeg
import numpy as np
import time

from audio_decoder import do_decoding

# loosely based on https://kkroening.github.io/ffmpeg-python/

if __name__ == "__main__":
    # in_filename = "rtsp://localhost/live"
    in_filename = "tcp://localhost:1234"
    # in_filename = "https://f111.rndfnk.com/ard/wdr/1live/diggi/mp3/128/stream.mp3?sid=2B1eCeSmJXOZEEiPpOnnykFYHP4&token=pGly4HjCjIPjybbqtozZnU3Oh1m-eP9YiXr5ya-83LI&tvf=zRZyqral-xZmMTExLnJuZGZuay5jb20"
    # in_filename = "video.ts"

    samplerate = 48000

    process1 = (
        ffmpeg
        # .input(in_filename, rtsp_transport='tcp')
        .input(in_filename)
        .output('pipe:', format='s16le', ac=1, ar=samplerate)
        .run_async(pipe_stdout=True)
    )

    timee = time.time()
    while True:
        # maybe we should try to find some way to do this in a rolling fashion
        in_bytes = process1.stdout.read(samplerate * 2 * 3)
        if not in_bytes:
            break
        do_decoding(np.frombuffer(in_bytes, dtype='<i2'))

        print("time", time.time() - timee)
        timee = time.time()

    process1.wait()
