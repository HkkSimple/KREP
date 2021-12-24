from glob import glob
import os
import shutil

img_path = glob('/mnt/data/rz/data/idCard/v1/images/*.*')

for imgp in img_path:
	# dst_path = imgp.replace('png', 'jpg')
	dst_path = imgp.split('.')[0]+'.jpg'
	os.rename(imgp, dst_path)
