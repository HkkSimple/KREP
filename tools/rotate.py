import math
import os
from tqdm import tqdm

import numpy as np
import torchvision.transforms.functional as TF
from shapely.geometry import Polygon
from shapely.geometry import box as shapely_box
from glob import glob
from PIL import Image


class RandomRotateImageBox:
    """Rotate augmentation for segmentation based text recognition.

    Args:
        min_angle (int): Minimum rotation angle for image and box.
        max_angle (int): Maximum rotation angle for image and box.
        box_type (str): Character box type, should be either
            'char_rects' or 'char_quads', with 'char_rects'
            for rectangle with ``xyxy`` style and 'char_quads'
            for quadrangle with ``x1y1x2y2x3y3x4y4`` style.
    """

    def __init__(self, min_angle=-10, max_angle=10, box_type='char_quads'):
        assert box_type in ('char_rects', 'char_quads')

        self.min_angle = min_angle
        self.max_angle = max_angle
        self.box_type = box_type

    def __call__(self, results):
        in_img = results['img']
        in_chars = results['ann_info']['chars']
        in_boxes = results['ann_info'][self.box_type]

        img_width, img_height = in_img.size
        rotate_center = [img_width / 2., img_height / 2.]

        tan_temp_max_angle = rotate_center[1] / rotate_center[0]
        temp_max_angle = np.arctan(tan_temp_max_angle) * 180. / np.pi

        random_angle = np.random.uniform(
            max(self.min_angle, -temp_max_angle),
            min(self.max_angle, temp_max_angle))
        random_angle_radian = random_angle * np.pi / 180.

        img_box = shapely_box(0, 0, img_width, img_height)

        out_img = TF.rotate(
            in_img,
            random_angle,
            resample=False,
            expand=False,
            center=rotate_center)

        out_boxes, out_chars = self.rotate_bbox(in_boxes, in_chars,
                                                random_angle_radian,
                                                rotate_center, img_box)

        results['img'] = out_img
        results['ann_info']['chars'] = out_chars
        results['ann_info'][self.box_type] = out_boxes

        return results

    @staticmethod
    def rotate_bbox(boxes, chars, angle, center, img_box):
        out_boxes = []
        out_chars = []
        for idx, bbox in enumerate(boxes):
            temp_bbox = []
            for i in range(len(bbox) // 2):
                point = [bbox[2 * i], bbox[2 * i + 1]]
                temp_bbox.append(
                    RandomRotateImageBox.rotate_point(point, angle, center))
            poly_temp_bbox = Polygon(temp_bbox).buffer(0)
            if poly_temp_bbox.is_valid:
                if img_box.intersects(poly_temp_bbox) and (
                        not img_box.touches(poly_temp_bbox)):
                    temp_bbox_area = poly_temp_bbox.area

                    intersect_area = img_box.intersection(poly_temp_bbox).area
                    intersect_ratio = intersect_area / temp_bbox_area

                    if intersect_ratio >= 0.7:
                        out_box = []
                        for p in temp_bbox:
                            out_box.extend(p)
                        out_boxes.append(out_box)
                        out_chars.append(chars[idx])

        return out_boxes, out_chars

    @staticmethod
    def rotate_point(point, angle, center):
        cos_theta = math.cos(-angle)
        sin_theta = math.sin(-angle)
        c_x = center[0]
        c_y = center[1]
        new_x = (point[0] - c_x) * cos_theta - (point[1] -
                                                c_y) * sin_theta + c_x
        new_y = (point[0] - c_x) * sin_theta + (point[1] -
                                                c_y) * cos_theta + c_y

        return [new_x, new_y]


def rotate_image_and_box():
	rtb = RandomRotateImageBox()

	ann_root = '/mnt/data/rz/data/register/detect/icdar_labels'
	images_root = '/mnt/data/rz/data/register/detect/images'
	store_root = '/mnt/data/rz/data/register/detect/rotate'
	paths = glob(os.path.join(ann_root, '*.txt'))
	for annp in tqdm(paths):
		with open(annp) as f:
			content = f.read().strip().split('\n')
			boxes = [line.split(',')[:-1] for line in content]
			categorys = [line.split(',')[-1] for line in content]
			in_boxes = [np.array(list(map(int, bx))) for bx in boxes]
			if len(boxes) > 2:
				continue

		txtn = os.path.basename(annp)
		imgn = txtn.replace('txt', 'png')
		imgp = os.path.join(images_root, imgn)
		
		in_img = Image.open(imgp)
		in_chars = 'tmp'
		img_width, img_height = in_img.size
		rotate_center = [img_width / 2., img_height / 2.]

		random_angle = -90
		random_angle_radian = random_angle * np.pi / 180.
		img_box = shapely_box(0, 0, img_width, img_height)

		out_img = TF.rotate(
			in_img,
			random_angle,
			resample=False,
			expand=False,
			center=rotate_center)

		out_boxes, out_chars = rtb.rotate_bbox(in_boxes, in_chars,
												random_angle_radian,
												rotate_center, img_box)

		txt_store_path = os.path.join(store_root, 'rt_' + txtn)
		img_store_path = os.path.join(store_root, 'rt_' + imgn)
		with open(txt_store_path, 'w') as f:
			boxes = [','.join(map(str, line))+','+ct for line, ct in zip(out_boxes, categorys)]
			f.write('\n'.join(boxes))
		out_img.save(img_store_path)


if __name__ == "__main__":
	rotate_image_and_box()
