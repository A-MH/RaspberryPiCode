from PIL import ImageDraw

chosen_pixels = (
((20, 202), (20, 202), (110, 228), (101, 294), (20, 201), (20, 202), (20, 202)),
((153, 226),(184, 200),(208, 227),(201, 295),(168, 326),(145, 294),(176, 261)),
((249, 227),(277, 197),(301, 228),(297, 289),(268, 323),(242, 294),(272, 259)),
((342, 225),(369, 195),(394, 225),(393, 290),(364, 320),(339, 286),(367, 257)),
((436, 215),(464, 191),(490, 216),(490, 281),(462, 317),(434, 282),(462, 253)),
)


# chosen_pixels = (
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
# ((0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)),
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
[1,1,1,1,1,0,1],
[0,0,0,0,0,0,0]]

def show_boxes(img):
    Drawer = ImageDraw.Draw(img)
    print("h")
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
        if digit == None:
#             print(f"segment {i}: {segments}")
            return None
        digits += digit * 10**(4-i)
    return digits
