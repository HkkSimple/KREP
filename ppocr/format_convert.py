import os.path as osp
from tqdm import tqdm
import numpy as np
from glob import glob
import json

def icdar_to_ppdetect(path, suffix, img_flag='jpg'):
	results = []
	name = osp.basename(path).split('.')[0]
	name = name.replace('gt_', '')
	img_file_name = "{}/{}.{}".format(suffix, name, img_flag)
	with open(path) as f:
		for line in f:
			line = line.strip().split()
			line = list(map(float, line))
			# line = [round(n) for n in line]
			x1, y1, x2, y2 = line
			line = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
			item = {"transcription": "MASA", "points": line}
			results.append(item)

	results = json.dumps(results)
	results = img_file_name + '\t' + results
	return results
			



def generate_ppdetect():
	root = '/mnt/data/rz/data/UIDetect/sap/elements/text_detect'
	txt_paths = glob(osp.join(root, 'xml/*.txt'))
	store_path = osp.join(root, 'sap_gt_label.txt')
	suffix = 'images'
	lines = []
	for txtp in txt_paths:
		line = icdar_to_ppdetect(txtp, suffix, 'png')
		lines.append(line)
	with open(store_path, 'w') as f:
		f.write('\n'.join(lines))



if __name__ == "__main__":
	generate_ppdetect()
