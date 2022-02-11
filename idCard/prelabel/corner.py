import base64
from io import BytesIO
import numpy as np
import cv2
import requests
import json
import pickle as cpk
from util import corner_point_transform

def request_api(url, header, params):
    response = requests.post(url, headers=header, data=json.dumps(params))
    response = response.json()
    return response

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


def get_cornered_img(url, img):
    headers = {"Content-Type": 'application/json;charset=UTF-8'}
    corner_points = []
    result = get_request_result(img, url, headers)
    res_data = result.get('responseData', None)
    if res_data is not None:
        clses = res_data.get('class_name', [])
        if len(clses) == 4:
            locs = res_data['location']
            locs = base64_to_array(locs)
            for lc in locs:
                x1, y1, x2, y2, x3, y3, x4, y4 = lc
                cx = (x1 + x3) / 2  # 将角点检测框都转成框的中心点，从而变成图片角点
                cy = (y1 + y3) / 2
                corner_points.append([cx, cy])
        if len(corner_points) == 4:
            img = corner_point_transform(img, np.array(corner_points))
            return img
    return None