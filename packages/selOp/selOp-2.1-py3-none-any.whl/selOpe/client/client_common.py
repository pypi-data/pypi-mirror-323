import time
from io import BytesIO

from PIL import Image
import pyautogui as pag
import requests


class ImageLoader:
    @staticmethod
    def load_image(pic_path):
        """加载图片，支持网络路径和本地路径"""
        if pic_path.startswith(('http://', 'https://')):
            response = requests.get(pic_path, stream=True)
            response.raise_for_status()
            image_data = BytesIO(response.content)
        else:
            image_data = pic_path

        return Image.open(image_data)


class ScreenInteraction:
    def __init__(self):
        self.image_loader = ImageLoader()

    def find_pic(self, pic_path, timeout, region=None, confidence=0.9):
        """在屏幕上查找指定图片的位置"""
        start_ms = time.time() * 1000
        stop_ms = start_ms + (timeout * 1000)
        image = self.image_loader.load_image(pic_path)

        while time.time() * 1000 < stop_ms:
            try:
                location = pag.locateOnScreen(image, region=region, confidence=confidence)
                if location:
                    return location
            except Exception as e:
                raise Exception(f'图片查找失败: {e}')

            time.sleep(0.1)

        raise Exception('图片查找失败,请检查%s' % pic_path)

    @staticmethod
    def get_center(location):
        """计算并返回给定位置的中心点坐标"""
        if location:
            return pag.center(location)
        raise ValueError("无法计算中心点，未提供有效的矩形区域")

    @staticmethod
    def move_to_coordinates(x, y):
        """移动鼠标到指定坐标"""
        for i in range(5):
            mouse_x, mouse_y = pag.position()
            if mouse_x == x and mouse_y == y:
                return mouse_x, mouse_y
            else:
                pag.moveTo(x, y)
        raise Exception('鼠标未移动到坐标%s, %s' % (x, y))