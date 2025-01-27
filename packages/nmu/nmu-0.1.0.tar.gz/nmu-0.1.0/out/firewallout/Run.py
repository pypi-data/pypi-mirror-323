from nmu.firewallout.Operation import Operation
from nmu.utils.PostgreSQLTool import PostgreSQLTool
from nmu.common.Browser import Browser
import json
import os
import logging

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# 数据库配置
db_config = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "datav"),
    "user": os.getenv("DB_USER", "usr_netsec"),
    "password": os.getenv("DB_PASSWORD", "o3h&sCas5vsK!gh@")
}

browser = Browser(isHeadless=True)
driver = browser.get_driver()
operation = Operation(driver)
postgresql_tool = PostgreSQLTool(db_config)


def insert_data(data_list, query, fields):
    for record in data_list:
        try:
            values = tuple(record[field] for field in fields)
            postgresql_tool.execute_query(query, values)
            logger.info(f"插入成功: {record}")
        except Exception as e:
            logger.error(f"插入失败: {record} - 错误: {e}")


def post_device_info():
    insert_query = """
        INSERT INTO usr_netsec.t_sbxx_out (state_version, state_time, system_run_time, state_fanstate, state_envir, state_hrpstate, state_onlineusr, state_productversion, state_hostname, device_sn, state_vfw, state_ipv6, state_nat64, state_pwrstate, state_agilenetstate, lastloaded_success, state_lastloaded, cpuuseddata, memoryusedper, flashper)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    result = operation.post_device_info()
    if isinstance(result, str):
        result = json.loads(result)
    state_dict = result.get("getDevSysInfo", {})
    hardware_dict = result.get("getDevResInfo", {}).get("resourceInf", {})
    data_dict = {**state_dict, **hardware_dict}
    # 将数组转为字符串
    pwrState_list = data_dict["state_pwrState"]
    state_mapping = {
        1: "正常",
        0: "异常"
    }
    pwrState_str = ";".join([f"{item['slot']}:{state_mapping.get(item['state'], '未知')}" for item in pwrState_list])
    data_dict["state_pwrState"] = pwrState_str

    cpu_str = data_dict["cpuUsedData"]
    data_dict["cpuuseddata"] = f"{cpu_str}%"

    men_str = data_dict["memoryUsedPer"]
    data_dict["memoryusedper"] = f"{men_str}%"

    flashTotal = data_dict["flashTotal"]
    flashFree = data_dict["flashFree"]
    used = round((flashTotal - flashFree) / flashTotal * 100, 0)
    data_dict["flashper"] = f"{used}%"


    print(data_dict)
    insert_data([data_dict], insert_query, ["state_version", "state_time", "system_run_time", "state_fanState", "state_envir", "state_hrpState", "state_onlineUsr", "state_productVersion", "state_hostName", "device_sn", "state_vfw", "state_ipv6", "state_nat64", "state_pwrState", "state_agilenetState", "lastLoaded_success", "state_lastLoaded", "cpuuseddata", "memoryusedper", "flashper"])


if __name__ == '__main__':
    try:
        post_device_info()
    finally:
        browser.close_browser()