# 对真实数据进行字段切分
import json
from glob import glob
import os.path as osp
import os
import re
from tqdm import tqdm
from pprint import pprint
import shutil
import matplotlib.pyplot as plt
import cv2
from time import time
import numpy as np


# 提取百度的识别结果
baidu_file_root = '/mnt/data/rz/data/idCard/v5/baiduLabel'
img_root= '/mnt/data/rz/data/idCard/v5/images'


def baidu_parse(path):
    result = list()
    with open(path) as f:
        for line in f.readlines():
            line = line.strip().split(',')
            loc = line[:8]
            loc = list(map(int, loc))
            ct = line[8]
            cls = line[9]
            tmp = {'cls': cls, 'ct': ct,  'loc': loc}
            result.append(tmp)
    return result


def cut_img(img, item):
    loc = item['loc']
    X = [loc[0], loc[2], loc[4], loc[6]]
    Y = [loc[1], loc[3], loc[5], loc[7]]
    minx, maxx = min(X), max(X)
    miny, maxy = min(Y), max(Y)
    x1, y1, x2, y2 = minx, miny, maxx, maxy
    item_img = img[y1:y2, x1:x2, :]
    shape = item_img.shape
    min_size = min(shape[:2])
    if min_size == 0:
        print(loc)
        return None
    return item_img



class_names = ('name', 'sex', 'birthday', 'address', 'number', 'authority', 'validity', 'nation')
baidu_paths = glob(osp.join(baidu_file_root, '*.txt'))
cutted_img_store_root = '/mnt/data/rz/data/idCard/v5/rec/baiduCut/baiduCutImages'
cutted_address_img_store_root = '/mnt/data/rz/data/idCard/v5/rec/address/images'
if not os.path.exists(cutted_img_store_root):
    os.makedirs(cutted_img_store_root)
if not os.path.exists(cutted_address_img_store_root):
    os.makedirs(cutted_address_img_store_root)
cutted_address_txt_store_path = '/mnt/data/rz/data/idCard/v5/rec/address/baiduLabels.txt'
cutted_label_store_path = '/mnt/data/rz/data/idCard/v5/rec/baiduCut/baiduLabels.txt'
label_lines = []
address_lines = []
for txtp in tqdm(baidu_paths):
    txtn = osp.basename(txtp)
    imgn = txtn.replace('txt', '') + 'jpg'
    imgp = osp.join(img_root, imgn)
    bresult = baidu_parse(txtp)
    img = cv2.imread(imgp)
    for item in bresult:
        cls, ct, loc = item['cls'], item['ct'], item['loc']
        cutted_img = cut_img(img, item)
        cutted_imgn = str(int(time()*1000000)) + '.jpg'
        cutted_imgp = osp.join(cutted_img_store_root, cutted_imgn)
        if cutted_img is None:
            continue
        if cls == 'validity':
            if len(ct) == 8:
                ct = ct[:4] + '.' + ct[4:6] + '.' + ct[6:8]
        if cls == 'birthday':
            if len(ct) == 8:
                ct = ct[:4] + '年' + ct[4:6] + '月' + ct[6:8] + '日'
        if cls == 'address':
            line = imgn + '\t' + ct
            address_lines.append(line)
            cv2.imwrite(osp.join(cutted_address_img_store_root, imgn), cutted_img)
            continue
        cv2.imwrite(cutted_imgp, cutted_img)
        # line = 'baiduCutImages/' + cutted_imgn + '\t' + ct
        line = cutted_imgn + '\t' + ct
        label_lines.append(line)

with open(cutted_label_store_path, 'w') as f:
    f.write('\n'.join(label_lines))

with open(cutted_address_txt_store_path, 'w') as f:
    f.write('\n'.join(address_lines))