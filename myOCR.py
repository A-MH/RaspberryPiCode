from PIL import ImageDraw
import pickle
import RobotSpecific as rs

calibrate_mode = 'off'
power_pixel = [20, 150]

digits_array = [
[1,1,1,1,1,1,0],
[0,0,1,1,0,0,0],
[0,1,1,0,1,1,1],
[0,1,1,1,1,0,1],
[1,0,1,1,0,0,1],
[1,1,0,1,1,0,1],
[1,1,0,1,1,1,1],
[0,1,1,1,0,0,0],
[1,1,1,1,1,1,1],
[1,1,1,1,1,0,1],
[0,0,0,0,0,0,0]]

def setup():
    global chosen_pixels
    global calibrate_mode
    if calibrate_mode == "manual":
        print('manual calibration.')
        chosen_pixels = rs.chosen_pixels
        with open('OCR calibration.data', 'wb') as file_handle:
            # store the data as binary data stream
            pickle.dump(chosen_pixels, file_handle)
    else:
        try:
            with open('OCR calibration.data', 'rb') as file_handle:
                chosen_pixels = pickle.load(file_handle)
        except FileNotFoundError:
            print('OCR calibration file not found, new file created.')
            chosen_pixels = rs.chosen_pixels
            with open('OCR calibration.data', 'wb') as file_handle:
                # store the data as binary data stream
                pickle.dump(chosen_pixels, file_handle)
    

def show_boxes(img):
    Drawer = ImageDraw.Draw(img)
    for i in range(5):
        for j in range(7):
            rectangle = (chosen_pixels[i][j][0] - 2, chosen_pixels[i][j][1] - 2, chosen_pixels[i][j][0] + 2, chosen_pixels[i][j][1] + 2)
            Drawer.rectangle(rectangle, outline=1, fill=0)

def workout_digit(segments):
    digit = None
    for i in range(len(digits_array)):
        if segments == digits_array[i]:
            digit = i
    if digit == 10:
        return 0
    else:
        return digit;

# calibrate the chosen_pixels corrdinates
def calibrate(img):
    for i in range(5):
        for j in range(7):
            # if we are outside the segment, move the pixel to the inside                
            if img.getpixel(tuple(chosen_pixels[i][j])) == 1:
                # if segment is vertical
                print(f"digit: {i}, segment: {j}")
                if j == 0 or j == 2 or j == 3 or j == 5:
                    # work out the distance from left edge of segment to chosen pixel
                    distance = 1
                    left_limit_reached = False
                    right_limit_reached = False
                    left_pixel = None
                    right_pixel = None
                    while True:
                        # check for segment to the left
                        try:
                            left_pixel = img.getpixel((chosen_pixels[i][j][0] - distance, chosen_pixels[i][j][1]))
                        except:
                            left_limit_reached = True
                        if left_limit_reached == False and left_pixel == 0:
                            chosen_pixels[i][j][0] -= distance
                            break
                        # check for segment to the right
                        try:
                            right_pixel = img.getpixel((chosen_pixels[i][j][0] + distance, chosen_pixels[i][j][1]))
                        except:
                            right_limit_reached = True
                        if right_limit_reached == False and right_pixel == 0:
                            chosen_pixels[i][j][0] += distance
                            break
                        distance += 1
                # if segment is horizontal
                else:
                    # work out the distance from top edge of segment to chosen pixel
                    distance = 1
                    top_limit_reached = False
                    bottom_limit_reached = False
                    top_pixel = None
                    bottom_pixel = None
                    while True:
                        try:
                            # check for segment above
                            top_pixel = img.getpixel((chosen_pixels[i][j][0], chosen_pixels[i][j][1] - distance))
                        except:
                            top_limit_reached = True
                        if top_limit_reached == False and top_pixel == 0:
                            chosen_pixels[i][j][1] -= distance
                            break
                        try:
                            # check for segment below
                            bottom_pixel = img.getpixel((chosen_pixels[i][j][0], chosen_pixels[i][j][1] + distance))
                        except:
                            bottom_limit_reached = True
                        if bottom_limit_reached == False and bottom_pixel == 0:
                            chosen_pixels[i][j][1] += distance
                            break
                        distance += 1
            # next, centre the chosen pixel on the segment
            # work out the distance from left edge of segment to chosen pixel
            distance_left = 0
            while img.getpixel((chosen_pixels[i][j][0] - distance_left - 1, chosen_pixels[i][j][1])) == 0:
                distance_left += 1
            # work out the distance from right edge of segment to chosen pixel
            distance_right = 0
            while img.getpixel((chosen_pixels[i][j][0] + distance_right + 1, chosen_pixels[i][j][1])) == 0:
                distance_right += 1
            difference = distance_right - distance_left
            chosen_pixels[i][j][0] += round(difference/2)
            
            # work out the distance from top edge of segment to chosen pixel
            distance_top = 0
            while img.getpixel((chosen_pixels[i][j][0], chosen_pixels[i][j][1] - distance_top - 1)) == 0:
                distance_top += 1
            # work out the distance from right edge of segment to chosen pixel
            distance_bottom = 0
            while img.getpixel((chosen_pixels[i][j][0], chosen_pixels[i][j][1] + distance_bottom + 1)) == 0:
                distance_bottom += 1
            difference = distance_bottom - distance_top
            chosen_pixels[i][j][1] += round(difference/2)
    with open('OCR calibration.data', 'wb') as file_handle:
        # store the data as binary data stream
        pickle.dump(chosen_pixels, file_handle)
        print("ocr calibrated")
                        
def read_scale(img):
    global chosen_pixels
    global power_pixel
    global calibrate_mode
    digits=0
    # if scale is off, return none
    if img.getpixel((power_pixel[0], power_pixel[1])) == 0:
        return "off"
    for i in range(5):
        segments = [0,0,0,0,0,0,0]
        for j in range(7):
            pixel_value = img.getpixel(tuple(chosen_pixels[i][j]))
            segments[j] = 1 if pixel_value == 0 else 0
            if i==0 and j==5 and segments[j] == 1:
                while not (calibrate_mode == 'auto' or calibrate_mode == 'manual'):
                    calibrate_mode = input("enter calibration mode (auto/manual):")
                if calibrate_mode == 'auto':
                    calibrate(img)
        digit = workout_digit(segments)
        if digit is None:
            return "NaN"
        digits += digit * 10**(4-i)
    return digits

setup()