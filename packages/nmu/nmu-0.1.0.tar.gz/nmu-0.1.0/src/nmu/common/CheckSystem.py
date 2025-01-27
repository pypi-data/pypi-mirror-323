import os
import platform


class CheckSystem:
    @classmethod
    def get_dirver_path(cls):
        # 获取当前脚本的目录路径
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # 获取操作系统类型
        system_platform = platform.system().lower()

        # 根据不同的操作系统选择 chromedriver 路径
        if system_platform == 'windows':
            chromedriver_path = os.path.join(current_directory, '..', 'chromedriver', 'chromedriver_win32',
                                             'chromedriver.exe')
        elif system_platform == 'linux':
            chromedriver_path = os.path.join(current_directory, '..', 'chromedriver', 'chromedriver_linux64',
                                             'chromedriver')
        elif system_platform == 'darwin':  # macOS
            chromedriver_path = os.path.join(current_directory, '..', 'chromedriver', 'chromedriver_mac_arm64',
                                             'chromedriver')
        else:
            raise ValueError(f"Unsupported platform: {system_platform}")

        # 获取绝对路径
        chromedriver_path = os.path.abspath(chromedriver_path)

        # 检查 chromedriver 是否存在
        if not os.path.exists(chromedriver_path):
            raise ValueError(f"The chromedriver path is invalid: {chromedriver_path}")

        return chromedriver_path

    @classmethod
    def get_chrome_path(cls):
        # 获取当前脚本的目录路径
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # 获取操作系统类型
        system_platform = platform.system().lower()

        # 根据不同的操作系统选择 chromedriver 路径
        if system_platform == 'windows':
            chrome_path = os.path.join(current_directory, '..', 'chrome', 'chrome-win32',
                                             'chrome.exe')
        elif system_platform == 'linux':
            chrome_path = os.path.join(current_directory, '..', 'chrome', 'chrome-linux64',
                                             'chrome')
        elif system_platform == 'darwin':  # macOS
            chrome_path = os.path.join(current_directory, '..', 'chrome', 'chrome-mac-arm64','Google Chrome for Testing.app', 'Contents', 'MacOS', 'Google Chrome for Testing')
        else:
            raise ValueError(f"Unsupported platform: {system_platform}")

        # 获取绝对路径
        chrome_path = os.path.abspath(chrome_path)

        # 检查 chromedriver 是否存在
        if not os.path.exists(chrome_path):
            raise ValueError(f"The chromedriver path is invalid: {chrome_path}")

        return chrome_path