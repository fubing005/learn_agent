from collections.abc import AsyncIterable, Iterable
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
from io import BytesIO
import base64

app = FastAPI()

# 使用 yield 的 StreamingResponse
message = """
Rick: (stumbles in drunkenly, and turns on the lights) Morty! You gotta come on. You got--... you gotta come with me.
Morty: (rubs his eyes) What, Rick? What's going on?
Rick: I got a surprise for you, Morty.
Morty: It's the middle of the night. What are you talking about?
Rick: (spills alcohol on Morty's bed) Come on, I got a surprise for you. (drags Morty by the ankle) Come on, hurry up. (pulls Morty out of his bed and into the hall)
Morty: Ow! Ow! You're tugging me too hard!
Rick: We gotta go, gotta get outta here, come on. Got a surprise for you Morty.
"""
@app.get("/story/stream", response_class=StreamingResponse)
async def stream_story() -> AsyncIterable[str]:
    for line in message.splitlines():
        yield line + "\n"
        # await asyncio.sleep(0.1)  # 每隔0.1秒发送一行

@app.get("/story/stream-no-async", response_class=StreamingResponse)
def stream_story_no_async() -> Iterable[str]:
    for line in message.splitlines():
        yield line

@app.get("/story/stream-no-annotation", response_class=StreamingResponse)
async def stream_story_no_annotation():
    for line in message.splitlines():
        yield line

@app.get("/story/stream-no-async-no-annotation", response_class=StreamingResponse)
def stream_story_no_async_no_annotation():
    for line in message.splitlines():
        yield line

@app.get("/story/stream-bytes", response_class=StreamingResponse)
async def stream_story_bytes() -> AsyncIterable[bytes]:
    for line in message.splitlines():
        yield line.encode("utf-8")

@app.get("/story/stream-no-async-bytes", response_class=StreamingResponse)
def stream_story_no_async_bytes() -> Iterable[bytes]:
    for line in message.splitlines():
        yield line.encode("utf-8")

@app.get("/story/stream-no-annotation-bytes", response_class=StreamingResponse)
async def stream_story_no_annotation_bytes():
    for line in message.splitlines():
        yield line.encode("utf-8")

@app.get("/story/stream-no-async-no-annotation-bytes", response_class=StreamingResponse)
def stream_story_no_async_no_annotation_bytes():
    for line in message.splitlines():
        yield line.encode("utf-8")

# -----------------------------------------

# 自定义 PNGStreamingResponse
image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAB0AAAAdCAYAAABWk2cPAAAAbnpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjadYzRDYAwCET/mcIRDoq0jGOiJm7g+NJK0vjhS4DjIEfHfZ20DKqSrrWZmyFQV5ctRMOLACxglNCcXk7zVqFzJzF8kV6R5vOJ97yVH78HjfYAtg0ged033ZgAAAoCaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/Pgo8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICBleGlmOlBpeGVsWERpbWVuc2lvbj0iMjkiCiAgIGV4aWY6UGl4ZWxZRGltZW5zaW9uPSIyOSIKICAgdGlmZjpJbWFnZVdpZHRoPSIyOSIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMjkiCiAgIHRpZmY6T3JpZW50YXRpb249IjEiLz4KIDwvcmRmOlJERj4KPC94OnhtcG1ldGE+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAKPD94cGFja2V0IGVuZD0idyI/PnQkBZAAAAAEc0JJVAgICAh8CGSIAAABoklEQVRIx8VXwY7FIAjE5iXWU+P/f6RHPNW9LIaOoHYP+0yMShVkwNGG1lqjfy4HfaF0oyEEt+oSQqBaa//m9Wd6PlqhhbRMDiEQM3e59FNKw5qZHpnQfuPaW6lazsztvu/eElFj5j63lNLlMz2ttbZtVMu1MTGo5Sujn93gMzOllKiUQjHGB9QxxneZhJ5iwZ1rL2fwenoGeL0q3wVGhBPHMz0PeFccIfASEeWcO8xEROd50q6eAV6s1s5XXoncas1EKqVQznnwUBdJJmm1l3hmmdlOMrGO8Vl5gZ56Y0y8IZF0BuqkQWM4B6HXrRCKa1SEqyzEo7KK59RT/VHDjX3ZvSefeW3CO6O6vsiA1NrwVkxxAcYTCcHyTjZmJd00pugBQoTnzjvn+kzLBh9GtRDjhleZFwbx3kugP3GvFzdkqRlbDYw0u/HxKjuOw2QxZCGL5V5f4l7cd6qsffUa1DcLM9N1XcTMvep5ul1e4jNPtZfWGIkE6dI8MquXg/dS2CGVJQ2ushd5GmlxFdOw+1tRa32MY4zDQ9yaZ60J3/iX+QG4U3qGrFHmswAAAABJRU5ErkJggg=="
binary_image = base64.b64decode(image_base64)

def read_image() -> BytesIO:
    return BytesIO(binary_image)

class PNGStreamingResponse(StreamingResponse):
    media_type = "image/png"

@app.get("/image/stream", response_class=PNGStreamingResponse)
async def stream_image() -> AsyncIterable[bytes]:
    with read_image() as image_file:
        for chunk in image_file:
            yield chunk

@app.get("/image/stream-no-async", response_class=PNGStreamingResponse)
def stream_image_no_async() -> Iterable[bytes]:
    with read_image() as image_file:
        for chunk in image_file:
            yield chunk

@app.get("/image/stream-no-async-yield-from", response_class=PNGStreamingResponse)
def stream_image_no_async_yield_from() -> Iterable[bytes]:
    with read_image() as image_file:
        yield from image_file

@app.get("/image/stream-no-annotation", response_class=PNGStreamingResponse)
async def stream_image_no_annotation():
    with read_image() as image_file:
        for chunk in image_file:
            yield chunk

@app.get("/image/stream-no-async-no-annotation", response_class=PNGStreamingResponse)
def stream_image_no_async_no_annotation():
    with read_image() as image_file:
        for chunk in image_file:
            yield chunk


