import json
import os
import numpy as np
from tqdm import tqdm
import shutil
import cv2
from xml.etree import cElementTree as ET
from glob import glob

def extract_voc(xmlp, default_class_name=None):
	if not os.path.exists(xmlp):
		print('{} file is not exists.'.format(xmlp))
		return 
	with open(xmlp) as f:
		tree = ET.parse(f)
		root = tree.getroot()

	filename = root.find('filename').text # get image file name
	lines = []
	objects = root.findall('object')
	if len(objects) >0:
		for obj in objects:
			name = obj.find('name').text #class name
			if default_class_name is not None:
				name = default_class_name
			polys = obj.find('polygon').findall('pt')
			points = []
			for pt in polys:
				x, y = pt.find('x').text, pt.find('y').text
				points.extend(map(int, [float(x), float(y)]))

			line = ','.join(map(str, points)) + '\t' + name
			lines.append(line)
		return {'filename': filename,
				'items': lines}
	return


if __name__ == '__main__':
	root = '../data'
	xml_paths = glob(os.path.join(root, '*.xml'))
	store_path = ''
	for xmlp in xml_paths:
		content = extract_voc(xmlp)
		if content is None:
			print('xml path:{} is error'.format(xmlp))
			continue
		name = content['filename']
		lines = content['items']
		with open(store_path, 'w') as f:
			f.write('\n'.join(lines))
		print(content)