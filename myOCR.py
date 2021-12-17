from PIL import ImageDraw
import pickle

chosen_pixels = [
[[23, 228], [60, 210], [96, 229], [90, 295], [60, 326], [40, 295], [60, 261]],
[[143, 226],[164, 190],[193, 227],[186, 295],[153, 326],[130, 294],[161, 261]],
[[250, 222],[280, 194],[301, 228],[297, 289],[268, 323],[242, 294],[272, 259]],
[[342, 225],[369, 195],[394, 225],[393, 290],[364, 320],[339, 286],[367, 257]],
[[436, 215],[464, 191],[490, 216],[490, 281],[462, 317],[434, 282],[462, 253]],
]

power_pixel = [20, 200]

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
    try:
        with open('OCR calibration.data', 'rb') as file_handle:
            chosen_pixels = pickle.load(file_handle)
    except FileNotFoundError:
        print('OCR calibration file not found, new file created with default values')
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
            if img.getpixel(tuple(chosen_pixels[i][j])) == 255:
                # if segment is vertical
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
                    print(i, j)
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
    digits=0
    # if scale is off, return none
    if img.getpixel((power_pixel[0], power_pixel[1])) == 0:
        return "off"
    for i in range(5):
        segments = [0,0,0,0,0,0,0]
        for j in range(7):
            pixel_value = img.getpixel(tuple(chosen_pixels[i][j]))
            if i == 0 and not (j == 2 or j == 3) and pixel_value == 0:
                print("calibrating")
#                 calibrate(img)
                return "calibrated"
            segments[j] = 1 if pixel_value == 0 else 0
        digit = workout_digit(segments)
        if digit is None:
            return "NaN"
        digits += digit * 10**(4-i)
    return digits

setup()