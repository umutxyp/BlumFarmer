import cv2
import mss
import numpy as np
import os
import pyautogui

def launch_button(window):
    with mss.mss() as sct:
        while True:
            rect = window.rectangle()

            monitor = {
                "top": rect.top,
                "left": rect.left,
                "width": rect.width(),
                "height": rect.height()
            }

            img = np.array(sct.grab(monitor))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            gray_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

            template = cv2.imread(os.path.join("assets", "launch_blum_button.png"), cv2.IMREAD_GRAYSCALE)

            result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)

            locations = np.where(result >=  0.8)

            w, h = template.shape[::-1]

            for pt in zip(*locations[::-1]):
                center_x = pt[0] + w // 2 + monitor["left"]
                center_y = pt[1] + h // 2 + monitor["top"]

                pyautogui.click(center_x, center_y)
                return