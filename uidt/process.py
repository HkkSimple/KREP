import os
import shutil
from glob import glob
from tqdm import tqdm

# path = '/mnt/data/rz/data/register/rec/truth/test_rec_gt_label.txt'
# path = '/mnt/data/rz/data/register/rec/truth/rec_gt_label.txt'
# img_store = '/mnt/data/rz/data/register/rec/truth/number_images'
# root = '/mnt/data/rz/data/register/rec/truth/'


# if not os.path.exists(img_store):
# 	os.makedirs(img_store)

# lines = []
# max_len = 0
# with open(path) as f:
# 	for line in f:
# 		items = line.strip().split('\t')
# 		if len(items) != 2:
# 			print('error line:', line)
# 		else:
# 			filename, ct = items
# 			flag = True
# 			for ch in ct:
# 				if ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
# 					flag = False
# 					break

# 			if len(ct) == 12 and flag:
# 				img_path = os.path.join(root, filename)
# 				shutil.copy(img_path, img_store)

# 				imgn = os.path.basename(filename)
# 				line = os.path.join('number_images', imgn) + '\t' + ct
# 				lines.append(line)

# with open(os.path.join(root, 'number_rec_gt_label.txt'), 'w') as f:
# 	f.write('\n'.join(lines))


# ========

# root = '/mnt/data/rz/data/register/clean/rec/vin_plate/'
# paths = glob(os.path.join(root, 'label/*.txt'))
# pre_label_dir_name = 'pre_labels.txt'
# result = []
# for path in paths:
# 	with open(path) as f:
# 		ct = f.read().strip()
# 	if len(ct) == 0:
# 		continue
# 	imgn = os.path.basename(path).split('.')[0] + '.jpg'
# 	line = imgn + '\t' + ct
# 	result.append(line)

# with open(os.path.join(root, pre_label_dir_name), 'w') as f:
# 	f.write('\n'.join(result))

# ==========
# img_root = '/mnt/data/rz/data/register/exp/rec/exp/gen_test_20210910/'
# dst_root = '/mnt/data/rz/data/register/exp/rec/exp/gen_train_20210913/'
# img_paths = glob(os.path.join(img_root, '*.jpg'))
# for imgp in tqdm(img_paths):
# 	shutil.copy(imgp, dst_root)

# ===========
# total = []
# root = '/mnt/data/rz/data/register/exp/rec/exp/gen_test_20210910_rec_gt_label.txt'
# with open(root) as f:
# 	test_contents = f.read().strip().split('\n')

# root = '/mnt/data/rz/data/register/exp/rec/exp/gen_train_20210913_rec_gt_label.txt'
# with open(root) as f:
# 	train_contents = f.read().strip().split('\n')

# total = train_contents + test_contents
# ===========

with open('/mnt/data/rz/data/register/exp/rec/exp/gen_train_rec_gt_label.txt') as f:
	total = f.read().strip().split('\n')
new_lines = []
max_len = 0
for line in total:
	name, ct = line.strip().split('\t')
	name = name.strip().split('/')[-1]
	new_line = 'gen_train_images' + '/' + name + '\t' + ct
	# new_lines.append(new_line)
	max_len = max([max_len, len(ct)])
	if len(ct) == 19:
		print('name:',name, '====', ct)

# print('max_len:', max_len)

# with open('/mnt/data/rz/data/register/exp/rec/exp/gen_train_rec_gt_label_bk.txt', 'w') as f:
# 	f.write('\n'.join(new_lines))

# ========

# for txtp in glob('/mnt/data/rz/data/register/exp/det/20211014/labels/*.txt'):
# 	name = os.path.basename(txtp)
# 	imgn = name.replace('txt', 'jpg')
# 	imgp = os.path.join('/mnt/data/rz/data/register/exp/det/20211014/images', imgn)
# 	with open(txtp) as f:
# 		content = f.read().strip().split('\n')
# 	if len(content) < 3:
# 		cover_store_root = '/mnt/data/rz/data/register/exp/det/20211014/cover'
# 		shutil.move(txtp, cover_store_root)
# 		shutil.move(imgp, cover_store_root)


# split dataset
# =======
# from sklearn.model_selection import train_test_split

# root = '/mnt/data/rz/data/register/exp/det/20211014/labels'
# paths = glob(os.path.join(root, '*.txt'))
# suffixes = [os.path.basename(p).split('.')[0] for p in paths]

# train_suffix, valid_suffix = train_test_split(suffixes, test_size=0.6, shuffle=True, random_state=47)

# for suf in train_suffix:
# 	shutil.copy(os.path.join('/mnt/data/rz/data/register/exp/det/20211014/images',
# 	            suf+'.jpg'), '/mnt/data/rz/data/register/exp/det/20211014/train')
# 	shutil.copy(os.path.join('/mnt/data/rz/data/register/exp/det/20211014/labels',
# 	            suf+'.txt'), '/mnt/data/rz/data/register/exp/det/20211014/train')

# for suf in valid_suffix:
# 	shutil.copy(os.path.join('/mnt/data/rz/data/register/exp/det/20211014/images',
# 	            suf+'.jpg'), '/mnt/data/rz/data/register/exp/det/20211014/val')
# 	shutil.copy(os.path.join('/mnt/data/rz/data/register/exp/det/20211014/labels',
# 	            suf+'.txt'), '/mnt/data/rz/data/register/exp/det/20211014/val')

txt_path = glob('/mnt/data/rz/data/UIDetect/sap/elements/labels/train/*.txt')
org_img_root = '/mnt/data/rz/data/UIDetect/sap/elements/images'
dst_img_root = '/mnt/data/rz/data/UIDetect/sap/elements/'
for txtp in txt_path:
	name = os.path.basename(txtp)
	imgn = name.replace('txt', 'png')
	org_imgp = os.path.join(org_img_root, imgn)
	dst_imgp = '/mnt/data/rz/data/UIDetect/sap/elements/train'
	shutil.move(org_imgp, dst_imgp)

