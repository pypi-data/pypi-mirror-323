from time import sleep

import pyautogui as pag
from SelAct.selOpe.client.client_common import ScreenInteraction


class SelCliOpe(ScreenInteraction):
    """
    用于实现各种基于图像识别的屏幕交互操作。
    它继承自 ScreenInteraction 类，提供了额外的鼠标点击和拖拽功能。
    """

    def left_click_coordinates(self, x, y):
        """
        移动鼠标到指定坐标并执行左键单击。

        :param x: 目标位置的X坐标
        :param y: 目标位置的Y坐标
        """
        self.move_to_coordinates(x, y)
        sleep(0.5)  # 等待一段时间以确保鼠标移动到位
        pag.click(x, y)

    def right_click_coordinates(self, x, y):
        """
        移动鼠标到指定坐标并执行右键单击。

        :param x: 目标位置的X坐标
        :param y: 目标位置的Y坐标
        """
        self.move_to_coordinates(x, y)
        pag.rightClick(x, y)

    def left_click_pic(self, pic_path, timeout, region=None):
        """
        查找图片并在其中心位置执行左键单击。

        :param pic_path: 图片路径（支持本地或网络）
        :param timeout: 查找图片的最大等待时间（秒）
        :param region: 屏幕上的搜索区域（可选）
        """
        location = self.find_pic(pic_path, timeout, region)
        x, y = self.get_center(location)
        self.left_click_coordinates(x, y)

    def right_click_pic(self, pic_path, timeout, region=None):
        """
        查找图片并在其中心位置执行右键单击。

        :param pic_path: 图片路径（支持本地或网络）
        :param timeout: 查找图片的最大等待时间（秒）
        :param region: 屏幕上的搜索区域（可选）
        """
        location = self.find_pic(pic_path, timeout, region)
        x, y = self.get_center(location)
        self.right_click_coordinates(x, y)

    def drag_to(self, start_x, start_y, end_x, end_y):
        """
        执行从起始点到结束点的拖拽操作。

        :param start_x: 起始位置的X坐标
        :param start_y: 起始位置的Y坐标
        :param end_x: 结束位置的X坐标
        :param end_y: 结束位置的Y坐标
        """
        self.move_to_coordinates(start_x, start_y)
        pag.dragTo(end_x, end_y, duration=2)  # 拖拽持续时间为2秒

    def move_to_pic(self, pic_path, timeout, region=None):
        """
        查找图片并将鼠标移动到图片中心。

        :param pic_path: 图片路径（支持本地或网络）
        :param timeout: 查找图片的最大等待时间（秒）
        :param region: 屏幕上的搜索区域（可选）
        """
        location = self.find_pic(pic_path, timeout, region)
        x, y = self.get_center(location)
        self.move_to_coordinates(x, y)


if __name__ == "__main__":
    # 示例：如何使用SelCliOpe类的方法
    sel_cli_ope = SelCliOpe()
    # 注意：以下示例调用需要实际的参数值才能正常工作
    # sel_cli_ope.left_click_pic("path/to/image.png", 10)