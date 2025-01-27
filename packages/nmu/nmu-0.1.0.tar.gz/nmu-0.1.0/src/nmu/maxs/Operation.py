from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from nmu.utils.Verifycode import Verifycode
import time
import httpx
import json
import html
from datetime import datetime, timedelta

class Operation(object):
    def __init__(self, driver):
        self.driver = driver

    def __get_cookie(self):
        # 打开 URL
        self.driver.get('https://10.128.6.24:8686/maxPage/login')

        # 找到用户名和密码输入框并输入用户名和密码
        username_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/div[2]/form/div[2]/div/div/div/input")))
        username_input.send_keys("user01")
        time.sleep(1)
        # 点击密码显示按钮
        password_ck = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/form/div[2]/div/div/div/input')))
        password_ck.click()
        time.sleep(1)
        # 输入密码
        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/form/div[3]/div/div/div/input')))
        password_input.send_keys("55RZy.$xP#4Z1")
        time.sleep(1)
        # 验证码
        verifyCode_input = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/form/div[4]/div/div[1]/div/input')))
        verifyCode_input.click()
        image_code = self.driver.find_element(By.XPATH,
                                                  '/html/body/div[1]/div[2]/div/div[2]/form/div[4]/div/div[2]/img')
        image_code.screenshot('code.png')
        with open('code.png', 'rb') as fp:
            image = fp.read()
        verifyCode = Verifycode.get_code(image)
        verifyCode_input.send_keys(verifyCode)

        # 点击登录按钮
        login_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div/div[2]/form/div[5]/div/button')))
        login_btn.click()

        # 等待页面加载完成（可选，根据需求调整等待策略）
        time.sleep(6)

        # 获取 Cookies
        print("获取cookie成功，准备退出浏览器。。。")

        # 转换为字典格式
        cookies_dict = {}
        for cookie in self.driver.get_cookies():
            cookies_dict[cookie['name']] = cookie['value']

        return cookies_dict

    def __send_request(self, url, method="GET", headers=None, cookies=None, data=None):
        """
        通用请求方法，支持 GET 和 POST 请求。

        :param url: str, 请求的 URL。
        :param method: str, 请求方法，默认为 POST。
        :param headers: dict, 请求头。
        :param cookies: dict, Cookies 信息。
        :param data: dict, 请求的数据。
        :return: dict, 包含解析后的响应数据。
        """

        if headers is None:
            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9",
                "priority": "u=1, i",
                "referer": "https://10.128.6.24:8686/maxPage/home?title=%E9%A6%96%E9%A1%B5&_permissionId=100000&way=isMenu",
                "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
            }

        if data is None:
            # 获取今天的日期并设置为今天的 0:00
            today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

            # 获取明天的日期并设置为明天的 0:00
            tomorrow = today + timedelta(days=1)
            data = {
                "startTime": today.strftime("%Y-%m-%d 00:00"),
                "endTime": tomorrow.strftime("%Y-%m-%d 00:00")
            }

        # 创建 HTTPX 客户端
        try:
            with httpx.Client(verify=False, cookies=cookies, headers=headers) as client:
                if method.upper() == "GET":
                    response = client.get(url, params=data)
                elif method.upper() == "POST":
                    response = client.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # 解析响应
                decoded_text = html.unescape(response.text)
                try:
                    json_data = json.loads(decoded_text)
                    return {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "json": json_data,
                    }
                except json.JSONDecodeError:
                    return {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "text": response.text,
                    }
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return {
                "error": str(e)
            }

    def get_grade(self):

        # 获取 Cookies
        cookies = self.__get_cookie()

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/portal/grade/get"
        response = self.__send_request(url=url, method="GET", cookies=cookies)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def get_safe_event(self):
        # 获取 Cookies
        cookies = self.__get_cookie()

        # 获取今天的日期并设置为今天的 0:00
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取明天的日期并设置为明天的 0:00
        tomorrow = today + timedelta(days=1)
        data = {
            "startTime": today.strftime("%Y-%m-%d 00:00"),
            "endTime": tomorrow.strftime("%Y-%m-%d 00:00"),
            "type": 1
        }

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/portal/overview/get"
        response = self.__send_request(url=url, method="GET", cookies=cookies, data=data)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def get_safe_warnnings(self):

        # 获取 Cookies
        cookies = self.__get_cookie()

        # 获取今天的日期并设置为今天的 0:00
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取明天的日期并设置为明天的 0:00
        tomorrow = today + timedelta(days=1)
        data = {
            "startTime": today.strftime("%Y-%m-%d 00:00"),
            "endTime": tomorrow.strftime("%Y-%m-%d 00:00"),
            "type": 2
        }

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/portal/overview/get"
        response = self.__send_request(url=url, method="GET", cookies=cookies, data=data)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def post_fall_count(self):
        # 获取 Cookies
        cookies = self.__get_cookie()

        # 获取今天的日期并设置为今天的 0:00
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取明天的日期并设置为明天的 0:00
        tomorrow = today + timedelta(days=1)
        data = {
            "startTime": today.strftime("%Y-%m-%d 00:00"),
            "endTime": tomorrow.strftime("%Y-%m-%d 00:00"),
            "alarmScope": -1,
            "assetKey": ""
        }

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/assetView/getFallTotalCount"
        response = self.__send_request(url=url, method="POST", cookies=cookies, data=data)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def post_danger_count(self):
        # 获取 Cookies
        cookies = self.__get_cookie()

        # 获取今天的日期并设置为今天的 0:00
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取明天的日期并设置为明天的 0:00
        tomorrow = today + timedelta(days=1)
        data = {
            "startTime": today.strftime("%Y-%m-%d 00:00"),
            "endTime": tomorrow.strftime("%Y-%m-%d 00:00"),
            "alarmScope": 1,
            "assetKey": ""
        }

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/assetView/getFallTotalCount"
        response = self.__send_request(url=url, method="POST", cookies=cookies, data=data)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def get_top5_attacks(self):
        # 获取 Cookies
        cookies = self.__get_cookie()

        # 获取今天的日期并设置为今天的 0:00
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取明天的日期并设置为明天的 0:00
        tomorrow = today + timedelta(days=1)
        data = {
            "startTime": today.strftime("%Y-%m-%d 00:00"),
            "endTime": tomorrow.strftime("%Y-%m-%d 00:00"),
            "important": "false"
        }

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/portal/asset/attacker/top5"
        response = self.__send_request(url=url, method="GET", cookies=cookies, data=data)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def get_top5_casualty(self):
        # 获取 Cookies
        cookies = self.__get_cookie()

        # 获取今天的日期并设置为今天的 0:00
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取明天的日期并设置为明天的 0:00
        tomorrow = today + timedelta(days=1)
        data = {
            "startTime": today.strftime("%Y-%m-%d 00:00"),
            "endTime": tomorrow.strftime("%Y-%m-%d 00:00"),
            "important": "false"
        }

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/portal/asset/casualty/top5"
        response = self.__send_request(url=url, method="GET", cookies=cookies, data=data)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def post_safe_alarm(self):
        # 获取 Cookies
        cookies = self.__get_cookie()

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/portal/threat/getSecurityAlarmStatistics"
        response = self.__send_request(url=url, method="POST", cookies=cookies)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def post_safe_event_list(self):
        # 获取 Cookies
        cookies = self.__get_cookie()

        # 调用工具方法
        url = "https://10.128.6.24:8686/maxs/rv/portal/threat/getAllSecurityEventList"
        response = self.__send_request(url=url, method="POST", cookies=cookies)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response