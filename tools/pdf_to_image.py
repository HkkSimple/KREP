import os
import cv2
from tqdm import tqdm
from pdf2image import convert_from_path, convert_from_bytes
from time import time


def convert(path):
    images = convert_from_path(path)
    return images


if __name__ == "__main__":
	pdf_path = '/home/user/rz/data/registration/100本产证扫描件.pdf'
	store_root = '/home/user/rz/data/registration/'
	images = convert(pdf_path)
	for img in tqdm(images):
		t = str(int(time()*10000000))
		name = '{}.jpg'.format(t)
		store_path = os.path.join(store_root, name)
		img.save(store_path)