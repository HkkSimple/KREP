from glob import glob
import os
import shutil

img_path = glob('/mnt/data/rz/data/register/exp/det/20211014/exp/images/train/*.png')

for imgp in img_path:
	dst_path = imgp.replace('png', 'jpg')
	os.rename(imgp, dst_path)
