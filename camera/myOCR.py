from PIL import ImageDraw

chosen_pixels = (
((32, 202), (32, 202), (126, 220), (115, 285), (32, 201), (32, 202), (32, 202)),
((117, 223),(150, 189),(176,223),(167, 292),(132, 323),(105, 292),(142, 254)),
((221, 219),(254, 185),(279, 219),(271, 288),(241, 317),(214, 288),(246, 251)),
((322, 219),(350, 185),(375, 217),(371, 288),(342, 317),(319, 288),(347, 251)),
((418, 219),(446, 186),(471, 217),(467, 288),(439, 315),(415, 288),(444, 249))
)

chosen_pixels = (
((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
((260, 217),(287, 190),(311, 219),(306, 281),(277, 311),(253, 281),(282, 249)),
((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0))
)

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
[1,1,1,1,0,0,1]]

def show_boxes(img):
    Drawer = ImageDraw.Draw(img)
    for i in range(5):
        for j in range(7):
            rectangle = (chosen_pixels[i][j][0] - 2, chosen_pixels[i][j][1] - 2, chosen_pixels[i][j][0] + 2, chosen_pixels[i][j][1] + 2)
            Drawer.rectangle(rectangle, outline=1, fill=0)

def workout_digit(segments):
    for i in range(10):
        if segments == digits_array[i]:
            return i
    return 9;

def get_weight(img):
    digits=0
    for i in range(5):
        segments = [0,0,0,0,0,0,0]
        for j in range(7):
            segments[j] = 1 if img.getpixel(chosen_pixels[i][j]) == 0 else 0
        digits = digits + workout_digit(segments) * 10**(4-i)
    return digits
