import base64
import os
from io import BytesIO
import numpy as np
import cv2
import requests
import json
from time import time
import pickle as cpk
from glob import glob

from tqdm import tqdm


def request_api(url, header, params):
    response = requests.post(url, headers=header, data=json.dumps(params))
    response = response.json()
    return response


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
    param = {"image": base64_bytes}
    return param


def get_request_result(data, url, headers):
    param = data_process(data)
    rst = request_api(url, headers, param)
    return rst


def draw_text_det_res(dt_boxes, img_path):
    src_im = cv2.imread(img_path)
    for box in dt_boxes:
        if len(box) == 4:
            x1, y1, x2, y2 = box
            box = [x1, y1, x2, y1, x2, y2, x1, y2]
        box = np.array(box).astype(np.int32).reshape(-1, 2)
        cv2.polylines(src_im, [box], True, color=(255, 255, 0), thickness=2)
    return src_im


if __name__ == "__main__":
    # url = "http://127.0.0.1:30001/general/ocr"
    url = "http://47.98.153.185:64324/general/ocr"

    headers = {"Content-Type": 'application/json;charset=UTF-8'}
    img_paths = glob('data/address/images/*.jpg')
    draw = True

    with open('data/address/address_labels.txt') as f:
        address_baidu_result = dict()
        for line in f:
            imgn, ct = line.strip().split('\t')
            address_baidu_result[imgn] = ct


    for imgp in tqdm(img_paths):
        img = cv2.imread(imgp)
        t1 = time()

        base64_bytes = array_to_base64(img)
        params = {"image": base64_bytes}
        response = requests.post(url, headers=headers, data=json.dumps(params))
        response = response.json()
        
        res = response['response']
        imgn = os.path.basename(imgp)
        baidu_ct = address_baidu_result[imgn]
        if len(res) > 0:
            result = res[0]['details']['text2']
            locs = []
            contents = []
            for rs in result:
                loc = rs['regions']
                ct = rs['result']
                locs.append(loc)
                contents.append(ct)
            pre_address_ct = ''.join(contents)
            lines = []
            if len(baidu_ct) == len(pre_address_ct):
                idx = np.argsort([lc[1] for lc in locs])
                begin = 0
                end = 0
                for i in idx:
                    loc = locs[i]
                    ct = contents[i]
                    end = begin + len(ct)
                    bct = baidu_ct[begin:end]
                    begin += len(ct)

                    x1, y1, x2, y2 = loc
                    cut_img = img[y1:y2, x1:x2, :]
                    line = ','.join(map(str, [x1, y1, x2, y1, x2, y2, x1, y2])) + '\t' + bct
                    lines.append(line)
            txtn = imgn.replace('jpg', 'txt')
            txt_store_path = os.path.join('data/address/labels', txtn)
            if len(lines) > 0:
                with open(txt_store_path, 'w') as f:
                    f.write('\n'.join(lines))
            else:
                h, w = img.shape[:2]
                x1, y1, x2, y2, x3, y3, x4, y4 = 0, 0, w, 0, w, h, 0, h
                line = ','.join(map(str, [x1, y1, x2, y2, x3, y3, x4, y4])) + '\t' + baidu_ct
                with open(txt_store_path, 'w') as f:
                    f.write(line)
        else:
            h, w = img.shape[:2]
            x1, y1, x2, y2, x3, y3, x4, y4 = 0, 0, w, 0, w, h, 0, h
            line = ','.join(map(str, [x1, y1, x2, y2, x3, y3, x4, y4])) + '\t' + baidu_ct
            with open(txt_store_path, 'w') as f:
                f.write(line)