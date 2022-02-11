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


def base64_to_image(base64_str, channel=1):
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    if channel == 1:
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if channel == 3:
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def path_image_to_base64(img_path):
    with open(img_path, 'rb') as f:
        base64_bytes = base64.b64encode(f.read())
    return base64_bytes.decode()

def image_to_base64(arr):
    retval, buffer = cv2.imencode('.jpg', arr)
    arr_str = base64.b64encode(buffer)
    arr_str = arr_str.decode()
    return arr_str


def request_by_image(url, headers, param):
    result = requests.post(url, files=param).json()
    return result



def get_custom_idcard_content(url, imgn, img):
    
    headers = {"Content-Type": 'application/json;charset=UTF-8'}
    # img_paths = glob('/mnt/data/rz/data/idCard/v5/images/*.jpg')

    base64_bytes = image_to_base64(img)
    param = {"imageData": base64_bytes,
            "imageUUID": imgn}
    result = requests.post(url, headers=headers, data=json.dumps(param))
    result = result.json()
    return result