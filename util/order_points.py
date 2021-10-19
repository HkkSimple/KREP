import numpy as np
from scipy.spatial import distance as dist


def _order_points(pts):
    # 根据x坐标对点进行排序
    x_sorted = pts[np.argsort(pts[:, 0]), :]

    # 从排序中获取最左侧和最右侧的点
    # x坐标点
    left_most = x_sorted[:2, :]
    right_most = x_sorted[2:, :]

    # 现在，根据它们的y坐标对最左边的坐标进行排序，这样我们就可以分别抓住左上角和左下角
    left_most = left_most[np.argsort(left_most[:, 1]), :]
    (tl, bl) = left_most

    # 现在我们有了左上角坐标，用它作为锚来计算左上角和右上角之间的欧氏距离;
    # 根据毕达哥拉斯定理，距离最大的点将是我们的右下角
    distance = dist.cdist(tl[np.newaxis], right_most, "euclidean")[0]
    (br, tr) = right_most[np.argsort(distance)[::-1], :]

    # 返回左上角，右上角，右下角和左下角的坐标
    return np.array([tl, tr, br, bl], dtype="float32")

# box: [x1, y1, x2, y2, x3, y3, x4, y4]
def sort_box(box):
    x1, y1, x2, y2, x3, y3, x4, y4 = box[:8]
    pts = (x1, y1), (x2, y2), (x3, y3), (x4, y4)
    pts = np.array(pts, dtype="float32")
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = _order_points(pts)

    return x1, y1, x2, y2, x3, y3, x4, y4
