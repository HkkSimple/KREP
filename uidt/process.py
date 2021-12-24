import os
import shutil
from glob import glob
from tqdm import tqdm
from sklearn.model_selection import train_test_split

# lines = []
# paths = glob('/mnt/data/rz/data/UIDetect/sap/elements/element_detect/labels/*.txt')

# for txtp in paths:
# 	lines = []
# 	name = os.path.basename(txtp)
# 	txtp2 = '/mnt/data/rz/data/UIDetect/sap/elements/text_detect/yolo_format/labels/' + name
# 	with open(txtp) as f:
# 		for line in f:
# 			line = line.strip()
# 			lines.append(line)

# 	with open(txtp2) as f:
# 		for line in f:
# 			line = line.strip()
# 			lines.append(line)


# 	with open('/mnt/data/rz/data/UIDetect/sap/elements/exp2/labels/'+name, 'w') as f:
# 		f.write('\n'.join(lines))

# ===============

# img_paths = glob('/mnt/data/rz/data/UIDetect/exp/sap_u8_ctp/images/*')

# for imgp in img_paths:
# 	suffix = os.path.basename(imgp).split('.')[0]
# 	txtn = suffix + '.txt'
# 	txtp = os.path.join('/mnt/data/rz/data/UIDetect/exp/sap_u8_ctp/labels', txtn)
# 	if not os.path.exists(txtp):
# 		print(imgp)
# 		os.remove(imgp)

# ===============
img_paths = glob('/mnt/data/rz/data/UIDetect/exp/sap_u8_ctp/images/*')
suffix = [os.path.basename(imgp).split('.')[0] for imgp in img_paths]

train_suffix, val_suffx = train_test_split(suffix, test_size=0.1, random_state=47)

root = '/mnt/data/rz/data/UIDetect/exp/sap_u8_ctp'
store_root = os.path.join(root, 'data')
train_img_store_root = os.path.join(store_root, 'images', 'train')
val_img_store_root = os.path.join(store_root, 'images', 'val')
train_label_store_root = os.path.join(store_root, 'labels', 'train')
val_label_store_root = os.path.join(store_root, 'labels', 'val')



def move_file(sfx, flag='train'):
	org_img_root = '/mnt/data/rz/data/UIDetect/exp/sap_u8_ctp/images'
	org_label_root = '/mnt/data/rz/data/UIDetect/exp/sap_u8_ctp/labels'
	for sx in sfx:
		org_imgp = os.path.join(org_img_root, sx+'.png')
		if not os.path.exists(org_imgp):
			org_imgp = os.path.join(org_img_root, sx+'.jpg')
		org_txtp = os.path.join(org_label_root, sx + '.txt')
		if flag == 'train':
			shutil.copy(org_imgp, train_img_store_root)
			shutil.copy(org_txtp, train_label_store_root)
		elif flag == 'val':
			shutil.copy(org_imgp, val_img_store_root)
			shutil.copy(org_txtp, val_label_store_root)


move_file(train_suffix, flag='train')
move_file(val_suffx, flag='val')

# ==================

# for txtp in glob('/mnt/data/rz/data/UIDetect/exp/sap_u8_ctp/labels/*.txt'):
# 	with open(txtp) as f:
# 		for line in f:
# 			cls = line.strip().split()[0]
# 			if cls != '0':
# 				print(txtp, '  ', line)
# 				break
