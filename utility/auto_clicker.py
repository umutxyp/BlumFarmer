import os
import time
import random
import math
import cv2
import keyboard
import mss
import numpy as np
import pygetwindow as gw
import win32api
import win32con
import win32gui
import warnings
from pywinauto import Application

warnings.filterwarnings("ignore", category=UserWarning, module='pywinauto')

class AutoClicker:
    def __init__(self, hwnd, target_colors_hex, nearby_colors_hex, threshold, target_percentage, collect_freeze):
        self.hwnd = hwnd
        self.target_colors_hex = target_colors_hex
        self.nearby_colors_hex = nearby_colors_hex
        self.threshold = threshold
        self.target_percentage = target_percentage
        self.collect_freeze = collect_freeze
        self.running = False
        self.clicked_points = []
        self.iteration_count = 0
        self.last_check_time = time.time()
        self.last_freeze_check_time = time.time()
        self.freeze_cooldown_time = 0

    @staticmethod
    def hex_to_hsv(hex_color):
        hex_color = hex_color.lstrip('#')
        h_len = len(hex_color)
        rgb = tuple(int(hex_color[i:i + h_len // 3], 16) for i in range(0, h_len, h_len // 3))
        rgb_normalized = np.array([[rgb]], dtype=np.uint8)
        hsv = cv2.cvtColor(rgb_normalized, cv2.COLOR_RGB2HSV)
        return hsv[0][0]

    @staticmethod
    def click_at(x, y):
            if not (0 <= x < win32api.GetSystemMetrics(0) and 0 <= y < win32api.GetSystemMetrics(1)):
                raise
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def toggle_script(self):
        self.running = not self.running
        r_text = "Açık" if self.running else "Kapalı"

    def is_near_color(self, hsv_img, center, target_hsvs, radius=8):
        x, y = center
        height, width = hsv_img.shape[:2]
        for i in range(max(0, x - radius), min(width, x + radius + 1)):
            for j in range(max(0, y - radius), min(height, y + radius + 1)):
                distance = math.sqrt((x - i) ** 2 + (y - j) ** 2)
                if distance <= radius:
                    pixel_hsv = hsv_img[j, i]
                    for target_hsv in target_hsvs:
                        if np.allclose(pixel_hsv, target_hsv, atol=[1, 50, 50]):
                            return True
        return False

    def click_color_areas(self):
        app = Application().connect(handle=self.hwnd)
        window = app.window(handle=self.hwnd)
        window.set_focus()

        target_hsvs = [self.hex_to_hsv(color) for color in self.target_colors_hex]
        nearby_hsvs = [self.hex_to_hsv(color) for color in self.nearby_colors_hex]

        with mss.mss() as sct:
            keyboard.add_hotkey('F6', self.toggle_script)

            while True:
                if self.running:
                    rect = window.rectangle()
                    monitor = {
                        "top": rect.top,
                        "left": rect.left,
                        "width": rect.width(),
                        "height": rect.height()
                    }
                    img = np.array(sct.grab(monitor))
                    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

                    for target_hsv in target_hsvs:
                        lower_bound = np.array([max(0, target_hsv[0] - 1), 30, 30])
                        upper_bound = np.array([min(179, target_hsv[0] + 1), 255, 255])
                        mask = cv2.inRange(hsv, lower_bound, upper_bound)
                        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                        num_contours = len(contours)
                        num_to_click = int(num_contours * self.target_percentage)
                        contours_to_click = random.sample(contours, num_to_click)

                        for contour in reversed(contours_to_click):
                            if cv2.contourArea(contour) < 6:
                                continue

                            M = cv2.moments(contour)
                            if M["m00"] == 0:
                                continue
                            cX = int(M["m10"] / M["m00"]) + monitor["left"]
                            cY = int(M["m01"] / M["m00"]) + monitor["top"]

                            if not self.is_near_color(hsv, (cX - monitor["left"], cY - monitor["top"]), nearby_hsvs):
                                continue

                            if any(math.sqrt((cX - px) ** 2 + (cY - py) ** 2) < 35 for px, py in self.clicked_points):
                                continue
                            cY += 5
                            self.click_at(cX, cY)
                            self.clicked_points.append((cX, cY))

                    if self.collect_freeze:
                     self.check_and_click_freeze_button(sct, monitor)

                     window.set_focus()
                     rect = win32gui.GetWindowRect(self.hwnd)
                    center_x = (rect[0] + rect[2]) // 2
                    center_y = (rect[1] + rect[3]) // 2
                    win32api.SetCursorPos((center_x, center_y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120)
                    self.check_and_click_new_object(sct, monitor)
                    self.check_and_click_new_object2(sct, monitor)

                    time.sleep(0.1)
                    self.iteration_count += 1
                    if self.iteration_count >= 5:
                        self.clicked_points.clear()
                        self.iteration_count = 0

    def check_and_click_freeze_button(self, sct, monitor):
        freeze_colors_hex = ["#82dce9", "#55ccdc"] 
        freeze_hsvs = [self.hex_to_hsv(color) for color in freeze_colors_hex]
        current_time = time.time()
        if current_time - self.last_freeze_check_time >= 1 and current_time >= self.freeze_cooldown_time:
            self.last_freeze_check_time = current_time
            img = np.array(sct.grab(monitor))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            for freeze_hsv in freeze_hsvs:
                lower_bound = np.array([max(0, freeze_hsv[0] - 1), 30, 30])
                upper_bound = np.array([min(179, freeze_hsv[0] + 1), 255, 255])
                mask = cv2.inRange(hsv, lower_bound, upper_bound)
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) < 3:
                        continue

                    M = cv2.moments(contour)
                    if M["m00"] == 0:
                        continue
                    cX = int(M["m10"] / M["m00"]) + monitor["left"]
                    cY = int(M["m01"] / M["m00"]) + monitor["top"]

                    self.click_at(cX, cY)
                    self.freeze_cooldown_time = time.time() + 4  
                    return
                
    def check_and_click_new_object2(self, sct, monitor):
        new_object_colors_hex = ["#EC6376", "#FF7787"]
        new_object_hsvs = [self.hex_to_hsv(color) for color in new_object_colors_hex]

        img = np.array(sct.grab(monitor))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        for new_object_hsv in new_object_hsvs:
            lower_bound = np.array([max(0, new_object_hsv[0] - 1), 30, 30])
            upper_bound = np.array([min(179, new_object_hsv[0] + 1), 255, 255])
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < 3:
                    continue

                M = cv2.moments(contour)
                if M["m00"] == 0:
                    continue
                cX = int(M["m10"] / M["m00"]) + monitor["left"]
                cY = int(M["m01"] / M["m00"]) + monitor["top"]
                self.click_at(cX, cY)
                return

    def check_and_click_new_object(self, sct, monitor):
     template_path = os.path.join(os.path.dirname(__file__), "image.png")
    
     template_img = cv2.imread(template_path)
     if template_img is None:
        print("Şablon resmi yüklenemedi!")
        return

     img = np.array(sct.grab(monitor))
     img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
     result = cv2.matchTemplate(img_bgr, template_img, cv2.TM_CCOEFF_NORMED)
    
     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
     threshold = 0.8
     if max_val >= threshold:
        top_left = max_loc
        h, w = template_img.shape[:2]
        cX = top_left[0] + w // 2 + monitor["left"]
        cY = top_left[1] + h // 2 + monitor["top"]
        self.click_at(cX, cY)
