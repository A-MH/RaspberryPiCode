from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import myOCR as ocr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

weights = []
is_image_shown = False

def makeBW(x):
    thresh = 90
    return 1 if x > thresh else 0

def plot(array):
    plt.grid(axis='x', markevery=1)
    plt.grid(axis='y', markevery=1)
    x_axis = range(array.size)
    plt.plot(x_axis, array)
#     plt.plot(x_axis, diff_array, 'k', x_axis, avg_diff_array, 'y', x_axis, pid_output_array, 'c', x_axis, pid_p_array, 'r', x_axis, pid_i_array, 'g', x_axis, pid_d_array, 'b')
    plt.show()

def setup():
    global stream
    global camera
    # Create the in-memory stream
    stream = BytesIO()
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.rotation = 180
    camera.start_preview(fullscreen=False, window=(500, 500, 640, 480))
    sleep(2)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    print(camera.exposure_mode)
    camera.shutter_speed = 33000
    camera.exposure_compensation = 25
    camera.iso = 100
    camera.awb_gains = 1
    sleep(1)
    
def log_time(log):
    global old_time
    global time_log
    if __name__ == '__main__':
        if log == 'capture':
            time_log += f"image captured {(datetime.now() - old_time).seconds}.{(datetime.now() - old_time).microseconds}\n"
            old_time = datetime.now()
        elif log == 'process':
            time_log += f"image processed {(datetime.now() - old_time).seconds}.{(datetime.now() - old_time).microseconds}\n"
        elif log == 'read':
            time_log += f"digits read {(datetime.now() - old_time).seconds}.{(datetime.now() - old_time).microseconds}\n\n"
            old_time = datetime.now()
        old_time = datetime.now()

def show_image_and_boxes(img):
    global is_image_shown
    if not is_image_shown:
        is_image_shown = True
        ocr.show_boxes(img)
        img.show()

def get_weight():
    result = None
    old_result = None
    global stream
    global camera
    global old_time
    global image
    while True:
        old_time = datetime.now()
        stream.seek(0)
        stream.truncate(0)
        camera.capture(stream, format='jpeg', resize=(640, 480), use_video_port = True)
        stream.seek(0)
        img = Image.open(stream)
        log_time('capture')
        # image preproccessing
        img = img.convert('L').point(makeBW, mode='1')
    #     img = img.filter(ImageFilter.MaxFilter(size=1))
    #     img = img.filter(ImageFilter.MinFilter(size=1))
        log_time('process')
            
        result = ocr.read_scale(img)
        log_time('read')
        if isinstance(result, str):
            if result != old_result:
                print(f"result of scale is {result}")
        else:
            break
        old_result = result
    if __name__ == "__main__":
        show_image_and_boxes(img)
    result_gram = result/100
    return result_gram

setup()

if __name__ == "__main__":
    time_log = ""
    start_time = datetime.now()
    try:
        while True:
            print(get_weight())
    except KeyboardInterrupt:
        plot(weights)
    
