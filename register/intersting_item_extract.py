import random
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import requests
import json
from glob import glob
from multiprocessing import Pool
from time import time
from tqdm import tqdm
import os
import os.path as osp
from pprint import pprint
import pickle as cpk
from concurrent import futures
import shutil



def base64_to_image(base64_str, channel=3):
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    if channel == 1:
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if channel == 3:
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def image_to_base64(img_path):
    with open(img_path, 'rb') as f:
        base64_bytes = base64.b64encode(f.read())
    return base64_bytes.decode()

def array_to_base64(arr):
    retval, buffer = cv2.imencode('.jpg', arr)
    arr_str = base64.b64encode(buffer)
    arr_str = arr_str.decode()
    return arr_str

# 通过检测模型，提取感兴趣类别字段的图片，并将图片存储到本地
def extract_item():
    url = "http://127.0.0.1:30102/ocr/register/detect/test"
    headers = {"Content-Type": 'application/json;charset=UTF-8'}

    thres = 0.55
    extract_item_class_name = ['idCard', 'frame_number', 'registration_number', 'number']

    img_root = '/mnt/data/rz/data/register/origin/v6/person'
    img_paths = glob(osp.join(img_root, '*'))
    store_root = '/mnt/data/rz/data/register/clean/rec/v6'
    for name in extract_item_class_name:
        store_dir = osp.join(store_root, name)
        if not osp.exists(store_dir):
            os.makedirs(store_dir)

    for imgp in tqdm(img_paths):
        img = cv2.imread(imgp)
        base64_bytes = array_to_base64(img)
        params = {"imageData": base64_bytes}
        response = requests.post(url, headers=headers, data=json.dumps(params))
        response = response.json()
        data = response.get('responseData', None)
        if data is not None and len(data) > 0:
            for item in data:
                category = item['category']
                location = item['location']
                score = item['scores']
                if score < thres:
                    continue
                if category in extract_item_class_name:
                    store_img_dir = osp.join(store_root, category)
                    x1, y1, x2, y2 = list(map(int, location))
                    cuted = img[y1:y2, x1:x2, :]
                    t = str(int(time()*1000000)) + '.jpg'
                    cv2.imwrite(osp.join(store_img_dir, t), cuted)

#把不同情况的图片区分开来
def select_person_company_cover():
    url = "http://127.0.0.1:30100/ocr/register"
    headers = {"Content-Type": 'application/json;charset=UTF-8'}
    img_root = '/mnt/data/rz/data/register/origin/v6/images'
    paths = glob(os.path.join(img_root, '*'))

    store_root = '/mnt/data/rz/data/register/origin/v6/'
    person_dir_name = 'person'
    company_dir_name = 'company'
    cover_dir_name = 'cover'

    for imgp in tqdm(paths):
        file = image_to_base64(imgp)
        param = {"imageData": file,
                "imageUUID": 'test-uuid',
                "fileType": 'img'}
        result = requests.post(url, headers, files=param).json()
        res_code = result['responseCode']
        res_data = result['responseData']
        # 默认会将图移到公司文件夹中，如果如确其实封面或者是个人，那就将其移到对应文件夹中
        img_store_root = osp.join(store_root, company_dir_name) 
        if res_code == '0000' and len(res_data) > 0:
            for item in res_data:
                category =item['category']
                if 'person' in category:
                    img_store_root = osp.join(store_root, person_dir_name)
                    break
                if 'company' in category:
                    img_store_root = osp.join(store_root, company_dir_name)
                    break
                if 'cover' in category:
                    img_store_root = osp.join(store_root, cover_dir_name)
                    break
        if not osp.exists(img_store_root):
            os.makedirs(img_store_root)
        shutil.copy(imgp, img_store_root)

#对切分成小图的字段图片进行ocr识别
def recognize_item_img():
    url = "http://127.0.0.1:30104/ocr/register/crnn"
    url_ = "http://127.0.0.1:30103/ocr/crnn"
    headers = {"Content-Type": 'application/json;charset=UTF-8'}
    root = '/mnt/data/rz/data/register/clean/rec/v6'
    for name in ['frame_number', 'idCard', 'number', 'registration_number']:
        img_root = osp.join(root, name, 'images')
        img_paths = glob(osp.join(img_root, '*.jpg'))
        txt_store_path = osp.join(root, name, 'pre_labels.txt')

        results = dict()
        if name == 'registration_number':
            url = url_
        for imgp in tqdm(img_paths):
            img = cv2.imread(imgp)
            imgn = osp.basename(imgp)
            base64_bytes = array_to_base64(img)
            param = {"imageData": base64_bytes,
                    "imageUUID": 'AI-TEST-CLIENT'}
            response = requests.post(url, headers=headers, data=json.dumps(param))
            response = response.json()
            ct = response['responseData']['content']
            results[imgn] = ct


        with open(txt_store_path, 'w') as f:
            f.write('\n'.join(imgn + '\t' + ct for imgn, ct in results.items()))

if __name__ == "__main__":
    recognize_item_img()
