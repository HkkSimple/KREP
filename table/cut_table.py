import os

import numpy as np
import cv2 as cv

def cut(img):
	# 灰度图片
	gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
	binary = cv.adaptiveThreshold(
		~gray, 1, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 35, -6)

	# 水平投影得到表格宽
	sumY = np.sum(binary, axis=1)
	indexY = np.where(sumY > 100)[0]
	#表格最上边与最下边
	top, bottom = indexY[0], indexY[-1]
	tableH = int(bottom - top)

	# 垂直投影得到表格长
	sumX = np.sum(binary, axis=0)
	indexX = np.where(sumX > 50)[0]
	#表格最左边与最右边
	left, right = indexX[0], indexX[-1]
	tableW = int(right - left)
	#切出表格图
	table_img = img[top:bottom, left:right, :]

	#切块
	for i, x in enumerate(range(0, tableW, tableH)):
		endX = min(x + tableH, tableW)
		block = table_img[3:(tableH-3), (x+2):(endX-10), :]
		# 存储数据
		imgn = str(i) + '.jpg'
		imgp = os.path.join('./data/table/table1', imgn)
		cv.imwrite(imgp, block)







def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs(np.dot(d1, d2) / np.sqrt(np.dot(d1, d1)*np.dot(d2, d2)))


def find_squares(img):
    squares = []
    img = cv.GaussianBlur(img, (3, 3), 0)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    bin = cv.Canny(gray, 30, 100, apertureSize=3)
    contours, _hierarchy = cv.findContours(
        bin, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    index = 0
    # 轮廓遍历
    centers = []
    for cnt in contours:
        cnt_len = cv.arcLength(cnt, True)  # 计算轮廓周长
        cnt = cv.approxPolyDP(cnt, 0.02*cnt_len, True)  # 多边形逼近
        # 条件判断逼近边的数量是否为4，轮廓面积是否大于1000，检测轮廓是否为凸的
        if len(cnt) == 4 and cv.contourArea(cnt) > 1000 and cv.isContourConvex(cnt):
            M = cv.moments(cnt)  # 计算轮廓的矩
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])  # 轮廓重心

            cnt = cnt.reshape(-1, 2)
            max_cos = np.max(
                [angle_cos(cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4]) for i in range(4)])
            # 只检测矩形（cos90° = 0）
            if max_cos < 0.1:
                # 检测四边形（不限定角度范围）
                # index = index + 1
				# 设置putText函数字体
				# font = cv.FONT_HERSHEY_SIMPLEX
				#计算两边夹角额cos值
                # cv.putText(img, ("#%d" % index), (cx, cy),
                #            font, 0.7, (255, 0, 255), 2)
                x1, x2 = np.min(cnt[:, 0]), np.max(cnt[:, 0])
                y1, y2 = np.min(cnt[:, 1]), np.max(cnt[:, 1])
                x1, y1, x2, y2 = list(map(int, [x1, y1, x2, y2]))
                cnt = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
                squares.append(cnt)
                centers.append([cx, cy])

    
    return squares, centers

if __name__ == '__main__':
	# 对水平表格框进行块切割
	img = cv.imread('./data/table/table1.jpg', 1)
	squares, centers = find_squares(img)
	squares = np.array(squares)
	if len(centers) != 1:
		cut(img)
	else:
		squares = squares[0]
		x1, x2 = np.min(squares[:, 0]), np.max(squares[:, 0])
		y1, y2 = np.min(squares[:, 1]), np.max(squares[:, 1])
		tableH = abs(y2-y1)
		tableW = abs(x2-x1)
		table_img = img[y1:y2, x1:x2, :]
		print(table_img.shape)
		for i, x in enumerate(range(0, tableW, tableH)):
			endX = min(x + tableH, tableW)
			block = table_img[3:(tableH-3), (x+2):(endX-10), :]
			print(block.shape)
			# 存储数据
			imgn = str(i) + '.jpg'
			imgp = os.path.join('./data/table/table1', imgn)
			cv.imwrite(imgp, block)