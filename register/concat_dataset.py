import os
from glob import glob
import shutil


total = []
with open("/mnt/data/rz/data/register/gen/20210809_train/new_rec_gt_train.txt") as f:
	lines = f.read().strip().split('\n')

for l in lines:
	nm, ct = l.strip().split('\t')
	name = os.path.basename(nm)
	line = name + '\t' + ct
	total.append(line)


with open('/mnt/data/rz/data/register/total/split_images/person_img_label.txt') as f:
	# sub_lines = f.read().strip().split('\n')
	sub_image_root = '/mnt/data/rz/data/register/total/split_images/sub_image'
	for line in f:
		if len(line.strip().split('\t')) ==1 :
			continue
		total.append(line.strip())
		name, ct = line.strip().split('\t')
		imgp  = os.path.join(sub_image_root, name)
		# repeat num
		for i in range(9):
			new_name = '{}_{}'.format(str(i), name)
			dst_path = os.path.join('/mnt/data/rz/data/register/gen/20210809_train/images_concat', new_name)
			shutil.copy(imgp, dst_path)
			repeat_line = new_name + '\t' + ct
			total.append(repeat_line)


with open('/mnt/data/rz/data/register/gen/20210809_train/image_concat_gt_train.txt', 'w') as f:
	f.write('\n'.join(total))
