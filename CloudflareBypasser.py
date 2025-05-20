import time
from DrissionPage import ChromiumPage
import pyautogui
import datetime
import random
from datetime import datetime

import cv2,os
import pytesseract


file_path = "images"
file_suffix = "PNG"
def check_path(file_path):
    if file_path and not os.path.exists(file_path):
        os.makedirs(file_path)

class CloudflareBypasser:
    def __init__(self, driver: ChromiumPage, max_retries=-1, log=True):
        self.driver = driver
        self.max_retries = max_retries
        self.log = log

    def search_recursively_shadow_root_with_iframe(self,ele):
        if ele.shadow_root:
            if ele.shadow_root.child().tag == "iframe":
                return ele.shadow_root.child()
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_iframe(child)
                if result:
                    return result
        return None

    def search_recursively_shadow_root_with_cf_input(self,ele):
        if ele.shadow_root:
            if ele.shadow_root.ele("tag:input"):
                return ele.shadow_root.ele("tag:input")
        else:
            for child in ele.children():
                result = self.search_recursively_shadow_root_with_cf_input(child)
                if result:
                    return result
        return None
    
    def locate_cf_button(self):
        button = None
        eles = self.driver.eles("tag:input")
        for ele in eles:
            if "name" in ele.attrs.keys() and "type" in ele.attrs.keys():
                if "turnstile" in ele.attrs["name"] and ele.attrs["type"] == "hidden":
                    button = ele.parent().shadow_root.child()("tag:body").shadow_root("tag:input")
                    break
            
        if button:
            return button
        else:
            # If the button is not found, search it recursively
            self.log_message("Basic search failed. Searching for button recursively.")
            ele = self.driver.ele("tag:body")
            iframe = self.search_recursively_shadow_root_with_iframe(ele)
            if iframe:
                button = self.search_recursively_shadow_root_with_cf_input(iframe("tag:body"))
            else:
                self.log_message("Iframe not found. Button search failed.")
            return button

    def log_message(self, message):
        if self.log:
            print(message)

    def click_verification_button(self):
        try:
            button = self.locate_cf_button()
            if button:
                self.log_message("Verification button found. Attempting to click.")
                # Location = pyautogui.position()  # 通过这个得出全屏状态下，选择框的位置x,y
                # pyautogui.click(Location)
                button.click()
            else:
                self.log_message("Verification button not found.")

        except Exception as e:
            self.log_message(f"Error clicking verification button: {e}")

    def is_bypassed(self):
        try:
            title = self.driver.title.lower()
            return "just a moment" not in title
        except Exception as e:
            self.log_message(f"Error checking page title: {e}")
            return False

    def get_click_xy(self, image_path):
        image = cv2.imread(image_path)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # 设置轮廓的最小和最大面积
        min_area = 10000
        max_area = 100000

        contour_xy = set()
        scontour_xy = set()
        click_xy = set()

        # 遍历所有轮廓并绘制矩形框
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(contour)
                roi = gray[y: y + h, x: x + w]  # 提取轮廓区域
                text = pytesseract.image_to_string(roi)  #
                # print("text", text)
                if "verify you are human" in text.lower():  # 检查是否包含目标文本
                    # print("大轮廓定位成功")
                    # print("text", x, y, w, h , text)
                    x, y, w, h = cv2.boundingRect(contour)
                    roi = gray[y: y + h, x: x + w]  # 提取大轮廓区域

                    # 在大轮廓区域内再次进行边缘检测和小轮廓查找
                    roi_edges = cv2.Canny(roi, 50, 150)
                    small_contours, _ = cv2.findContours(roi_edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    # 判断是否存在按钮
                    contour_xy.add((x, y, w, h))  # 大轮廓轮廓

                    for small_contour in small_contours:
                        small_area = cv2.contourArea(small_contour)
                        if 500 < small_area < 5000:  # 小轮廓的面积范围
                            # print("小轮廓定位成功")

                            sx, sy, sw, sh = cv2.boundingRect(small_contour)
                            # print("texts", sx, sy, sw, sh)
                            scontour_xy.add((x + sx, y + sy, sw, sh))  # 小轮廓
                            contour_xy.add((x, y, w, h))  # 大轮廓轮廓

        for x, y, w, h in contour_xy.union(scontour_xy):
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for x, y, w, h in contour_xy:
            # 大轮廓中寻找点击位置（点击位置可在小轮廓外层）
            click_x = x + random.randint(int(w * 0.06), int(w * 0.2))
            click_y = y + random.randint(int(h * 0.47), int(h * 0.53))
            cv2.circle(image, (click_x, click_y), 5, (0, 0, 255), -1)
            click_xy.add((click_x, click_y))
            cv2.imwrite(image_path + ".click.png", image)  # 保存图片

        # # 使用Tesseract进行OCR识别
        # text = pytesseract.image_to_string(gray)
        #
        # # 显示图像
        # cv2.imshow('Detected Components', image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return click_xy


    def bypass_pic(self):
        import pyautogui

        for i in range(100):

            print('jietu')
            # 截取整个屏幕的截图

            screenshot = pyautogui.screenshot()
            file_name = datetime.now().strftime("%Y%m%d.%H_%M_%S")

            screenshot_path = f"{file_path}/{file_name}.{file_suffix}"
            screenshot.save(screenshot_path)

            for click_x, click_y in self.get_click_xy(screenshot_path):
                pyautogui.moveTo(click_x / 2, click_y / 2, duration=1, tween=pyautogui.easeInOutQuad)
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(3)


    def bypass(self):
        
        try_count = 0

        while not self.is_bypassed():
            if 0 < self.max_retries + 1 <= try_count:
                self.log_message("Exceeded maximum retries. Bypass failed.")
                break

            self.log_message(f"Attempt {try_count + 1}: Verification page detected. Trying to bypass...")
            self.click_verification_button()

            try_count += 1
            time.sleep(2)

        if self.is_bypassed():
            self.log_message("Bypass successful.")
        else:
            self.log_message("Bypass failed.")
