import os
import shutil
from glob import glob
from tqdm import tqdm

lines = []
paths = glob('/mnt/data/rz/data/UIDetect/sap/elements/element_detect/labels/*.txt')

for txtp in paths:
	lines = []
	name = os.path.basename(txtp)
	txtp2 = '/mnt/data/rz/data/UIDetect/sap/elements/text_detect/yolo_format/labels/' + name
	with open(txtp) as f:
		for line in f:
			line = line.strip()
			lines.append(line)

	with open(txtp2) as f:
		for line in f:
			line = line.strip()
			lines.append(line)


	with open('/mnt/data/rz/data/UIDetect/sap/elements/exp2/labels/'+name, 'w') as f:
		f.write('\n'.join(lines))
