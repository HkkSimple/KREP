import json
import os
import numpy as np
from tqdm import tqdm
from xml.etree import cElementTree as ET
from glob import glob

# extract voc format data
def extract_voc(xmlp, split_flag, default_class_name=None):
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

			line = split_flag.join(map(str, points)) + split_flag + name
			lines.append(line)
		return {'filename': filename,
				'items': lines}
	return


# convert to dota format
def voc_to_dota(xml_root, txt_store_root, split_flag):
	xml_paths = glob(os.path.join(xml_root, '*.xml'))
	for xmlp in tqdm(xml_paths):
		content = extract_voc(xmlp, split_flag)
		if content is None:
			print('xml path:{} is error'.format(xmlp))
			continue
		name = content['filename']
		lines = content['items']
		# dota line format: x1,y1,x2,y2,x3,y3,x4,y4,category,difficult
		dota_lines = ['imagesource:GF-2', 'gsd:null']
		difficult = '0' # 0 or 1; 1->difficult, 0->not difficult
		for line in lines:
			line = line + split_flag + difficult
			dota_lines.append(line)
		txt_name = name.split('.')[0] + '.txt'
		txt_store_path = os.path.join(txt_store_root, txt_name)
		with open(txt_store_path, 'w') as f:
			f.write('\n'.join(dota_lines))


if __name__ == "__main__":
	xml_root = '/mnt/data/rz/data/register/xml'
	txt_store_root = '/mnt/data/rz/data/register/labelTxt'
	split_flag = ' '
	voc_to_dota(xml_root, txt_store_root, split_flag)
