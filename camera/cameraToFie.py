from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (640, 480)
camera.rotation = 180
camera.start_preview()
# Camera warm-up time
sleep(5)
camera.capture('test2.jpg', use_video_port=True, resize=(640,480))