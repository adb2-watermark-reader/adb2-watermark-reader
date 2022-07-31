# ADB2 Audio/Video Watermarks Reader

This repository implements the `ETSI TS 103 464 V1.3.1` specification.

It was built as a student project and is not optimized for use in production.

[Our paper is available here.](documentation/paper.pdf)


## How to install

- install [poetry](https://python-poetry.org/docs/)
- clone this repository
- run `poetry install` in this directory

### Choose your input source

We support all input formats supported by FFmpeg, including file input in all common formats like MP4, TS, MKV,...

Additionally, we support live input from different sources including tcp streams with a looped video or shared screens.

We successfully tried screen sharing with [OBS](https://obsproject.com/) with [OBS-RTSPServer](https://github.com/iamscottxu/obs-rtspserver).

For use with looped video we used the command
```
ffmpeg -stream_loop -1 -i "sample_videos/sample_1.ts" -f mpegts -c:a copy -c:v copy tcp://0.0.0.0:1234?listen
```

You need to edit `main.py` in the `src` directory and comment in the correct line.

After that run `poetry run python main.py` in the `src` directory and it will show the detected watermark.
