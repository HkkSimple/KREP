import shutil
import os
from glob import glob
from tqdm import tqdm


def split_dir(root, store_root, num):
	paths = glob(os.path.join(root, '*'))
	total_num = len(paths)
	package = 0
	for begin in range(0, total_num, num):
		store_package = os.path.join(store_root, str(package))
		if not os.path.exists(store_package):
			os.makedirs(store_package)
		end = begin+num if begin+num < total_num else total_num
		for p in paths[begin:end]:
			shutil.copy(p, store_package)
		package += 1


if __name__ == '__main__':
	img_root = '/mnt/data/rz/data/store/20211207/images'
	store_root = '/mnt/data/rz/data/store/20211207/split'
	if not os.path.exists(store_root):
		os.makedirs(store_root)
	num = 100
	split_dir(img_root, store_root, num)