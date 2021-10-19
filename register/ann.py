import os
from glob import glob

# root = '/mnt/data/rz/data/register/gen/20210811/train/images'
# suffix = 'sub_image/'
# ann_store_path = '/mnt/data/rz/data/register/gen/20210811/train/person_img_label.txt'
# img_paths = glob(os.path.join(root, '*.jpg'))
# img_names = [os.path.basename(p) for p in img_paths]
# imgp_ann = [os.path.join(suffix, name) + '\t' + ''.join(ch for ch in name.split('_')[0] if ch != ' ')
# 				for name in img_names]
# with open(ann_store_path, 'w') as f:
# 	f.write('\n'.join(imgp_ann))

# max_len = max([len(name.split('_')[0]) for name in img_names])
# print(max_len)

# # =============================

root = '/mnt/data/rz/data/register/rec/gen/20210913'
dr = 'gen_train_20210913'
ann_file_name = 'gen_train_20210913_rec_gt_label.txt'
ann_store_path = os.path.join(root, ann_file_name)

img_paths = glob(os.path.join(root, dr, '*.jpg'))
img_names = [os.path.basename(p) for p in img_paths]
imgp_ann = [os.path.join(dr, name) + '\t' + ''.join(ch for ch in name.split('_')[0] if ch != ' ')
				for name in img_names]

with open(ann_store_path, 'w') as f:
	f.write('\n'.join(imgp_ann))

max_len = max([len(name.split('_')[0]) for name in img_names])
print(max_len)

# =============================

# path = '/mnt/data/rz/data/register/gen/20210811/train/person_img_label.txt'
# suffix = 'sub_image/'
# lines = []
# with open(path) as f:
# 	for line in f:
# 		name, ct = line.strip().split('\t')
# 		new_line = os.path.join(suffix ,name) + '\t' + ct
# 		lines.append(new_line)
# with open('/mnt/data/rz/data/register/gen/20210811/train/person_img_label.txt', 'w') as f:
# 	f.write('\n'.join(lines))
