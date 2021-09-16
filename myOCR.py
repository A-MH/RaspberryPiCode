from PIL import ImageDraw
import pickle

chosen_pixels = [
[[20, 200], [55, 228], [111, 229], [102, 295], [55, 228], [55, 228], [55, 228]],
[[153, 226],[184, 200],[208, 227],[201, 295],[168, 326],[145, 294],[176, 261]],
[[254, 222],[280, 194],[301, 228],[297, 289],[268, 323],[242, 294],[272, 259]],
[[342, 225],[369, 195],[394, 225],[393, 290],[364, 320],[339, 286],[367, 257]],
[[436, 215],[464, 191],[490, 216],[490, 281],[462, 317],[434, 282],[462, 253]],
]

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

def calibrate(img):
    for i in range(5):
        for j in range(7):
            if not (i == 0 and j == 0):
                # if chosen pixel is black, it means we are inside the segment
                if img.getpixel(tuple(chosen_pixels[i][j])) == 0:
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
                else:
                    print("ocr needs manual calibration")
                    return
    with open('OCR calibration.data', 'wb') as file_handle:
        # store the data as binary data stream
        pickle.dump(chosen_pixels, file_handle)
                        
def read_scale(img):
    global chosen_pixels
    digits=0
    try:
        with open('OCR calibration.data', 'rb') as file_handle:
            chosen_pixels = pickle.load(file_handle)
    except FileNotFoundError:
        print('OCR calibration file not found, using default values')
    for i in range(5):
        segments = [0,0,0,0,0,0,0]
        for j in range(7):
            segments[j] = 1 if img.getpixel(tuple(chosen_pixels[i][j])) == 0 else 0
            if i == 0:
                if j == 0 and segments[j] == 1:
                    print ("error: scale seems to be off")
                    return None
                elif j == 1 and segments[j] == 1:
                    calibrate(img)
                    print ("ocr calibrated")
                    return None
#         print(segments)
        digit = workout_digit(segments)
        if digit is None:
            return None
        digits += digit * 10**(4-i)
    return digits

