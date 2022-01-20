from stamp.remove import remove
from skew.clipper import clipper
from skew.deskew import deskewImage
from denoise.image_denoise import deHaze, noise
from denoise.water_mark import remove_water_mark

import os
import argparse

import cv2
import numpy as np


class preprocess:
    
    def __init__(self, cfg):
        self.cfg = cfg
        self.imgp = cfg.img_path
        self.output_dir = cfg.output
        self.remove_stamp_flag = cfg.stamp
        self.skew_flag = cfg.skew
        self.noise_flag = cfg.noise
        self.haze_flag = cfg.haze
        self.angle_flag = cfg.angle
        self.water_flag = True if len(cfg.water) > 0 else False
        
        
    def store(self, img):
        imgn = os.path.basename(self.imgp)
        storep = os.path.join(self.output_dir, imgn)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        cv2.imwrite(storep, img)
        
    def process(self):
        img = cv2.imread(self.imgp)

        if self.skew_flag: #去背景，并作仿射变换
            img = clipper(img)
        if self.angle_flag:
            img = deskewImage(img) # 方向矫正
        if self.remove_stamp_flag:
            img = remove(np.copy(img)) # 去红章
        if self.noise_flag: # 去噪声
            img = noise(img)
        if self.haze_flag: # 去雾
            img = deHaze(img)
        if self.water_flag:
            water_pixel = tuple(int(px) for px in self.cfg.water[0].split(',')) # 水印像素点RGB通道的和
            background_pixel = tuple(int(px) for px in self.cfg.water[1].split(',')) # 水印像素点RGB通道的和
            img = remove_water_mark(img, water_pixel, background_pixel)

        self.store(img) #存储



class Parser():
    """Defining and parsing command-line arguments"""
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.__add_arguments()

    def __add_arguments(self) -> None:
        """ Add arguments to the parser """
        self.parser.add_argument("--img_path", help="Input image path")
        self.parser.add_argument("--output", help="Output folder")
        self.parser.add_argument("--stamp", action='store_true', help="remove the red stamp")
        self.parser.add_argument("--haze", action='store_true', help="remove the haze of the image")
        self.parser.add_argument("--angle", action='store_true', help="rotate the image text angle")
        self.parser.add_argument("--noise", action='store_true', help="remove the noise of the image")
        self.parser.add_argument("--skew", action='store_true', help="cut the object image from background image")
        self.parser.add_argument("--water", default=[], nargs=argparse.REMAINDER, help="water color pixel and background color pixel.eg:'200,200,200' '255,255,255'  water mask pixel and background pixel")

        return

    def parse_arguments(self) -> argparse.Namespace:
        """ Parse arguments """
        return self.parser.parse_args()


if __name__ == '__main__':
    parser = Parser()
    args = parser.parse_arguments()
    pprocess = preprocess(args)
    pprocess.process()