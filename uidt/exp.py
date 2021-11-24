import pdqhash
import cv2
import os.path as osp
import numpy as np
import os
from glob import glob


def calcu_phash(h1, h2): 
	return 1 - (h1 - h2) / len(h1.hash) ** 2

root = 'elements/'
org_img_paths = glob(os.path.join(root, '000-0', '*.jpg'))
org_imgp = org_img_paths[0]
image = cv2.imread(org_imgp)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
org_vector, org_quality = pdqhash.compute(image)

distances = []
paths = []
dst_img_paths = glob(osp.join(root, '000-1', '*.jpg'))
for imgp in dst_img_paths:
	img = cv2.imread(imgp)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	dst_vector, dst_qulity = pdqhash.compute(img)
	dis = calcu_phash(org_vector, dst_vector)
	distances.append(dis)
	paths.append(imgp)

dst_rank = np.argsort(distances)[::-1]
for idx in dst_rank[:5]:
    p = paths[idx]
    im = cv2.imread(p)[:, :, ::-1]
    print('========= ', distances[idx], ' ========')
	

# Get all the rotations and flips in one pass.
# hash_vectors is a list of vectors in the following order
# - Original
# - Rotated 90 degrees
# - Rotated 180 degrees
# - Rotated 270 degrees
# - Flipped vertically
# - Flipped horizontally
# - Rotated 90 degrees and flipped vertically
# - Rotated 90 degrees and flipped horizontally
# hash_vectors, quality = pdqhash.compute_dihedral(image)

# Get the floating point values of the hash.
# hash_vector_float, quality = pdqhash.compute_float(image)
