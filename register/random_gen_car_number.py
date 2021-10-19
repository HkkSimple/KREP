import random
import string




def gen(length):
	#数字
	num = string.digits
	#大写字母
	en = string.ascii_uppercase
	en = en.replace('I', '') # 不允许使用I跟O
	en = en.replace('O', '')
	print(en)
	#车牌省份
	province = '京津沪渝蒙新藏宁桂港澳黑吉辽晋冀青鲁豫苏皖浙闽赣湘鄂粤琼甘陕贵云川'

	#首位是车牌省份
	first = random.choice(province)
	#第二位字母
	seconde = random.choice(en)
	#第三部分5位或者6位的数字与字母
	third = [random.choice(num+en) for _ in range(length-2)]
	third = ''.join(third)
	result = first + seconde + third
	return result


if __name__ == "__main__":
	source_store_path = '/mnt/data/rz/programe/TextRecognitionDataGenerator/trdg/texts/register/car_id.txt'
	number = 1000000
	gen(7)
	# with open(source_store_path, 'a') as f:
	# 	for _ in range(number):
	# 		result = gen(7)
	# 		f.write(result+'\n')
