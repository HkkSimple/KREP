import enum
import os
from glob import glob
from tqdm import tqdm
import xml.etree.ElementTree as ET



# 单个文字图片进行预标注，将其转成cvat中的labelme3.0的xml格式
def gen_cut_image_voc_format(template_xml_path, xml_path, content_dict, xml_store):
	with open(template_xml_path) as f:
		tree = ET.parse(f)
		root = tree.getroot()
	
	#获取原始xml的基础信息，从而将这些信息更新到模板xml中
	with open(xml_path) as f:
		new_tree = ET.parse(f)
		new_root = new_tree.getroot()
	new_filename = new_root.find('filename').text
	new_imgH = new_root.find('imagesize').find('nrows').text
	new_imgW = new_root.find('imagesize').find('ncols').text

	# 在模板的基础上，修改文件名
	filename = root.find('filename')  
	filename.text = new_filename     #修改标签内容
	#修改图片宽、高
	imgH = root.find('imagesize').find('nrows')
	imgW = root.find('imagesize').find('ncols')
	imgH.text = new_imgH
	imgW.text = new_imgW
	#修改polygon的值
	x1, y1, x2, y2, x3, y3, x4, y4 = '0', '0', new_imgW, '0', new_imgW, new_imgH, '0', new_imgH
	new_points = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
	polys = root.find('object').find('polygon').findall('pt')
	for i, pt in enumerate(polys):
		pt.find('x').text, pt.find('y').text = new_points[i]
	#修改attribute的值
	attr = root.find('object').find('attributes')
	attr.text = content_dict[new_filename]

	# store new xml
	# tree.write('test.xml', encoding="utf-8", xml_declaration=True)
	xmln = os.path.basename(xml_path)
	xml_store_path = os.path.join(xml_store, xmln)
	tree.write(xml_store_path)

# ===============================================================================
def get_cut_image_label():
	template_xml_path = '../data/template.xml'
	content_dict = {}

	pre_ann_file_path = '/mnt/data/rz/data/register/clean/rec/v6/idCard/pre_labels.txt'
	old_xml_root = '/mnt/data/rz/data/register/clean/rec/v6/idCard/xml'
	new_xml_root = '/mnt/data/rz/data/register/clean/rec/v6/idCard/new_xml'
	with open(pre_ann_file_path) as f:
		for line in f:
			item = line.strip().split('\t')
			if len(item) != 2:
				imgn = item[0]
				ct = ''
			else:
				imgn, ct = item
			content_dict[imgn] = 'text=' + "'" + ct # 加上一个空格，以防纯数字出现浮点格式化的问题
	xml_paths = glob(os.path.join(old_xml_root, '*.xml'))
	if not os.path.exists(new_xml_root):
		os.makedirs(new_xml_root)
	for xmlp in tqdm(xml_paths):
		gen_cut_image_voc_format(template_xml_path, xmlp, content_dict, new_xml_root)

def update_object(txtp, object_xml_path):
	objes = []
	if not os.path.exists(txtp):
		return objes
	with open(txtp) as f:
		for i, line in enumerate(f):
			loc, ct = line.strip().split('\t')
			loc = loc.strip().split(',')
			x1, y1, x2, y2, x3, y3, x4, y4 = loc
			new_points = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
			with open(object_xml_path) as objf:
				obj_root = ET.parse(objf).getroot()
				polys = obj_root.find('polygon').findall('pt')
			id = obj_root.find('id')
			id.text = str(i)
			for i, pt in enumerate(polys):
				pt.find('x').text, pt.find('y').text = new_points[i]
			attr = obj_root.find('attributes')
			attr.text = 'content=' + "'" + ct
			objes.append(obj_root)
	return objes



# 对整图进行ocr预标注，包括文字位置，文字内容。从icdar格式，转到cvat中的labelme3.0格式
def get_image_label():
	labels_root = '/mnt/data/rz/data/store/20211207/labels'
	object_xml_path = '../data/object.xml'
	xml_root = '/mnt/data/rz/data/store/20211207/xml/'
	xml_store_root_ = '/mnt/data/rz/data/store/20211207/pred_label/'
	for d in range(1, 6):
		xml_paths = glob(os.path.join(xml_root, str(d), '*.xml'))
		xml_store_root = os.path.join(xml_store_root_, str(d))
		if not os.path.exists(xml_store_root):
			os.makedirs(xml_store_root)

		for src_xmlp in tqdm(xml_paths):
			xmln = os.path.basename(src_xmlp)
			xml_store_path = os.path.join(xml_store_root, xmln)
			with open(src_xmlp) as f:
				tree = ET.parse(f)
				root = tree.getroot()
			imgn = root.find('filename').text
			txtn = imgn.split('.')[0] + '.txt'
			txtp = os.path.join(labels_root, txtn)
			objes = update_object(txtp=txtp, object_xml_path=object_xml_path)
			if len(objes) > 0:
				root.extend(objes)
			tree.write(xml_store_path, encoding='utf-8', xml_declaration=True)
			# tree.write('tt.xml', encoding='utf-8', xml_declaration=True)


if __name__ == "__main__":
	get_image_label()