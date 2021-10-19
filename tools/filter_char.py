import re
 
 
def find_chinese(file):
	pattern = re.compile(r'[^\u4e00-\u9fa5]')
	chinese = re.sub(pattern, '', file)
	return chinese
 
def find_unchinese(file):
	pattern = re.compile(r'[\u4e00-\u9fa5]')
	unchinese = re.sub(pattern,"",file)
	return unchinese