import shutil
import os
from glob import glob
from tqdm import tqdm


org_img_root = '/mnt/data/rz/data/register/v2'
dst = '/mnt/data/rz/data/register/v2/1'
paths = glob(os.path.join(org_img_root, 'images', '*.jpg'))
for p in tqdm(paths[1005:]):
	shutil.copy(p, dst)
