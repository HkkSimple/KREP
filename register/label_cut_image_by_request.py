import base64
import cv2
import requests
import json
from glob import glob
from tqdm import tqdm
import os

def request_api(url, header, params):
    response = requests.post(url, headers=header, data=json.dumps(params))
    response = response.json()
    return response

def array_to_base64(arr):
    retval, buffer = cv2.imencode('.jpg', arr)
    arr_str = base64.b64encode(buffer)
    arr_str = arr_str.decode()
    return arr_str

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
    url = "http://127.0.0.1:30103/ocr/crnn"
    service = '/crnn'
    headers = {"Content-Type": 'application/json;charset=UTF-8'}

    rec_results = {}
    img_paths = glob(os.path.join('/mnt/data/rz/data/register/v2/cut_img/*.jpg'))
    txt_store_path = '/mnt/data/rz/data/register/v2/pre_cut_img_label.txt'
    for imgp in tqdm(img_paths):
        img = cv2.imread(imgp)
        imgn = os.path.basename(imgp)
        result = get_request_result(img, url, headers)
        ct = result['responseData']['content']
        rec_results[imgn] = ct

    with open(txt_store_path, 'w') as f:
        f.write('\n'.join(imgn + '\t' + ct for imgn, ct in rec_results.items()))
