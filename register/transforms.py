from PIL import Image, ImageDraw
import random


# 对识别的图片数据随机画横线
def random_plot_line(imgp, random_scale, color, line_width):
	im = Image.open(imgp)
	draw = ImageDraw.Draw(im)
	w, h = im.size
	random_y = random.randint(0, h)
	x1, y1, x2, y2 = 0, random_y, w, random_y

	draw.line((x1, y1, x2, y2), fill=color, width=line_width)

	return im


# 登记证真实数据随机划线划线
def plot_images_line():
	img_paths = glob('')