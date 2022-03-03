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
from pprint import pprint
import pickle as cpk
from concurrent import futures
import shutil

def request_api(url, header, params):
    response = requests.post(url, headers=header, data=json.dumps(params))
    response = response.json()
    return response

def draw_text_det_res(dt_boxes, img_path):
    src_im = cv2.imread(img_path)
    for box in dt_boxes:
        box = np.array(box).astype(np.int32).reshape(-1, 2)
        cv2.polylines(src_im, [box], True, color=(255, 255, 0), thickness=2)
    return src_im

def base64_to_image(base64_str, channel=1):
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

def base64_to_array(base64_str):
    img_data = base64.b64decode(base64_str)
    arr = cpk.loads(img_data)
    return arr

def pil_to_byte(img):
    buffered = BytesIO()
    img.save(buffered, format=img.format)
    return buffered.getvalue()

def data_process(img):
    base64_bytes = array_to_base64(img)
    param = {"imageData": base64_bytes,
            "imageUUID": 'AI-TEST-CLIENT'}
    return param

def get_request_result(data, url, headers):
    param = data_process(data)
    rst = request_api(url, headers, param)
    return rst


if __name__ == "__main__":
    url = "http://127.0.0.1:30301/DB"
    root = '/mnt/data/rz/data/IE/invoice/template'
    txt_store_root = os.path.join(root, 'labels')
    if not os.path.exists(txt_store_root):
        os.makedirs(txt_store_root)

    app_name = 'ASP-MODEL-DB'
    headers = {"Content-Type": 'application/json;charset=UTF-8'}
    img_paths = glob(os.path.join(root, 'images/*.png'))
    drawed = True
    store_txt = True
    cut = False

    for imgp in tqdm(img_paths):
        img = cv2.imread(imgp)
        imgn = os.path.basename(imgp)
        suffix = imgn.split('.')[0]
        result = get_request_result(img, url, headers)
        # print('demo server result is:', result)

        loc = result['responseData']['location']
        loc = base64_to_array(loc)
        loc = loc.astype('int')

        if cut:
            points = loc.reshape((-1, 8))
            points = points[:, [0, 1, 4, 5]]
            for pt in points:
                x1, y1, x2, y2 = pt
                cutted_img = img[y1:y2, x1:x2, :]
                shape = cutted_img.shape
                if min(shape) == 0:
                    continue
                cutted_path = str(int(time()*1000000))+'.jpg'
                cv2.imwrite(cutted_path, cutted_img)
        if drawed:
            drawed_img = draw_text_det_res(loc, imgp)
            img_name = os.path.basename(imgp)
            cv2.imwrite('./drawed_{}'.format(img_name), drawed_img)
        
        if store_txt:
            h, w = img.shape[:2]
            img_name = os.path.basename(imgp)
            txt_name = suffix + '.txt'
            txt_store_path = os.path.join(txt_store_root, txt_name)
            loc = loc.reshape((-1, 8))
            lines = []
            for lc in loc:
                lc = map(str, lc)
                ct = '###'
                cls = 'other'
                line = ','.join(lc) + ',' + ct + ',' + cls
                lines.append(line)
            with open(txt_store_path, 'w') as f:
                f.write('\n'.join(lines))