ffmpeg -stream_loop -1 -i video.ts -f mpegts -c:a copy -c:v copy tcp://0.0.0.0:1234?listen
