from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
import sys

# Create the in-memory stream
stream = BytesIO()
camera = PiCamera()
camera.resolution = (640, 480)
camera.rotation = 180
camera.start_preview(fullscreen=False, window=(0, 0, 640, 480))
sleep(2)
counter = 0
while counter < 1:
    stream.seek(0)
    stream.truncate(0)
    camera.capture(stream, format='jpeg', resize=(640, 480), use_video_port = True)
    img = Image.open(stream)
    img.show()
    counter= counter+1
print('done')
# "Rewind" the stream to the beginning so we can read its content
#stream.seek(0)
#image = Image.open(stream)