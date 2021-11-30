import numpy as np
import cv2




def draw_text_det_res(dt_boxes, img):
    for box in dt_boxes:
        if len(box) == 4:
            box = [box[0], box[1], box[2], box[1],
                   box[2], box[3], box[0], box[3]]
        box = np.array(box).astype(np.int32).reshape(-1, 2)
        cv2.polylines(img, [box], True, color=(255, 255, 0), thickness=2)
    return img
