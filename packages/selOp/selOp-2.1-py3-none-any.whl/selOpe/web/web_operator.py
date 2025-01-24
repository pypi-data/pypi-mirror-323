import time

from selenium.common import WebDriverException, TimeoutException, ElementNotVisibleException, \
    StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from SelAct.selOpe.web.driver_config import driver_config


class SelEleOpe:
    def __init__(self, browser_path, driver_path, incognito=False, headless=False):
        self.driver = driver_config(browser_path, driver_path, incognito, headless)

    def element_get(self, locator_expr, timeout=30, must_be_visible=False):
        """
        获取元素
        :param locator_expr: 元素定位表达式
        :param timeout: 超时，默认30s
        :param must_be_visible: 是否必须可见
        :return:
        """
        # 开始时间
        start_ms = time.time() * 1000
        # 设置的结束时间
        stop_ms = start_ms + (timeout * 1000)
        for i in range(int(timeout * 10)):
            # 查找元素
            try:
                element = self.driver.find_element(By.XPATH, value=locator_expr)
                # 如果元素不是必须可见的,就直接返回元素
                if not must_be_visible:
                    return element
                # 如果元素必须是可见的,则需要先判断元素是否可见
                else:
                    if element.is_displayed():
                        return element
                    else:
                        raise Exception()
            except Exception:
                now_ms = time.time() * 1000
                if now_ms >= stop_ms:
                    break
            time.sleep(0.1)
        raise ElementNotVisibleException('元素定位失败,定位表达式:%s' % locator_expr)

    def open_page(self, url, expected_title=None, locator_expr=None, timeout=10):
        """
        打开指定的网页，并进行验证。

        :param url: 要打开的网页地址。
        :param expected_title: 预期的页面标题（可选）。
        :param locator_expr: 定位表达式（可选）
        :param timeout: 等待预期条件满足的最大时间（秒，默认10秒）。
        """
        try:
            self.driver.get(url)

            # 检查URL是否正确加载
            if not self.driver.current_url.startswith(url):
                raise ValueError(f"Failed to load page {url}. Loaded URL is {self.driver.current_url}")

            # 如果提供了预期的页面标题，则等待直到标题匹配
            if expected_title:
                WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.title and expected_title in driver.title
                )

            # 如果提供了预期的元素，则等待该元素出现
            if locator_expr:
                self.element_get(locator_expr, timeout=timeout, must_be_visible=True)

        except (WebDriverException, TimeoutException) as e:
            raise Exception("url超时,%s" % e)

    def element_disappear(self, locator_expr, timeout=30):
        """
        等待页面元素消失
        :param locator_expr: 定位表达式
        :param timeout: 超时时间
        :return:
        """
        if locator_expr:
            # 开始时间
            start_ms = time.time() * 1000
            # 设置结束时间
            stop_ms = start_ms + (timeout * 1000)
            for i in range(int(timeout * 1000)):
                try:
                    element = self.driver.find_element(By.XPATH, value=locator_expr)
                    if element.is_displayed():
                        now_ms = time.time() * 1000
                        if now_ms >= stop_ms:
                            break
                        time.sleep(0.1)
                except Exception:
                    continue
            raise Exception('元素没有消失,定位表达式:%s' % locator_expr)

    def element_appear(self, locator_expr, timeout=30):
        """
        等待元素出现
        :param locator_expr:
        :param timeout:
        :return:
        """
        if locator_expr:
            # 开始时间
            start_ms = time.time() * 1000
            # 设置结束时间
            stop_ms = start_ms + (timeout * 1000)
            for i in range(int(timeout * 10)):
                try:
                    element = self.driver.find_element(By.XPATH, locator_expr)
                    if element.is_displayed():
                        return element
                except Exception:
                    now_ms = time.time() * 1000
                    if now_ms >= stop_ms:
                        break
                    time.sleep(0.1)
                    pass
            raise ElementNotVisibleException('元素没有出现,定位表达式:%s' % locator_expr)

    def wait_for_ready_state_complete(self, timeout=30):
        """
        等待页面完全加载完成
        :param timeout: 超时
        :return:
        """
        # 设置开始时间
        start_ms = time.time() * 1000
        # 设置结束时间
        stop_ms = start_ms + (timeout * 1000)
        for i in range(int(timeout * 1000)):
            try:
                # 获取页面状态
                ready_state = self.driver.execute_script("return document.readyState")
            except WebDriverException:
                # 如果有driver的错误,执行js会失败,就直接跳过
                time.sleep(0.03)
                return True
            # 如果页面元素全部加载完成,返回True
            if ready_state == 'complete':
                time.sleep(0.01)
                return True
            else:
                now_ms = time.time() * 1000
                # 如果超时就break
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        raise Exception('打开网页时,页面元素在%s秒后仍未完全加载' % timeout)

    def element_fill_value(self, locator_expr, fill_value, timeout=30):
        """
        元素填值
        :param locator_expr: 定位表达式
        :param fill_value:填入的值
        :param timeout: 超时时间
        :return:
        """
        # 元素出现
        element = self.element_appear(locator_expr, timeout)
        try:
            # 先清除元素中的原有值
            element.clear()
        except StaleElementReferenceException:
            # 页面元素没有刷新出来
            self.wait_for_ready_state_complete(timeout)
            time.sleep(0.06)
            element = self.element_appear(locator_expr, timeout)
            try:
                element.clear()
            except Exception as e:
                raise Exception('元素清空内容失败' % e)
        except Exception as e:
            raise Exception('元素清空内容失败' % e)
        # 填入的值转换成字符串
        if type(fill_value) is int or type(fill_value) is float:
            fill_value = str(fill_value)
        try:
            # 填入的值不是以\n结尾
            if not fill_value.endswith('\n'):
                element.send_keys(fill_value)
                self.wait_for_ready_state_complete(timeout)
            else:
                fill_value = fill_value[:-1]
                element.send_keys(fill_value)
                element.send_keys(Keys.RETURN)
                self.wait_for_ready_state_complete(timeout)
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete(timeout)
            time.sleep(0.05)
            element = self.element_appear(locator_expr, timeout)
            element.clear()
            if not fill_value.endswith('\n'):
                element.send_keys(fill_value)
                self.wait_for_ready_state_complete(timeout)
            else:
                fill_value = fill_value[:-1]
                element.send_keys(fill_value)
                element.send_keys(Keys.RETURN)
                self.wait_for_ready_state_complete(timeout)
        except Exception:
            raise Exception('元素填值失败')

    def element_click(self, locator_expr, locator_expr_appear, locator_expr_disappear, timeout=30):
        """
        元素点击
        :param locator_expr:定位表达式
        :param locator_expr_appear:等待元素出现的定位表达式
        :param locator_expr_disappear:等待元素消失的定位表达式
        :param timeout: 超时时间
        :return:
        """
        # 元素要可见
        element = self.element_appear(locator_expr, timeout)
        try:
            # 点击元素
            element.click()
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete(timeout)
            time.sleep(0.06)
            element = self.element_appear(locator_expr, timeout)
            element.click()
        except Exception as e:
            raise Exception('页面出现异常:%s,元素不可点击' % e)
        try:
            # 点击元素后的元素出现或消失
            self.element_appear(locator_expr_appear, timeout)
            self.element_disappear(locator_expr_disappear, timeout)
        except Exception:
            pass

    def switch_last_handle(self):
        """
        句柄切换到最新的窗口
        :return:
        """
        window_handles = self.driver.window_handles
        self.driver.switch_to.window(window_handles[-1])

    def switch_into_iframe(self, locator_iframe_expr, timeout):
        """
        进入iframe
        :param locator_iframe_expr: 定位iframe的表达式
        :param timeout: 超时
        :return:
        """
        iframe = self.element_get(locator_iframe_expr, timeout)
        self.driver.switch_to.frame(iframe)

    def switch_from_iframe_to_content(self):
        """
        跳出iframe
        :return:
        """
        self.driver.switch_to.parent_frame()

    def scroll_left_right(self, class_name, deviation):
        """
        操作滚动条向左/右移动
        :param class_name: 滚动条的class name
        :param deviation:偏移。0代表最左
        :return:
        """
        down_scroll_js = 'document.getElementsByClassName("%s")[0].scrollLeft=%s' % (class_name, deviation)
        return self.driver.execute_script(down_scroll_js)

    def get_attribute(self, locator_expr, attribute, timeout):
        """
        获取属性值
        :param locator_expr: 定位表达式
        :param attribute: 属性
        :param timeout: 超时
        :return:
        """
        try:
            ele = self.element_get(locator_expr, timeout, must_be_visible=True)
            return ele.get_attribute(attribute)
        except Exception as e:
            raise Exception("获取元素属性失败,%s" % e)

    def element_right_click(self, locator_expr, timeout):
        """
        元素右键点击
        :param locator_expr:定位表达式
        :param timeout: 超时
        :return:
        """
        # 元素要可见
        element = self.element_appear(locator_expr, timeout)
        try:
            # 右击元素
            ActionChains(self.driver).context_click(element).perform()
            return True
        except StaleElementReferenceException:
            self.wait_for_ready_state_complete(timeout)
            time.sleep(0.06)
            element = self.element_appear(locator_expr, timeout)
            ActionChains(self.driver).context_click(element).perform()
        except Exception as e:
            raise Exception('页面出现异常:%s,元素不可右击' % e)

    def quit(self):
        # 关闭浏览器
        self.driver.quit()
