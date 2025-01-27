from nmu.log.Operation import Operation
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

def get_log_count():
    insert_query = """
        INSERT INTO usr_netsec.t_rzsltj_log (total, today)
        VALUES (%s, %s)
    """
    result = operation.get_log_counts()
    print(result)
    if isinstance(result, str):
        result = json.loads(result)

    insert_data([result], insert_query, ["countAll", "currentCount"])

def get_sys_usage():
    insert_query = """
        INSERT INTO usr_netsec.t_xtzyzy_log (type, occupancy, occupation, occupancy_total)
        VALUES (%s, %s, %s, %s)
    """
    result = operation.get_sys_usage()
    if isinstance(result, str):
        result = json.loads(result)
    result.get("table").append({"name": "CPU", "total": None, "unit": None, "use": None})
    for e in result.get("table"):
        if e.get("name") == "CPU":
            e["occupancy"] = result.get("chart")[2]
        elif e.get("name") == "内存":
            e["occupancy"] = result.get("chart")[1]
        elif e.get("name") == "磁盘":
            e["occupancy"] = result.get("chart")[0]
        else:
            e["occupancy"] = None
        e["occupancy_total"] = result.get("total")
        if e.get("name") != "CPU":
            e["occupation"] = f"{e['use']}/{e['total']}{e['unit']}"
        else:
            e["occupation"] = None

    print(result)
    insert_data(result.get("table"), insert_query, ["name", "occupancy", "occupation", "occupancy_total"])




if __name__ == '__main__':
    try:
        get_log_count()
        get_sys_usage()
    finally:
        browser.close_browser()