from glob import glob
import os
import shutil
from time import time

root = '/mnt/data/rz/data/invoice/v2/images/val'
img_path = glob(os.path.join(root, '*.*'))

for imgp in img_path:

	# dst_path = imgp.replace('png', 'jpg')
	imgn = str(int(time()*1000000)) + '.jpg'
	dst_imgp = os.path.join(root, imgn)
	# dst_path = imgp.split('.')[0]+'.jpg'
	os.rename(imgp, dst_imgp)
