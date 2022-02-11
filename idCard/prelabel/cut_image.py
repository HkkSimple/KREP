# 对真实数据进行字段切分
from glob import glob
import os.path as osp
import cv2

def baidu_parse(data):
    result = list()
    for line in data:
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
        return None
    return item_img

# 通过预标注文件中，字段的位置与内容，将图片裁切并对应相应的字段内容
def get_item_label(anno_lines, img):
    label_lines = []
    cutted_imgs = []
    bresult = baidu_parse(anno_lines)
    for item in bresult:
        cls, ct, loc = item['cls'], item['ct'], item['loc']
        cutted_img = cut_img(img, item)
        if cutted_img is None:
            continue
        if cls == 'validity':
            if len(ct) == 8:
                ct = ct[:4] + '.' + ct[4:6] + '.' + ct[6:8]
        if cls == 'birthday':
            if len(ct) == 8:
                ct = ct[:4] + '年' + ct[4:6] + '月' + ct[6:8] + '日'
        line = cls + '\t' + ct
        label_lines.append(line)
        cutted_imgs.append(cutted_img)
    return label_lines, cutted_imgs