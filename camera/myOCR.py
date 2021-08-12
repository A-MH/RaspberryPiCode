from PIL import ImageDraw

chosen_pixels = (
((20, 202), (20, 202), (105, 220), (95, 285), (20, 201), (20, 202), (20, 202)),
((149, 217),(180, 186),(204, 217),(196, 285),(163, 315),(140, 284),(173, 249)),
((247, 217),(276, 186),(300, 217),(295, 284),(263, 316),(240, 284),(270, 248)),
((341, 215),(369, 186),(394, 216),(392, 281),(364, 311),(337, 282),(365, 247)),
((436, 215),(464, 184),(490, 216),(490, 281),(462, 310),(434, 282),(462, 246)),
)

# chosen_pixels = (
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
# ((436, 215),(464, 184),(490, 216),(490, 281),(462, 310),(434, 282),(462, 246)),
# )

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
[1,1,1,1,0,0,1],
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

def get_weight(img):
    digits=0
    for i in range(5):
        segments = [0,0,0,0,0,0,0]
        for j in range(7):
            segments[j] = 1 if img.getpixel(chosen_pixels[i][j]) == 0 else 0
#         print(segments)
        digit = workout_digit(segments)
#         print(digit)
        if digit == None:
            return None
        digits += digit * 10**(4-i)
    return digits
