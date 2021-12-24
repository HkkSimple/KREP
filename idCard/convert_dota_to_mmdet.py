import os
import os.path as osp

import mmcv
import numpy as np
from PIL import Image



def norm_angle(angle, range=[-np.pi / 4, np.pi]):
    return (angle - range[0]) % range[1] + range[0]

def poly_to_rotated_box_single(poly):
    """
    poly:[x0,y0,x1,y1,x2,y2,x3,y3]
    to
    rotated_box:[x_ctr,y_ctr,w,h,angle]
    """
    poly = np.array(poly[:8], dtype=np.float32)

    pt1 = (poly[0], poly[1])
    pt2 = (poly[2], poly[3])
    pt3 = (poly[4], poly[5])
    pt4 = (poly[6], poly[7])

    edge1 = np.sqrt((pt1[0] - pt2[0]) * (pt1[0] - pt2[0]) +
                    (pt1[1] - pt2[1]) * (pt1[1] - pt2[1]))
    edge2 = np.sqrt((pt2[0] - pt3[0]) * (pt2[0] - pt3[0]) +
                    (pt2[1] - pt3[1]) * (pt2[1] - pt3[1]))

    width = max(edge1, edge2)
    height = min(edge1, edge2)

    angle = 0
    if edge1 > edge2:
        angle = np.arctan2(
            np.float(pt2[1] - pt1[1]), np.float(pt2[0] - pt1[0]))
    elif edge2 >= edge1:
        angle = np.arctan2(
            np.float(pt4[1] - pt1[1]), np.float(pt4[0] - pt1[0]))

    angle = norm_angle(angle)

    x_ctr = np.float(pt1[0] + pt3[0]) / 2
    y_ctr = np.float(pt1[1] + pt3[1]) / 2
    rotated_box = np.array([x_ctr, y_ctr, width, height, angle]).astype('float16')
    return rotated_box

def parse_ann_info(label_base_path, img_name, label_ids):
    lab_path = osp.join(label_base_path, img_name + '.txt')
    bboxes, labels, bboxes_ignore, labels_ignore = [], [], [], []
    with open(lab_path, 'r') as f:
        for ann_line in f.readlines():
            ann_line = ann_line.strip().split(',')
            bbox = [float(ann_line[i]) for i in range(8)]
            # 8 point to 5 point xywha
            bbox = tuple(poly_to_rotated_box_single(bbox).tolist())
            # class_name = ann_line[9]
            class_name = ann_line[9]
            # difficult = int(ann_line[9])
            difficult = 0
            # ignore difficult =2
            if difficult == 0:
                bboxes.append(bbox)
                labels.append(label_ids[class_name])
            elif difficult == 1:
                bboxes_ignore.append(bbox)
                labels_ignore.append(label_ids[class_name])
    return bboxes, labels, bboxes_ignore, labels_ignore


def convert_icdar_to_mmdet(src_path, out_path, label_ids, trainval=True, filter_empty_gt=True, ext='.png'):
    """Generate .pkl format annotation that is consistent with mmdet.
    Args:
        src_path: dataset path containing images and labelTxt folders.
        out_path: output pkl file path
        trainval: trainval or test
    """
    # img_path = os.path.join(src_path, 'images')
    img_path = os.path.join(src_path, 'data')
    label_path = os.path.join(src_path, 'labelTxt')
    img_lists = os.listdir(img_path)

    data_dict = []
    for id, img in enumerate(img_lists):
        img_info = {}
        img_name = osp.splitext(img)[0]
        label = os.path.join(label_path, img_name + '.txt')
        img = Image.open(osp.join(img_path, img))
        img_info['filename'] = img_name + ext
        img_info['height'] = img.height
        img_info['width'] = img.width
        if trainval:
            if not os.path.exists(label):
                print('Label:' + img_name + '.txt' + ' Not Exist')
                continue
            # filter images without gt to speed up training
            if filter_empty_gt & (osp.getsize(label) == 0):
                continue
            bboxes, labels, bboxes_ignore, labels_ignore = parse_ann_info(label_path, img_name, label_ids=label_ids)
            ann = {}
            ann['bboxes'] = np.array(bboxes, dtype=np.float32)
            ann['labels'] = np.array(labels, dtype=np.int64)
            ann['bboxes_ignore'] = np.array(bboxes_ignore, dtype=np.float32)
            ann['labels_ignore'] = np.array(labels_ignore, dtype=np.int64)
            img_info['ann'] = ann
        data_dict.append(img_info)

    mmcv.dump(data_dict, out_path)


if __name__ == '__main__':
    class_name = ['name', 'sex', 'birthday', 'address', 'number', 'authority', 'validity', 'nation']
    label_ids = {name: i + 1 for i, name in enumerate(class_name)}
    root = '/mnt/data/rz/data/idCard/v2'
    out_path = '/mnt/data/rz/data/idCard/v2/trainval_idCard.pkl'

    # the icdar format of ocr:x1,y1,x2,y2,x3,y3,x4,y4 \t class_name \t difficult 0/1（1:will be ignore）
    # convert_icdar_to_mmdet('data/dota_1024/trainval_split',
    #                      'data/dota_1024/trainval_split/trainval_s2anet.pkl', label_ids=label_ids)
    convert_icdar_to_mmdet(root, out_path, label_ids=label_ids, ext='.jpg')
    print('done!')