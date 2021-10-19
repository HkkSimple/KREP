import os
import cv2
from tqdm import tqdm
from pdf2image import convert_from_path, convert_from_bytes
from time import time
from glob import glob


def convert(path):
    images = convert_from_path(path)
    return images

def register_pdf_convert():
	store_root = '/mnt/data/rz/project/register/register_main'
	pdf_paths = glob('02/*.pdf')
	if not os.path.exists(store_root):
		os.makedirs(store_root)
	for pdf_path in tqdm(pdf_paths):
		images = convert(pdf_path)
		name = os.path.basename(pdf_path).split('.')[0] + '.jpg'
		img_store_path = os.path.join(store_root, name)
		for img in images:
			img.save(img_store_path)


def pdf_convert():
	# store_root = '/mnt/data/rz/data/register/origin/v6/images'
	# pdf_root = '/mnt/data/rz/data/register/origin/v6/pdf'
	store_root = '../data/'
	pdf_root = '../data'

	pdf_paths = glob(os.path.join(pdf_root, '*.pdf'))
	if not os.path.exists(store_root):
		os.makedirs(store_root)
	i = 1
	for pdf_path in tqdm(pdf_paths):
		images = convert(pdf_path)
		for img in images:
			# t = str(int(time()*10000000))
			t = str(i)
			name = '{}.jpg'.format(t)
			store_path = os.path.join(store_root, name)
			img.save(store_path)
			i += 1

if __name__ == "__main__":
	pdf_convert()
