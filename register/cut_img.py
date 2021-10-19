from glob import glob 
import numpy as np
import os.path as osp
import os
import shutil
import cv2
from time import time
from tqdm import tqdm

root = '/mnt/data/rz/data/register/v2'
img_extend = '.jpg'

txt_paths = glob(osp.join(root, 'icdar_format_label', '*.txt'))
img_root = osp.join(root, 'images')
cut_img_store_root = osp.join(root,'cut_img')
if not osp.exists(cut_img_store_root):
	os.makedirs(cut_img_store_root)
	


for txtp in tqdm(txt_paths):
	txtn = osp.basename(txtp)
	suffix = txtn.split('.')[0]
	imgn = suffix + img_extend
	imgp = osp.join(img_root, imgn)
	img = cv2.imread(imgp)

	with open(txtp) as f:
		for line in f:
			loc = line.split(',')[:8]
			loc = list(map(int, loc))
			x1, y1, x2, y2, x3, y3, x4, y4 = loc
			cuted = img[y1:y3, x1:x3, :]

			cut_img_name = str(int(time()*1000000)) + '.jpg'
			img_store_path = osp.join(cut_img_store_root, cut_img_name)
			cv2.imwrite(img_store_path, cuted)