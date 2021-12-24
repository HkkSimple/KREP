from glob import glob
import os.path as osp
from tqdm import tqdm
import numpy as np

# iou calculate
def iou(rect1, rect2):
	def area(rect):
		X = rect[:, 2] - rect[:, 0]
		Y = rect[:, 3] - rect[:, 1]
		return X * Y
	sum_area = area(rect1) + area(rect2)

	upleft = np.maximum(rect1[:, :2], rect2[:, :2])
	botright = np.minimum(rect1[:, 2:], rect2[:, 2:])
	inter_wh = botright - upleft
	inter_wh = np.maximum(inter_wh, 0)
	inter_area = inter_wh[:, 0] * inter_wh[:, 1]

	union = sum_area - inter_area
	iou_val = inter_area / union
	return iou_val

def parse_label_file(path):
	locations = []
	contents = []
	with open(path) as f:
		for line in f:
			loc, ct= line.strip().split('\t')[:2]
			loc = list(map(int, loc.strip().split(',')))
			loc = [loc[0], loc[1], loc[4], loc[5]]
			locations.append(loc)
			contents.append(ct)
	return np.array(locations), contents

ocr_labels_root = '/mnt/data/rz/data/store/20211207/ocr_labels'
person_labels_root = '/mnt/data/rz/data/store/20211207/person_label'
ocr_labels_paths = glob(osp.join(ocr_labels_root, '*.txt'))
total_items = 0
correct = 0
invalid = 0
for ocrp in tqdm(ocr_labels_paths):
	name = osp.basename(ocrp)
	personp = osp.join(person_labels_root, name)
	if not osp.exists(personp):
		print('path is not exist:', ocrp)
	
	# ocr api labels txt file
	ocr_locations, ocr_contents = parse_label_file(ocrp)

	# person labels txt file 
	person_locations, person_contents = parse_label_file(personp)
	for ploc, pct in zip(person_locations, person_contents):
		total_items += 1
		if '###' in pct:
			invalid += 1
			continue
		ploc = np.expand_dims(ploc, axis=0)
		iou_val = iou(ocr_locations, ploc)
		idx = np.argmax(iou_val)
		if iou_val[idx] != 0:
			ocr_ct = ocr_contents[idx]
			if ocr_ct == pct:
				correct += 1

print('total item:', total_items)
print('invalid item:', invalid)
print('acc:', correct / (total_items - invalid))
print('acc:', correct / total_items)