from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from time import sleep
import myOCR as ocr
from io import BytesIO
from picamera import PiCamera

def makeBW(x):
    thresh = 55
    return 255 if x > thresh else 0

# set up camera
camera = PiCamera()
camera.resolution = (640, 480)
# camera.shutter_speed = 1000
camera.rotation = 180
camera.start_preview(fullscreen=False, window=(0, 0, 640, 480))
sleep(5)
# camera.exposure_mode = 'backlight'
# Create the in-memory stream
stream = BytesIO()
camera.capture(stream, format='jpeg', resize=(640, 480), use_video_port = True)
# "Rewind" the stream to the beginning so we can read its content
stream.seek(0)
img = Image.open(stream)

# image preproccessing
img = img.convert('L').point(makeBW, mode='1')
# img = img.filter(ImageFilter.MaxFilter(size=1))
# img = img.filter(ImageFilter.MinFilter(size=1))

# to see what is happenning with the boxes, or to adjust, uncomment following line
# ocr.show_boxes(img)
img.show()
digits = ocr.get_weight(img)

weight = digits/100
print(weight)

