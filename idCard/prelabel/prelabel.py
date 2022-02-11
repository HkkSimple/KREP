import os
import os.path as osp
from glob import glob
from tqdm import tqdm
import numpy as np
import cv2
import shutil
from time import time

from extract import extract_source_data
from util import make_dirs
from cut_image import get_item_label
from custom_idcard import get_custom_idcard_content
from corner import get_cornered_img



if __name__ == "__main__":
    root = '/mnt/data/rz/data/idCard/v6'
    source_data_dir = osp.join(root, 'org')
    org_img_paths = glob(osp.join(source_data_dir, '*.base64'))
    image_angle_detect_url = "http://127.0.0.1:30101/ocr/image_angle_detect"
    custom_idcard_rec_url = "http://127.0.0.1:30100/ocr/idcard"
    corner_url = "http://127.0.0.1:30102/ocr/idcard/corner"

    store_cutted_img_root = osp.join(root, 'cutted/images')
    store_cutted_txt_path = osp.join(root, 'cutted/baiduLabel.txt')
    make_dirs(store_cutted_img_root)

    error_img_root = osp.join(root, 'error/images')
    error_txt_path = osp.join(root, 'error/label.txt')
    except_img_root = osp.join(root, 'error/except')
    make_dirs(error_img_root)
    make_dirs(except_img_root)

    item_lines = [] # 字段标注文件的行信息
    error_lines = []
    for imgp in tqdm(org_img_paths):
        org_imgn = osp.basename(imgp).replace('base64', 'jpg')
        extract_data = extract_source_data(imgp, image_angle_detect_url)
        if extract_data is None:
            # line = 'images/' + org_imgn + '\t' + '###'
            # error_lines.append(line)
            shutil.copy(imgp, except_img_root)
            shutil.copy(imgp.replace('base64', 'json'), except_img_root)
            continue
        lines, img = extract_data
        new_lines, cutted_imgs = get_item_label(lines, img)

        # custom idcard recognize result
        clses = [l.strip().split('\t')[0] for l in new_lines]
        custom_address_info = {'content':[], 'y':[], 'img':[]}
        if 'validity' not in clses and 'authority' not in clses:
            cornered_img = get_cornered_img(corner_url, img) # 获取经过角点提取后的图片,去除了背景
            custom_content = get_custom_idcard_content(custom_idcard_rec_url, org_imgn, img)
            res_data = custom_content.get('responseData', None)
            if res_data is not None and len(res_data) > 0 and cornered_img is not None:
                for item in res_data:
                    cls, ct, loc = item['class_name'], item['content'], item['location']
                    x1, y1, x2, y2, x3, y3, x4, y4 = loc
                    if cls == 'address':
                        custom_cutted_img = cornered_img[y1:y3, x1:x3, :]
                        custom_address_info['content'].append(ct)
                        custom_address_info['y'].append(y1)
                        custom_address_info['img'].append(custom_cutted_img)

        for i, d in enumerate(zip(new_lines, cutted_imgs)):
            line, cutted_im = d
            shape = cutted_im.shape
            if shape is None or min(shape) == 0:
                continue
            cls, ct = line.split('\t')
            # t = str(int(time()*1000000))
            if cls != 'address': # 除了地址地段，其余的以百度识别结果为准
                imgn = str(i) + '_' + org_imgn
                store_cutted_img_path = osp.join(store_cutted_img_root, imgn)
                cv2.imwrite(store_cutted_img_path, cutted_im)
                line = 'images/' + imgn + '\t' + ct
                item_lines.append(line)
            # 对于地址字段，需要进一步进行处理
            else:
                baidu_address = ct
                custom_address_list = custom_address_info['content']
                custom_address_cutted_imgs = custom_address_info['img']
                custom_address_len = len(''.join(custom_address_list))
                idxes = np.argsort(custom_address_info['y']) # 字段框左上点的y坐标，用于判断字段的上下位置
                if len(baidu_address) == custom_address_len: # custom的识别结果与百度的识别结果当字符数一样时，则直接保存引用，如果不一样，则转人工确认
                    begin = 0
                    end = 0
                    for j, ix in enumerate(idxes):
                        end = min(begin + len(custom_address_list[ix]), custom_address_len)
                        baidu_item_address = baidu_address[begin:end]
                        imgn = str(j) + str(i) + '_' + org_imgn
                        line = 'images/' + imgn + '\t' + baidu_item_address
                        begin = end
                        item_lines.append(line)
                        imgp = osp.join(store_cutted_img_root, imgn)
                        cv2.imwrite(imgp, custom_address_cutted_imgs[ix])
                else:
                    # 如果不相等，则使用百度的地址整块识别内容，转人工后进行确认
                    imgn = str(i) + '_' + org_imgn
                    imgp = osp.join(error_img_root, imgn)
                    line = 'images/' + imgn + '\t' + baidu_address
                    cv2.imwrite(imgp, cutted_im)
                    error_lines.append(line)

    with  open(store_cutted_txt_path, 'w') as f:
        f.write('\n'.join(item_lines))

    with open(error_txt_path, 'w') as f:
        f.write('\n'.join(error_lines))

