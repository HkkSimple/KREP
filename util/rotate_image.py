import cv2
import numpy as np


def rotate_bound(image, angle):
    '''
    . 旋转图片
    . @param image    opencv读取后的图像
    . @param angle    (顺)旋转角度
    '''

    (h, w) = image.shape[:2]  # 返回(高,宽,色彩通道数),此处取前两个值返回
    # 抓取旋转矩阵(应用角度的负值顺时针旋转)。参数1为旋转中心点;参数2为旋转角度,正的值表示逆时针旋转;参数3为各向同性的比例因子
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -angle, 1.0)
    # 计算图像的新边界维数
    newW = int((h * np.abs(M[0, 1])) + (w * np.abs(M[0, 0])))
    newH = int((h * np.abs(M[0, 0])) + (w * np.abs(M[0, 1])))
    # 调整旋转矩阵以考虑平移
    M[0, 2] += (newW - w) / 2
    M[1, 2] += (newH - h) / 2
    # 执行实际的旋转并返回图像
    return cv2.warpAffine(image, M, (newW, newH)) # borderValue 缺省，默认是黑色