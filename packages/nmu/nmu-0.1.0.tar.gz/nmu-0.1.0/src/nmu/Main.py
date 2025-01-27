from nmu.log.Operation import Operation
from nmu.common.Browser import Browser

def main():
    browser = Browser(isHeadless=False)
    driver = browser.get_driver()
    operation = Operation(driver)
    print(operation.get_sys_usage())
    browser.close_browser()

if __name__ == '__main__':
    main()