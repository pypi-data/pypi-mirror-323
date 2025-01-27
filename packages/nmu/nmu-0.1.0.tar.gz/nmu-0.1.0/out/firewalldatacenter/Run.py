from nmu.firewalldatacenter.Operation import Operation
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


def get_ips_stat():
    insert_query = """
        INSERT INTO usr_netsec.t_zjygywxfhsj_sjzx (id, name, statistic, severity)
        VALUES (%s, %s, %s, %s)
    """
    result = operation.get_ips_stat()
    if isinstance(result, str):
        result = json.loads(result)

    data_list = result.get("getIPSStatData", {}).get("data", [])
    insert_data(data_list, insert_query, ["id", "name", "statistic", "severity"])


def get_interface_traffic():
    insert_query = """
        INSERT INTO usr_netsec.t_jklltjxx_sjzx (sj, ll)
        VALUES (%s, %s)
    """
    result = operation.get_interface_traffic()
    if isinstance(result, str):
        result = json.loads(result)

    x_data = result["getDBInterfaceHoursData"]["x"][0]["data"]
    y_data = result["getDBInterfaceHoursData"]["y"][0]["data"]
    combined_list = [{"时间": x, "流量": y} for x, y in zip(x_data, y_data)]
    insert_data(combined_list, insert_query, ["时间", "流量"])

def get_online_info():
    insert_query = """
        INSERT INTO usr_netsec.t_zxssjk_sjzx (xjljsl, bfljs, udpbfljs, tcpbfljs, zxips, zxyhs)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    result = operation.get_online_info()
    if isinstance(result, str):
        result = json.loads(result)

    data_dict = result.get("getOnlineInformation", {}).get("data", {})
    insert_data([data_dict], insert_query, ["newConnection", "superveneConnection", "UDP", "TCP", "IP", "users"])

def get_security_trend():
    insert_query = """
        INSERT INTO usr_netsec.t_aqqs_sjzx (index, time, low, medium, high, information)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    result = operation.get_security_trend()
    if isinstance(result, str):
        result = json.loads(result)

    data_list = result.get("getSecurityTrendData", {}).get("data", [])
    insert_data(data_list, insert_query, ["index", "time", "low", "medium", "high", "information"])

def get_traffic_report_app():
    insert_query = """
        INSERT INTO usr_netsec.t_yyssllpm_sjzx (index, application, vsysname, upflow, downflow, flow, sessionNum)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    result = operation.get_traffic_report_app()
    if isinstance(result, str):
        result = json.loads(result)
    data_list = result.get("getTrafficReportApp", {}).get("data", [])
    insert_data(data_list, insert_query, ["index", "application", "vsysname", "upflow", "downflow", "flow", "sessionNum"])

def get_ips_security_stat():
    insert_query = """
        INSERT INTO usr_netsec.t_zjygywxfhyzxtjxx_sjzx (name, severity, value, jump_flag)
        VALUES (%s, %s, %s, %s)
    """
    result = operation.get_ips_security_stat()
    if isinstance(result, str):
        result = json.loads(result)
    print(result)
    data_list = result.get("getIPSSecurityStat", [])
    print(data_list)
    insert_data(data_list, insert_query, ["name", "severity", "value", "jump_flag"])

def get_traffic_ranking():
    insert_query = """
        INSERT INTO usr_netsec.t_ydzssllpm_sjzx (index, sourceip, "user", vsysname, upflow, downflow, flow, sessionNum)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    result = operation.get_traffic_ranking()
    if isinstance(result, str):
        result = json.loads(result)
    data_list = result.get("getTrafficReportSrcip", {}).get("data", [])
    insert_data(data_list, insert_query, ["index", "sourceip", "user", "vsysname", "upflow", "downflow", "flow", "sessionNum"])

if __name__ == '__main__':
    try:
        get_ips_stat()
        get_interface_traffic()
        get_online_info()
        get_security_trend()
        get_traffic_report_app()
        get_ips_security_stat()
        get_traffic_ranking()
    finally:
        browser.close_browser()