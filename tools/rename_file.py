from glob import glob
import os
import shutil

img_path = glob('/mnt/data/rz/data/register/val/images/*.jpg')

for imgp in img_path:
	dst_path = imgp.replace('jpg', 'png')
	os.rename(imgp, dst_path)