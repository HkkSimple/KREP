from glob import glob
import os

paths = glob('/mnt/data/rz/data/idCard/v2/labels/*.txt')

classes = []
for p in paths:
	with open(p) as f:
		for line in f:
			line = line.strip().split('\t')
			cls = line[-1]
			classes.append(cls)


print(list(set(classes)))
