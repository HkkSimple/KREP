import numpy as np
import cv2 as cv
import os
from copy import deepcopy


# 设置putText函数字体
font = cv.FONT_HERSHEY_SIMPLEX
#计算两边夹角额cos值


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
                index = index + 1
                # cv.putText(img, ("#%d" % index), (cx, cy),
                #            font, 0.7, (255, 0, 255), 2)
                x1, x2 = np.min(cnt[:, 0]), np.max(cnt[:, 0])
                y1, y2 = np.min(cnt[:, 1]), np.max(cnt[:, 1])
                x1, y1, x2, y2 = list(map(int, [x1, y1, x2, y2]))
                cnt = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
                squares.append(cnt)
                centers.append([cx, cy])

    
    return squares, centers, img


if __name__ == '__main__':
	# img = cv2.imread('./data/table/table2.jpg')
	# img = cv.imread('./data/table/table1.jpg')
	# squares, img = find_squares(img)
	# print('矩形数:', len(squares))
	# cv.drawContours(img, squares, -1, (0, 0, 255), 2)
	img = cv.imread('./data/table/table2.jpg')
	# img = cv.imread('./data/table/table1.jpg'	
	squares, centers, img = find_squares(img)
	centers = np.array(centers, dtype=np.int64)
	centers_squares_map = {','.join(map(str, pt)): sqr
						for pt, sqr in zip(centers, squares)}
	# cts = deepcopy(centers)
	sorted_centers = [','.join(map(str, sortCT)) 
					for sortCT in sorted(centers, key=lambda k: [k[1], k[0]])]
	
	for row in range(4):
		begin = row * 5
		end = (row+1) * 5
		line = sorted_centers[begin:end] # 每一行块元素的中心点信息
		X = [int(x.split(',')[0]) for x in line]
		# XX = deepcopy(X)
		sortedXX = sorted(X)
		# indexX = X.argsort()
		indexX = [sortedXX.index(x) for x in X]
		print(indexX)
		for col, ct in zip(indexX, line):
			rw, cl = str(row), str(col)
			imgn = rw + '_' + cl + '.jpg'
			imgp = os.path.join('./data/table/table2', imgn)
			loc = centers_squares_map[ct]
			x1, y1, x2, y2 = loc[0][0], loc[0][1], loc[2][0], loc[2][1]
			block_img = img[y1+2:y2-2, x1+2:x2-2, :]
			cv.imwrite(imgp, block_img)
