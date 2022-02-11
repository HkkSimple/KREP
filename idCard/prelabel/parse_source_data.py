import cv2
import os.path as osp
from glob import glob
from tqdm import tqdm

from extract import extract_source_data
from util import make_dirs


# 解析百度识别结果后的原文件,并存储
if __name__ == "__main__":
    root = '/mnt/data/rz/data/idCard/v5'
    source_data_dir = osp.join(root, 'org')
    org_img_paths = glob(osp.join(source_data_dir, '*.base64'))
    image_angle_detect_url = "http://127.0.0.1:30101/ocr/image_angle_detect"

    img_store_root = osp.join(root, 'images')
    txt_store_root = osp.join(root, 'baiduLabels')

    make_dirs(img_store_root)
    make_dirs(txt_store_root)

    for imgp in tqdm(org_img_paths):
        imgn = osp.basename(imgp)
        txtn = imgn.replace('jpg', 'txt')
        
        lines, img = extract_source_data(imgp, image_angle_detect_url)
        store_imgp = osp.join(img_store_root, imgn)
        store_txtp = osp.join(txt_store_root, txtn)
        cv2.imwrite(store_imgp, img)
        with open(store_txtp, 'w') as f:
            f.write('\n'.join(lines))