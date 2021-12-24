import cv2
import shutil
import os.path as osp
import os
import numpy as np
from tqdm import tqdm
from xml.etree import cElementTree as ET
from glob import glob
from sklearn.model_selection import train_test_split

import sys
sys.path.append('/mnt/data/rz/programe/KREP')

from tools.filter_char import find_unchinese
from util.order_points import sort_box

# Truncates numbers to N decimals
def truncate(n, decimals=0):
	multiplier = 10 ** decimals
	return int(n * multiplier) / multiplier

# extract voc format data
def extract_voc(xmlp, split_flag, default_class_name=None):
	if not os.path.exists(xmlp):
		print('{} file is not exists.'.format(xmlp))
		return
	with open(xmlp) as f:
		tree = ET.parse(f)
		root = tree.getroot()

	filename = root.find('filename').text  # get image file name
	folder = root.find('folder').text
	imgH = root.find('imagesize').find('nrows').text
	imgW = root.find('imagesize').find('ncols').text
	imgH, imgW = int(imgH), int(imgW)
	lines = []
	objects = root.findall('object')
	if len(objects) > 0:
		for obj in objects:
			name = obj.find('name').text  # class name
			if default_class_name is not None:
				name = default_class_name
			# find polygon
			polys = obj.find('polygon').findall('pt')
			points = []
			for pt in polys:
				x, y = pt.find('x').text, pt.find('y').text
				points.extend(map(int, [float(x), float(y)]))
			# find attributes
			att = obj.find('attributes').text

			if att is None:
				att = '###'
			line = split_flag.join(map(str, points)) + '\t' + name + '\t' + att
			lines.append(line)
		return {'filename': filename,
				'items': lines,
				'imgH': imgH,
				'imgW': imgW,
				'folder': folder,
				'attributes': att}
	return {'filename': filename,
			'items': '',
			'imgH': imgH,
			'imgW': imgW,
			'folder': folder,
			'attributes': '###'}


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
		# dota_lines = ['imagesource:GF-2', 'gsd:null']
		dota_lines = []
		difficult = '0'  # 0 or 1; 1->difficult, 0->not difficult
		for line in lines:
			print(line)
			line = line.strip().split('\t')[:2]
			line = split_flag.join(line)
			line = line + split_flag + difficult
			dota_lines.append(line)
		txt_name = name.split('.')[0] + '.txt'
		txt_store_path = os.path.join(txt_store_root, txt_name)
		with open(txt_store_path, 'w') as f:
			f.write('\n'.join(dota_lines))

# convert to icdar format
def voc_to_icdar(xml_root, txt_store_root, split_flag, filter_classes=[]):
	error_names = []
	xml_paths = glob(os.path.join(xml_root, '*.xml'))
	for xmlp in tqdm(xml_paths):
		content = extract_voc(xmlp, split_flag)
		if content is None:
			print('xml path:{} is error'.format(xmlp))
			continue
		name = content['filename']
		lines = content['items']
		icdar_lines = []
		for line in lines:
			loc, cls, ct = line.split('\t')
			if cls in filter_classes:  # 过滤掉在filter classes中出现的类
				continue
			txt = ct.replace('content=', '')
			if len(txt) == 0:
				txt = '###'
			if txt[0] == "'":
				txt = txt[1:]
			line = loc + ',' + txt + ',' + cls
			icdar_lines.append(line)

		# store
		if len(icdar_lines) == 0:
			error_names.append(name)
			continue
		txt_name = name.split('.')[0] + '.txt'
		txt_store_path = os.path.join(txt_store_root, txt_name)
		with open(txt_store_path, 'w') as f:
			f.write('\n'.join(icdar_lines))
	return error_names
		
def voc_to_yolov5(xml_root, txt_store_root, class_idx, split_flag=',', filter_classes=[]):
	if not osp.exists(txt_store_root):
		os.makedirs(txt_store_root)
	xml_paths = glob(osp.join(xml_root, '*.xml'))
	for xmlp in tqdm(xml_paths):
		content = extract_voc(xmlp, split_flag=split_flag)
		img_name = content['filename']
		lines = content['items']
		imgH = content['imgH']
		imgW = content['imgW']
		new_lines = []
		for line in lines:
			line = line.split(split_flag)
			loc, cls = line[:8], line[-1]
			if cls in filter_classes:  # 过滤掉在filter classes中出现的类
				continue
			# if cls == 'icon':
			#     cls = 'element'
			loc = list(map(int, loc))
			xmin, ymin, xmax, ymax = loc[0], loc[1], loc[4], loc[5]
			dw, dh = 1. / imgW, 1 / imgH
			x = (xmin + xmax)/2
			y = (ymin + ymax)/2
			w = xmax - xmin
			h = ymax - ymin
			x = x * dw
			w = w * dw
			y = y * dh
			h = h * dh
			idx = class_idx[cls]
			# idx = '0'
			new_line = ' '.join([idx,
								 str(truncate(x, 7)),
								 str(truncate(y, 7)),
								 str(truncate(w, 7)),
								 str(truncate(h, 7))])
			new_lines.append(new_line)
		txt_name = img_name.split('.')[0] + '.txt'
		txt_store_path = osp.join(txt_store_root, txt_name)
		if len(new_lines) > 0:
			with open(txt_store_path, 'w') as f:
				f.write('\n'.join(new_lines))

# 将voc格式的xml文件转成单个字段识别的格式
# suffix: 在做line的filename那一栏时，是否需要添加前缀
# 登记证里目前没有加入全中文的训练，所以需要过滤掉一些样本
def voc_to_rec(xmlp, split_flag, suffix=''):
	content = extract_voc(xmlp, split_flag)
	filename = content['filename']
	att = content['attributes']
	if len(att) > 0:
		txt = att.split('=')[-1]
		if txt[0] == "'":
			txt = txt[1:]
		filtered_txt = find_unchinese(txt)
		if len(filtered_txt) < 4:
			return None, filename
		elif '/' in txt or '.' in txt:
			return None, filename
		if suffix != '':
			line = os.path.join(suffix, filename) + '\t' + txt
		else:
			line = filename + '\t' + txt
		return line, filename
	else:
		return None, filename

# cvat icdar format to common icdar format
def load_cvat_icdar(txtp, content='content'):
	results = []
	with open(txtp) as f:
		for line in f:
			line = line.strip().split()
			line = list(map(float, line))
			line = [round(n) for n in line]
			x1, y1, x2, y2 = line
			line = [x1, y1, x2, y1, x2, y2, x1, y2]
			line = [str(x) for x in line]
			line.append('content')
			line = ','.join(line)
			results.append(line)
	return results

# icdar format to labelme format: x1,y1,x2,y2,x3,y3,x4,y4 \t content ---> labelme3.0 xml format
def icdar_to_labelme():
	pass
# =======================================================

# 将voc格式的xml文件，转成icdar的格式去做文字检测:x1,y1,x2,y2,x3,y3,x4,y4,cls
def get_icdar_label():
	root = '/mnt/data/rz/data/idCard/v1'
	image_root = os.path.join(root, 'images')
	txt_store_root = os.path.join(root, 'personLabelTxt')
	error_store_root = os.path.join(root, 'error')
	if not osp.exists(txt_store_root):
		os.makedirs(txt_store_root)
	if not osp.exists(error_store_root):
		os.makedirs(error_store_root)
	# txt_paths = glob(osp.join(root, 'xml/*.txt'))
	# class_names = ['number', 'owner', 'frame_number', 'registration_number',
	#                'manner', 'property', 'cover_code', 'cover_number', 'idCard']
	# class_idx = {cls: str(idx) for idx, cls in enumerate(class_names)}

	# for d in ['1', '2', '3', '4', '5']:
	xml_root = os.path.join(root, 'xml')
	error_names = voc_to_icdar(xml_root, txt_store_root, split_flag=',',
							   filter_classes=['other'])
	for ename in error_names:
		epath = os.path.join(image_root, ename)
		# epath = epath.split('.')[0] + '.jpg'
		shutil.move(epath, error_store_root)
	# if not osp.exists(txt_store_root):
	#     os.makedirs(txt_store_root)
	# for txtp in txt_paths:
	#     txtn = osp.basename(txtp)
	#     txt_store_path = osp.join(txt_store_root, txtn)
	#     result = load_cvat_icdar(txtp)
	#     with open(txt_store_path, 'w') as f:
	#         f.write('\n'.join(result))

def get_dota_label():
	root = '/mnt/data/rz/data/idCard/v1'
	txt_store_root = os.path.join(root, 'labelTxt')
	if not osp.exists(txt_store_root):
		os.makedirs(txt_store_root)
	xml_root = os.path.join(root, 'xml')
	voc_to_dota(xml_root, txt_store_root, split_flag=',')
		

# 将voc格式的xml文件，转成yolov5的格式去做文字检测:x1,y1,x2,y2,x3,y3,x4,y4,cls
def get_yolov5_label():
	root = '/mnt/data/rz/data/UIDetect/sap/elements/element_detect'
	txt_store_root = '/mnt/data/rz/data/UIDetect/sap/elements/element_detect/labels_one_class'
	if not os.path.exists(txt_store_root):
		os.makedirs(txt_store_root)
	# class_names = ['number', 'owner', 'frame_number', 'registration_number',
	#                'manner', 'property', 'cover_code', 'cover_number', 'number_code', 
	#                'oil_type', 'vehicle_brand', 'domestic_import', 'factory', 'idCard']
	class_names = ['element', 'txt', 'button', 'inputBox', 'checkBox', 'comboBox', 
				   'minimize', 'maximize', 'close', 'slidingBoxes', 'radioButton']
	# class_names = ['txt']
	class_idx = {cls: str(idx) for idx, cls in enumerate(class_names)}
	# for d in map(str, range(0, 1)):
	# xml_root = os.path.join(root, d)
	xml_root= os.path.join(root, 'xml')
	voc_to_yolov5(xml_root, txt_store_root, class_idx, split_flag=',',
					filter_classes=['other'])

# 将voc格式的xml文件，转成txt格式的识别格式去做文字识别:filename '\t' image_content(exp:1234)
def get_rec_label():
	root = '/mnt/data/rz/data/register/clean/rec/v6/registration_number'
	error_path = os.path.join(root, 'error')
	img_root = os.path.join(root, 'images')
	xml_root = os.path.join(root, 'xml')
	xml_paths = glob(os.path.join(xml_root, '*.xml'))
	# xml_paths = []
	# for dr in range(8, 11):
	#     path = os.path.join(xml_root, str(dr), '*.xml')
	#     xml_paths.extend(glob(path))


	if not os.path.exists(error_path):
		os.makedirs(error_path)

	train_xml_paths = xml_paths
	train_xml_paths, valid_xml_paths = train_test_split(
		xml_paths, test_size=0.2, random_state=47)
	train_xml_paths = xml_paths
	def store(paths, label_path, suffix, img_root, error_path, img_store_root):
		results = []
		for xmlp in tqdm(paths):
			line, filename = voc_to_rec(xmlp, split_flag=',', suffix=suffix)
			img_path = os.path.join(img_root, filename)
			if line is not None:
				results.append(line)
				if os.path.exists(img_path):
					shutil.copy(img_path, img_store_root)
			else:
				if os.path.exists(img_path):
					shutil.move(img_path, error_path)
		with open(label_path, 'w') as f:
			f.write('\n'.join(results))
	train_dir_name = 'truth_images_train'
	train_img_store_root = os.path.join(root, train_dir_name)
	valid_dir_name = 'truth_images_test'
	valid_img_store_root = os.path.join(root, valid_dir_name)
	train_label_path = os.path.join(root, 'train_rec_gt_label.txt')
	valid_label_path = os.path.join(root, 'test_rec_gt_label.txt')
	if not os.path.exists(train_img_store_root):
		os.makedirs(train_img_store_root)
	if not os.path.exists(valid_img_store_root):
		os.makedirs(valid_img_store_root)
	store(train_xml_paths, train_label_path, train_dir_name,
		  img_root, error_path, img_store_root=train_img_store_root)
	store(valid_xml_paths, valid_label_path, valid_dir_name,
		  img_root, error_path, img_store_root=valid_img_store_root)


def icdar_to_yolov5():
	txt_root = '/mnt/data/rz/data/idCard/v2/yolo_format_labels'
	img_root = '/mnt/data/rz/data/idCard/v2/images'
	txt_store_root = '/mnt/data/rz/data/idCard/v2/labels'
	if not osp.exists(txt_store_root):
		os.makedirs(txt_store_root)
	txt_paths = glob(osp.join(txt_root, '*.txt'))
	split_flag = '\t'
	filter_class = ['Advertisement', 'Card']
	# class_names = ['number', 'owner', 'frame_number', 'registration_number',
	# 				'manner', 'property', 'cover_code', 'cover_number']
	# class_names = ['List Item', 'Toolbar', 'Video', 'Background Image', 'Radio Button', 'On/Off Switch', 'Button Bar', 'Multi-Tab', 'Icon', 'Input', 'Modal', 'Checkbox',
	#     'Number Stepper', 'Pager Indicator', 'Date Picker', 'Text Button', 'Slider', 'Image', 'Drawer', 'Bottom Navigation', 'Text', 'Web View', 'Map View']
	class_names = ('name', 'sex', 'birthday', 'address', 'number', 'authority', 'validity', 'nation')
	class_names_map = {'出生':'birthday', '公民身份号码':'number', '失效日期':'validity', '姓名':'name', '性别':'sex', '住址':'address', '签发日期':'validity', '签发机关':'authority', '民族':'nation'}
	class_idx = {cls: str(idx) for idx, cls in enumerate(class_names)}
	for txtp in tqdm(txt_paths):
		suffix = osp.basename(txtp).split('.')[0]
		imgn = suffix + '.jpg'
		imgp = osp.join(img_root, imgn)
		imgH, imgW = cv2.imread(imgp).shape[:2]
		new_lines = []
		with open(txtp) as f:
			for line in f:
				line = line.strip().split(split_flag)
				if len(line) == 2:
					loc, cls = line[0].split(','), line[-1]
				else:
					loc, cls = line[0], line[-1]
				cls = class_names_map[cls]
				loc = loc.split(',')
				if cls in filter_class:
					continue
				loc = list(map(float, loc))
				loc = list(map(int, loc))
				if len(loc) == 4:
					loc = [loc[0], loc[1], loc[2], loc[1], loc[2], loc[3], loc[0], loc[3]]
				loc = sort_box(loc) # sort the box points orders
				xmin, ymin, xmax, ymax = loc[0], loc[1], loc[4], loc[5]
				dw, dh = 1. / imgW, 1 / imgH
				x = (xmin + xmax)/2
				y = (ymin + ymax)/2
				w = xmax - xmin
				h = ymax - ymin
				x = x * dw
				w = w * dw
				y = y * dh
				h = h * dh
				idx = class_idx[cls]
				new_line = ' '.join([idx,
										str(truncate(x, 7)),
										str(truncate(y, 7)),
										str(truncate(w, 7)),
										str(truncate(h, 7))])
				new_lines.append(new_line)
		txt_store_path = osp.join(txt_store_root, suffix + '.txt')
		with open(txt_store_path, 'w') as f:
			f.write('\n'.join(new_lines))


if __name__ == "__main__":
	get_icdar_label()
