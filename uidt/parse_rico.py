import os.path as osp
import numpy as np
from tqdm import tqdm
import json
from glob import glob
from pandas import DataFrame
import cv2
import os


def parse_semantic_children(data, store):
    for item in data:
        tmp = dict()
        for key, value in item.items():
            if key == 'children':
                parse_semantic_children(value, store)
            elif key == 'bounds':
                tmp[key] = value
            elif key == 'componentLabel':
                tmp[key] = value
        store.append(tmp)
    return store


def parse_semantic_ann(path):
    with open(path) as f:
        content = f.read()
    content = json.loads(content)
    border = []
    children_data = []
    for key, value in content.items():
        item = dict()
        if key == 'bounds':
            border = value
        elif key == 'children':
            parse_semantic_children(value, children_data)

    return border, children_data


def unique_points(data):
    bounds = [','.join(map(str, d['bounds'])) for d in data]
    labels = [d['componentLabel'] for d in data]

    df_data = DataFrame(data={'bounds': bounds, 'labels': labels}, columns=[
                        'bounds', 'labels'])
    unique_data = df_data.drop_duplicates()
    return unique_data


if __name__ == "__main__":
    root = '/mnt/data/rz/data/UIDetect/combined/'
    org_img_root = osp.join(root, 'images')
    cutted_img_store_root = osp.join(root, 'labels_icdar')
    if not osp.exists(cutted_img_store_root):
        os.makedirs(cutted_img_store_root)
    ann_path = osp.join(root, 'semantic_annotations', '*.json')
    ann_paths = glob(ann_path)

    for annp in tqdm(ann_paths):
        imgn = osp.basename(annp).replace('json', 'jpg')
        sem_img_path = osp.join(root, 'semantic_annotations',
                                imgn.replace('jpg', 'png'))
        border, elements = parse_semantic_ann(annp)
        org_img_path = osp.join(org_img_root, imgn)
        org_img = cv2.imread(org_img_path)
        h, w = org_img.shape[:2]
        semH, semW = cv2.imread(sem_img_path).shape[:2]
        ratioH, ratioW = h / semH, w / semW

        boxes = [d['bounds'] for d in elements]
        labels = [d['componentLabel'] for d in elements]
        boxes = np.array(boxes)
        boxes = boxes.reshape((-1, 2, 2))
        boxes[:, :, 0] = boxes[:, :, 0] * ratioW
        boxes[:, :, 1] = boxes[:, :, 1] * ratioH
        boxes = boxes.reshape((-1, 4))
        boxes = boxes.tolist()

        lines = [','.join(map(str, bx)) + '\t' + lb for bx,
                 lb in zip(boxes, labels)]
        store_img_path = osp.join(cutted_img_store_root, imgn)
        store_txt_path = store_img_path.replace('jpg', 'txt')

        cv2.imwrite(store_img_path, org_img)
        with open(store_txt_path, 'w') as f:
            f.write('\n'.join(lines))
