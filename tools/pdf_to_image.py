import os
import cv2
from tqdm import tqdm
from pdf2image import convert_from_path, convert_from_bytes
from time import time


def convert(path):
    images = convert_from_path(path)
    return images


if __name__ == "__main__":
	pdf_path = '/mnt/data/rz/data/register/20210731/20210731.pdf'
	store_root = '/mnt/data/rz/data/register/20210731/images'
	if not os.path.exists(store_root):
		os.makedirs(store_root)
	images = convert(pdf_path)
	for img in tqdm(images):
		t = str(int(time()*10000000))
		name = '{}.png'.format(t)
		store_path = os.path.join(store_root, name)
		img.save(store_path)
