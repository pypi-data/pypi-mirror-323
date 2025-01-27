from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from nmu.utils.Verifycode import Verifycode
import json
import httpx
import html
import random
from nmu.utils.Hasher import Hasher
from nmu.utils.HashTool import HashTool


class Operation(object):

    def __init__(self, driver):
        self.driver = driver
        self.token = None

    def __get_cookie(self):
        # 打开 URL
        self.driver.get('https://172.16.203.16/')

        # 找到用户名和密码输入框并输入用户名和密码
        username_input = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "username")))
        username_input.send_keys("user01")
        time.sleep(1)
        # 点击密码显示按钮
        password_ck = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="password"]')))
        password_ck.click()
        time.sleep(1)
        # 输入密码
        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="password"]')))
        password_input.send_keys("55RZy.$xP#4Z")
        time.sleep(1)
        # 验证码
        verifyCode_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="verifyCodeTextNum"]')))
        verifyCode_input.click()
        imgCode = self.driver.find_element(By.XPATH,
                                           '//*[@id="layout"]/div[2]/div[2]/form/nz-form-item[3]/nz-form-control/div/div/nz-input-group/img')
        imgCode.screenshot('code.png')
        with open('code.png', 'rb') as fp:
            image = fp.read()
        self.verifycode = Verifycode.get_code(image)

        verifyCode_input.send_keys(self.verifycode)

        time.sleep(1)

        # 点击登录按钮
        login_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="layout"]/div[2]/div[2]/form/nz-form-item[4]/nz-form-control/div[1]/div/button')))
        login_btn.click()

        # 等待页面加载完成（可选，根据需求调整等待策略）
        time.sleep(5)

        # 获取 Cookies
        selenium_cookie = self.driver.get_cookies()

        # 获取token
        local_storage = self.driver.execute_script("return localStorage.getItem('ls.user');")
        local_data = json.loads(local_storage)
        self.token = local_data.get("token")
        print(self.token)

        # 转换为字典格式
        cookies_dict = {cookie['name']: cookie['value'] for cookie in selenium_cookie}
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
                "accept-language": "zh_CN",
                "Connection": "keep-alive",
                "Content-Type": "application/json;charset=UTF-8",
                "referer": "https://172.16.203.16/static/dist/pisces/",
                "Sec-Fetch-Dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
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

    def get_log_counts(self):
        cookies = self.__get_cookie()
        url = "https://172.16.203.16/api/audit/log/count"
        nonce = str(round(random.uniform(0, 1), 16))
        timestamp = str(time.time() * 1000)
        params = {
            "token": self.token,
            "accountId": "14",
            "nonce": nonce,
            "timestamp": timestamp,
            "hashStr1": Hasher().start().appendStr("/audit/log/count").end(),
            "hashStr2": Hasher().start().appendStr("").end(),
            "hashStr3": Hasher().start().appendStr("").end()
        }
        # 按字典值排序
        sorted_items = sorted(params.items(), key=lambda item: str(item[1]))

        # 拼接排序后的值
        signature = "".join([str(value) for _, value in sorted_items])

        payload = {
            "signature": HashTool().hash(signature),
            "nonce": nonce,
            "timestamp": timestamp,
            "accountId": "14"
        }

        response = self.__send_request(url=url, method="GET", cookies=cookies, data=payload)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def get_sys_usage(self):
        cookies = self.__get_cookie()
        url = "https://172.16.203.16/api/v1/monitor/resource/count"
        nonce = str(round(random.uniform(0, 1), 16))
        timestamp = str(time.time() * 1000)
        params = {
            "token": self.token,
            "accountId": "14",
            "nonce": nonce,
            "timestamp": timestamp,
            "hashStr1": Hasher().start().appendStr("/v1/monitor/resource/count").end(),
            "hashStr2": Hasher().start().appendStr("").end(),
            "hashStr3": Hasher().start().appendStr("").end()
        }
        # 按字典值排序
        sorted_items = sorted(params.items(), key=lambda item: str(item[1]))

        # 拼接排序后的值
        signature = "".join([str(value) for _, value in sorted_items])

        payload = {
            "signature": HashTool().hash(signature),
            "nonce": nonce,
            "timestamp": timestamp,
            "accountId": "14"
        }

        response = self.__send_request(url=url, method="GET", cookies=cookies, data=payload)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response
