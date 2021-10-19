import os
from glob import glob
from tqdm import tqdm
import xml.etree.ElementTree as ET



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

if __name__ == '__main__':
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
