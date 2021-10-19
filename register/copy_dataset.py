import os
from glob import glob
import shutil
from transforms import random_plot_line
import random


ann_file = './v1/rec_gt_label.txt'
image_root= './v1/truth_images'


dst_root = '/mnt/data/rz/data/register/rec/exp5'
dst_img_dir_name = 'truth_images'
dst_ann_file_name = 'truth_rec_gt_label.txt'

os.makedirs(os.path.join(dst_root, dst_img_dir_name), exist_ok=True)

#原标注文件
total = []
#复制图片与标注文件到指定位置
with open(ann_file) as f:
	for line in f:
		suffix, ct = line.strip().split('\t')
		name = suffix.strip().split('/')[-1]
		org_imgp  = os.path.join(image_root, name) # 原图像的存储路径
		# repeat copy images
		for i in range(5, 10):
			new_name = '{}_{}'.format(str(i), name)
			img_dst_path = os.path.join(dst_root, dst_img_dir_name, new_name)
			colors = [(108, 88, 82),
                      (175, 149, 138),
					  (136, 118, 121),
                      (136, 132, 126)]
			clr = random.choice(colors)
			lw = random.choice([1, 2, 3])
			img = random_plot_line(org_imgp, random_scale=1, 
								   color=clr, line_width=lw)
			img.save(img_dst_path)
			repeat_line = os.path.join(dst_img_dir_name, new_name) + '\t' + ct
			total.append(repeat_line)
		# random plot line to images
		for i in range(5):
			new_name = '{}_{}'.format(str(i), name)
			img_dst_path = os.path.join(dst_root, dst_img_dir_name, new_name)
			shutil.copy(org_imgp, img_dst_path)
			repeat_line = os.path.join(dst_img_dir_name, new_name) + '\t' + ct
			total.append(repeat_line)



dst_ann_path = os.path.join(dst_root, dst_ann_file_name)
with open(dst_ann_path, 'w') as f:
	f.write('\n'.join(total))
