import os
import requests
from io import BytesIO
from pyzbar import pyzbar
from PIL import Image, ImageEnhance
from pyzxing import BarCodeReader


def decode_by_zbar(img_path):
    """ 读取二维码的内容： img_adds：二维码地址（可以是网址也可是本地地址 """
    img = Image.open(img_path)
    txt_list = pyzbar.decode(img)
    results = []

    for txt in txt_list:
        barcodeData = txt.data.decode("utf-8")
        results.append(barcodeData)
    return results


def decode_by_zxin(img_path):
    reader = BarCodeReader()
    results = reader.decode(img_path)
    return results


if __name__ == '__main__':
    # 解析本地二维码
    result1 = decode_by_zbar('../data/2.jpg')
    result2 = decode_by_zxin('../data/2.jpg')
    print(result1)
    print(result2)
