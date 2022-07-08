import subprocess as sp
import threading

import audio_decoder
import video_decoder

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
        'ffmpeg -hide_banner -loglevel panic '  # Set loglevel to error for disabling the prints ot stderr
        # '-rtsp_transport tcp '              # needed when using obs over rtsp
        f'-i "{in_filename}" '
        '-vcodec rawvideo -pix_fmt rgb24 '  # Raw video codec with rgb24 pixel format                               
        '-map 0:v -f:v rawvideo pipe:2 '  # rawvideo format is mapped to stderr pipe
        f'-acodec pcm_s16le -ar {samplerate} -ac 1 '  # Audio codec pcm_s16le (-ar 16k has no affect)
        '-map 0:a -f:a s16le pipe:1 '  # s16le audio format is mapped to stdout pipe
        # '-report'  # Create a log file (because we can't the statuses that are usually printed to stderr).
        , stdout=sp.PIPE, stderr=sp.PIPE, shell=True)

    threading.Thread(target=audio_decoder.handle_audio_pipe, args=(process.stdout, samplerate)).start()
    threading.Thread(target=video_decoder.handle_video_pipe, args=(process.stderr, video_resolution)).start()
