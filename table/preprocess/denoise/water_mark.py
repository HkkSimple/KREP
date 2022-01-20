from asyncio.unix_events import BaseChildWatcher
from itertools import product
from PIL import Image
import numpy as np

def remove_water_mark(img, water_color, background_color) -> np.ndarray:
    color_thresh = int(sum(water_color) * 0.9)
    if type(img) is np.ndarray:
        img = Image.fromarray(img)
    width, height = img.size
    for pos in product(range(width), range(height)):
        if sum(img.getpixel(pos)[:3]) > color_thresh:
            img.putpixel(pos, background_color)
    return np.array(img)