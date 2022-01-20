import os
import datetime
from PIL import Image
import numpy as np


def remove(picArray):
        '''
        以下是加深150以下的 并且不相等的
        '''
        red_data = picArray[..., 0]
        green_data = picArray[..., 1]
        blue_data = picArray[..., 2]
        red_green = red_data - green_data
        red_blue = red_data - blue_data
        red_150_1 = np.int64(red_data < 160)
        green_150_1 = np.int64(green_data < 150)
        blue_150_1 = np.int64(blue_data < 150)
        red_green_1 = np.int64(red_green != 0)
        black_150_index = np.where(
            red_150_1 + green_150_1 + blue_150_1 + red_green_1 == 4)
        picArray[black_150_index] = [0, 0, 0]
        '''
        以下是加深100以下 并且相等值的
        '''
        red_data = picArray[..., 0]
        green_data = picArray[..., 1]
        blue_data = picArray[..., 2]
        red_green = red_data - green_data
        red_blue = red_data - blue_data
        red_100_1 = np.int64(red_data < 100)
        red_green_100 = np.int64(red_green == 0)
        red_blue_100 = np.int64(red_blue == 0)
        black_100_index = np.where(
            red_100_1 + red_green_100 + red_blue_100 == 3)
        picArray[black_100_index] = [0, 0, 0]
        '''
        以下是红色情况的去除
        '''
        red_data = picArray[..., 0]
        green_data = picArray[..., 1]
        blue_data = picArray[..., 2]
        red_green = red_data - green_data
        red_blue = red_data - blue_data
        red_green1 = np.int64(red_green > 10)
        red_blue1 = np.int64(red_blue > 10)
        red_index = np.where(red_green1 + red_blue1 == 2)
        picArray[red_index] = [255, 255, 255]
        '''
        以下是去除200以上的
        '''
        red_data = picArray[..., 0]
        green_data = picArray[..., 1]
        blue_data = picArray[..., 2]
        red_green = red_data - green_data
        red_blue = red_data - blue_data
        red_200_1 = np.int64(red_data > 200)
        green_200_1 = np.int64(green_data > 200)
        blue_200_1 = np.int64(blue_data > 200)
        white_200_index = np.where(red_200_1 + green_200_1 + blue_200_1 == 3)
        picArray[white_200_index] = [255, 255, 255]
        return picArray