from PIL import Image
from PIL.ExifTags import TAGS
img = Image.open('/home/pi/Robot/camera/test.jpg')
exif_data = img._getexif()
for tag, value in exif_data.items():
  print(TAGS.get(tag, tag), value)