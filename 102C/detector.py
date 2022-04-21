# encoding: utf-8
import cv2
import numpy as np

class Detector(object):

    def __init__(self):
        
        # self.fgbg = cv2.createBackgroundSubtractorMOG2(history=250, varThreshold=100, detectShadows=False)
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=250, varThreshold=100, detectShadows=False)

    def apply(self, frame):

        fgmask = self.fgbg.apply(frame)

        # 图像形态学操作
        # fgmask = cv2.erode(fgmask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)), iterations=1)
        fgmask = cv2.dilate(fgmask, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)), iterations=3)

        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(frame, contours, -1, (0, 255, 0))

        # 最小面积阈值
        # contours = [c for c in contours if cv2.contourArea(c) > 100]

        contours_area = np.zeros(0)
        if len(contours) > 0:
            for c in contours:
                contours_area = np.append(contours_area, cv2.contourArea(c))

            index_from_min = np.argsort(contours_area)
            x1, y1, w1, h1 = cv2.boundingRect(contours[index_from_min[-1]])

        center = None
        if len(contours) >= 2:
            x2, y2, w2, h2 = cv2.boundingRect(contours[index_from_min[-2]])
        
            x_new = min(x1, x2)
            y_new = min(y1, y2)
            w_new = max(x1+w1, x2+w2) - min(x1, x2)
            h_new = max(y1+h1, y2+h2) - min(y1, y2)
            # near enough
            if np.abs(x1+w1/2 - (x2+w2/2)) < 20 and np.abs(y1+h1/2 - (y2+h2/2)) < 80 \
                and contours_area[index_from_min[-2]] > 60 and h_new < 110:

                center = np.round(np.array([[x_new + w_new/2], [y_new + h_new/2]]))
                cv2.rectangle(frame, (x_new, y_new), (x_new + w_new, y_new + h_new), (0, 0, 255), 2)
            else:
                center = np.round(np.array([[x1 + w1/2], [y1 + h1/2]]))
                cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)

        elif len(contours) == 1:
            center = np.round(np.array([[x1 + w1/2], [y1 + h1/2]]))
            cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)

        return center, frame, fgmask
