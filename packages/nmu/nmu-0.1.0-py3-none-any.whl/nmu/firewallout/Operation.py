from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import httpx
import json
import html

class Operation(object):

    def __init__(self, driver):
        self.driver = driver

    def __get_cookie(self):

        # 打开 URL
        self.driver.get('https://10.11.255.252:8443/login.html?lang=zh_CN')

        # 找到用户名和密码输入框并输入用户名和密码
        username_input = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "username")))
        username_input.send_keys("adminuser")
        time.sleep(1)
        # 点击密码显示按钮
        password_ck = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="hide_pwd"]')))
        password_ck.click()
        time.sleep(1)
        # 输入密码
        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="platcontent"]')))
        password_input.send_keys("Bfmzdx@20250121")
        time.sleep(1)
        # 点击登录按钮
        login_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_login"]/tbody/tr/td')))
        login_btn.click()

        time.sleep(1)

        # 点击确认按钮
        # confirm_btn = WebDriverWait(self.driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, '//*[@id="fw_main_window_sweb-1_apply"]/tbody/tr/td')))
        # confirm_btn.click()

        # 等待页面加载完成（可选，根据需求调整等待策略）
        # driver.implicitly_wait(5)
        time.sleep(15)

        # 获取 Cookies
        selenium_cookie = self.driver.get_cookies()
        print("获取cookie成功，准备退出浏览器。。。")
        self.driver.quit()

        # 转换为字典格式
        cookies_dict = {cookie['name']: cookie['value'] for cookie in selenium_cookie}
        print(cookies_dict)

        return cookies_dict

    def __get_token(self, cookies, url="https://10.11.255.252:8443/common.html"):
        """
        模拟 curl 命令获取 Token，并返回解析的 swebToken。

        :param cookies: dict, 包含 Cookies 的字典，例如 {"SESSIONID": "abc123"}。
        :param url: str, 请求的目标 URL。
        :return: str, 返回解析出的 swebToken 或错误信息。
        """
        # 将 Cookies 转换为 "key=value; key2=value2" 的格式
        cookie_header = "; ".join([f"{key}={value}" for key, value in cookies.items()]) if cookies else None

        # 请求头
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": cookie_header,
            "Origin": "https://10.11.255.252:8443/",
            "Referer": "https://10.11.255.252:8443/default.html",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        }

        # 请求数据
        payload = {"getFWCommonData": {"language": 1, "vsys": "", "funcName": "getFWCommonData"}}

        try:
            # 使用 httpx.Client 发起 POST 请求
            with httpx.Client(verify=False) as client:  # verify=False 忽略 SSL 证书验证
                response = client.post(url, headers=headers, json=payload)

            # 打印响应状态码
            print("Status Code:", response.status_code)

            # HTML 解码并解析 JSON
            try:
                decoded_text = html.unescape(response.text)
                json_data = json.loads(decoded_text)
                print("Response JSON:", json.dumps(json_data, indent=4, ensure_ascii=False))

                # 提取 'swebToken'
                sweb_token = json_data["getFWCommonData"].get("swebToken", None)
                if sweb_token:
                    print("Extracted swebToken:", sweb_token)
                    return sweb_token
                else:
                    print("swebToken not found.")
                    return None
            except json.JSONDecodeError as e:
                print("Failed to parse JSON response:", e)
                return None

        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return None

    def __send_request(self, url, method="POST", headers=None, cookies=None, data=None, token=None):
        """
        通用请求方法，支持 GET 和 POST 请求。

        :param url: str, 请求的 URL。
        :param method: str, 请求方法，默认为 POST。
        :param headers: dict, 请求头。
        :param cookies: dict, Cookies 信息。
        :param data: dict, 请求的数据。
        :return: dict, 包含解析后的响应数据。
        """
        # 设置默认请求头
        if headers is None:
            headers = {
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://10.11.255.252:8443/",
                "Referer": "https://10.11.255.252:8443/default.html",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Token": token,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
                "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
            }

        # 创建 HTTPX 客户端
        try:
            with httpx.Client(verify=False, headers=headers, cookies=cookies) as client:
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

    # 设备信息
    def post_device_info(self):
        # 请求数据
        # payload = {"getDevSysInfo":{"language":1,"vsys":"public","funcName":"getDevSysInfo"},"getDevResInfo":{"language":1,"vsys":"public","funcName":"getDevResInfo"},"getLicenseInfo":{"language":1,"vsys":"public","funcName":"getLicenseInfo"}}
        payload = {"getDevSysInfo":{"language":1,"vsys":"public","funcName":"getDevSysInfo"},"getDevResInfo":{"language":1,"vsys":"public","funcName":"getDevResInfo"}}
        # 获取 Cookies
        cookies = self.__get_cookie()
        token = self.__get_token(cookies=cookies)
        print(token)

        # 调用工具方法
        url = "https://10.11.255.252:8443/common.html"
        response = self.__send_request(url=url, method="POST", headers=None, cookies=cookies, data=payload, token=token)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    # 接口流量统计
    def get_interface_traffic(self):
        # 请求数据
        payload = {"getDBInterfaceHoursData": {"language": 1, "vsys": "public", "funcName": "getDBInterfaceHoursData",
                                               "iName": ["all"], "flowType": "input"}}
        # 获取 Cookies
        cookies = self.__get_cookie()
        token = self.__get_token(cookies=cookies)
        print(token)

        # 调用工具方法
        url = "https://10.11.255.252:8443/common.html"
        response = self.__send_request(url=url, method="POST", headers=None, cookies=cookies, data=payload, token=token)

        # 打印结果
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def get_traffic_ranking(self):
        payload = {"getTrafficReportSrcip":{"language":1,"vsys":"public","funcName":"getTrafficReportSrcip","desc":"flow","switchFlag":1,"vsysName":""}}

        cookies = self.__get_cookie()
        token = self.__get_token(cookies=cookies)
        print(token)

        url = "https://10.11.255.252:8443/common.html"
        response = self.__send_request(url=url, method="POST", headers=None, cookies=cookies, data=payload, token=token)

        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def get_online_info(self):
        payload = {"getOnlineInformation":{"language":1,"vsys":"public","funcName":"getOnlineInformation","vsysName":"","switchFlag":1}}
        cookies = self.__get_cookie()
        token = self.__get_token(cookies=cookies)
        print(token)
        url = "https://10.11.255.252:8443/common.html"
        response = self.__send_request(url=url, method="POST", headers=None, cookies=cookies, data=payload, token=token)
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response

    def get_traffic_report_app(self):
        payload = {"getTrafficReportApp":{"language":1,"vsys":"public","funcName":"getTrafficReportApp","desc":"flow","switchFlag":1,"vsysName":""}}
        cookies = self.__get_cookie()
        token = self.__get_token(cookies=cookies)
        print(token)
        url = "https://10.11.255.252:8443/common.html"
        response = self.__send_request(url=url, method="POST", headers=None, cookies=cookies, data=payload, token=token)
        if "json" in response:
            return json.dumps(response["json"], indent=4, ensure_ascii=False)
        else:
            return response
