from itertools import product
from PIL import Image

img = Image.open('/mnt/data/rz/programe/table/preprocess/data/img/test/w1.jpg')
width, height = img.size
for pos in product(range(width), range(height)):
    if sum(img.getpixel(pos)[:3]) > 600:
        img.putpixel(pos, (255,255,255))
img.save('removed_1.png')