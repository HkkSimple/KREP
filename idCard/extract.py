import urllib
import copy
from matplotlib import pyplot as plt
import math
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


def draw_text_det_res(dt_boxes, img_path):
    if type(img_path) is str:
        src_im = cv2.imread(img_path)
    else:
        src_im = img_path
    for box in dt_boxes:
        box = np.array(box).astype(np.int32).reshape(-1, 2)
        cv2.polylines(src_im, [box], True, color=(255, 255, 0), thickness=2)
    return src_im


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


def request_api(url, header, params):
    response = requests.post(url, headers=header, data=json.dumps(params))
    response = response.json()
    return response

def data_process(img):
    base64_bytes = array_to_base64(img)
    param = {"imageData": base64_bytes,
             "imageUUID": 'AI-TEST-CLIENT'}
    return param


def get_request_result(data, url, headers):
    param = data_process(data)
    rst = request_api(url, headers, param)
    return rst


def rotate_bound(image, angle):
    '''
    . 旋转图片
    . @param image    opencv读取后的图像
    . @param angle    (顺)旋转角度
    '''

    (h, w) = image.shape[:2]  # 返回(高,宽,色彩通道数),此处取前两个值返回
    # 抓取旋转矩阵(应用角度的负值顺时针旋转)。参数1为旋转中心点;参数2为旋转角度,正的值表示逆时针旋转;参数3为各向同性的比例因子
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -angle, 1.0)
    # 计算图像的新边界维数
    newW = int((h * np.abs(M[0, 1])) + (w * np.abs(M[0, 0])))
    newH = int((h * np.abs(M[0, 0])) + (w * np.abs(M[0, 1])))
    # 调整旋转矩阵以考虑平移
    M[0, 2] += (newW - w) / 2
    M[1, 2] += (newH - h) / 2
    # 执行实际的旋转并返回图像
    return cv2.warpAffine(image, M, (newW, newH))  # borderValue 缺省，默认是黑色

def rotate_img_bbox(img, bboxes, angle=45, scale=1.):
    '''
    输入:
        img(ndarray):(h,w,c)
        bboxes(list):[[[x0, y0], [x1, y1], [x2, y2], [x3, y3]]]
        angle:旋转角度,逆时针旋转
        scale:默认1
    输出:
        rot_img:旋转后的图像array
        rot_bboxes:[[x0, y0], [x1, y1], [x2, y2], [x3, y3]], 顺时针左上到左下
    '''
    #---------------------- 旋转图像 ----------------------
    w = img.shape[1]
    h = img.shape[0]

    # 角度变弧度
    rangle = np.deg2rad(angle)  # angle in radians

    # now calculate new image width and height
    nw = (abs(np.sin(rangle)*h) + abs(np.cos(rangle)*w))*scale
    nh = (abs(np.cos(rangle)*h) + abs(np.sin(rangle)*w))*scale

    # ask OpenCV for the rotation matrix
    rot_mat = cv2.getRotationMatrix2D((nw*0.5, nh*0.5), angle, scale)

    # calculate the move from the old center to the new center combined
    # with the rotation
    rot_move = np.dot(rot_mat, np.array([(nw-w)*0.5, (nh-h)*0.5, 0]))

    # the move only affects the translation, so update the translation
    # part of the transform
    rot_mat[0, 2] += rot_move[0]
    rot_mat[1, 2] += rot_move[1]

    # 仿射变换
    rot_img = cv2.warpAffine(img,
                             rot_mat,
                             (int(math.ceil(nw)), int(math.ceil(nh))),
                             flags=cv2.INTER_LANCZOS4,
                             borderMode=cv2.BORDER_REFLECT,  # 这里可以选择填充颜色
                             )

    #---------------------- 矫正bbox坐标 ----------------------
    # rot_mat是最终的旋转矩阵
    rot_bboxes = list()
    for bbox in bboxes:
        point1 = np.dot(rot_mat, np.array(
            [bbox[0][0], bbox[0][1], 1]).astype(np.int32))
        point2 = np.dot(rot_mat, np.array(
            [bbox[1][0], bbox[1][1], 1]).astype(np.int32))
        point3 = np.dot(rot_mat, np.array(
            [bbox[2][0], bbox[2][1], 1]).astype(np.int32))
        point4 = np.dot(rot_mat, np.array(
            [bbox[3][0], bbox[3][1], 1]).astype(np.int32))

        # 加入list中
        rot_bboxes.append([ [point2[0], point2[1]],
                           [point3[0], point3[1]],
                           [point4[0], point4[1]],
                           [point1[0], point1[1]]])

    return rot_img, rot_bboxes


if __name__ == "__main__":
    root = '/mnt/data/rz/data/idCard/v4'
    img_paths = glob(os.path.join(root, 'org/*.base64'))
    drawed = True
    store_txt = True
    url = "http://127.0.0.1:30101/ocr/image_angle_detect"
    headers = {"Content-Type": 'application/json;charset=UTF-8'}


    for imgp in tqdm(img_paths):
        name = os.path.basename(imgp)
        name = os.path.splitext(name)[0]
        img_dir_name = 'image'
        label_dir_name = 'baiduLabel'
        store_img_path = os.path.join(root, img_dir_name, name+'.jpg')
        store_label_path = os.path.join(root, label_dir_name, name+'.txt')
        if not os.path.exists(os.path.join(root, img_dir_name)):
            os.makedirs(os.path.join(root, img_dir_name))
        if not os.path.exists(os.path.join(root, label_dir_name)):
            os.makedirs(os.path.join(root, label_dir_name))

        # =============== get image angle =============
        with open(imgp) as f:
            content = f.read().split(',')[1]
            img = base64_to_image(content)
        # get image angle
        angle_result = get_request_result(img, url, headers)
        angle = angle_result["responseData"]['angle']


        # =============== extract images =============
        lines = []
        points = []
        rot_points = []
        with open(imgp.replace('base64', 'json'), 'r', encoding='utf-8') as f:
            ct = json.load(f)
        ct = json.loads(ct)
        result = ct.get("words_result", None)
        if result is None:
            continue
        for k, v in result.items():
            class_names_map = {'出生':'birthday', '公民身份号码':'number', '失效日期':'validity', '姓名':'name', '性别':'sex', '住址':'address', '签发日期':'validity', '签发机关':'authority', '民族':'nation'}
            cls = class_names_map[k]
            loc = v["location"]
            left, top, width, height = loc['left'], loc['top'], loc['width'], loc['height']
            x1, y1 = left, top
            x2, y2 = x1 + width, y1
            x3, y3 = x2, y1+height
            x4, y4 = x1, y3
            pt = [x1, y2, x2, y2, x3, y3, x4, y4]
            points.append(pt)
            words = v["words"]
            line = ','.join(map(str, pt)) + '\t' + words + '\t' + cls
            lines.append(line)

        bboxes = np.reshape(points, (-1, 4, 2))
        # rotate image and bbox
        rot_img, rot_bbox = rotate_img_bbox(img, bboxes, angle)
        rot_bbox = np.array(rot_bbox, dtype='int').reshape((-1, 8)).tolist()
        new_lines = []
        for i, line in enumerate(lines):
            _, ct, cls = line.strip().split('\t')
            rbbox = rot_bbox[i]
            rbbox = ','.join(map(str, rbbox))
            # line = '\t'.join([rbbox, ct, cls])
            line = ','.join([rbbox, ct, cls])
            new_lines.append(line)
        with open(store_label_path, 'w') as f:
            f.write('\n'.join(new_lines))
        cv2.imwrite(store_img_path, rot_img)

        # =============================

        if drawed:
            drawed_img = draw_text_det_res(rot_bbox, rot_img)
            img_name = name + '.jpg'
            cv2.imwrite('./data/drawed/{}'.format(img_name), drawed_img)
        
        # if store_txt:
        #     h, w = img.shape[:2]
        #     img_name = name + '.jpg'
        #     txt_name = img_name.split('.')[0] + '.txt'
        #     txt_store_path = os.path.join('./drawed/', txt_name)
        #     loc = loc.reshape((-1, 8))
        #     loc = loc[:, [0, 1, 4, 5]]
        #     x_center = (loc[:, 0] + loc[:, 2]) / (2 * w)
        #     y_center = (loc[:, 1] + loc[:, 3]) / (2 * h)
        #     w_yolo = (loc[:, 2] - loc[:, 0]) / w
        #     h_yolo = (loc[:, 3] - loc[:, 1]) / h
        #     lines = []
        #     for xc, yc, wy, hy in zip(x_center, y_center, w_yolo, h_yolo):
        #         line = '1 ' + ' '.join(map(str, [xc, yc, wy, hy]))
        #         lines.append(line)
        #     with open(txt_store_path, 'w') as f:
        #         f.write('\n'.join(lines))
