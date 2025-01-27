import psycopg2
from psycopg2 import OperationalError, DatabaseError
from dbutils.pooled_db import PooledDB
from typing import List, Tuple, Any, Optional
from contextlib import closing
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PostgreSQLTool:
    def __init__(self, master_db_config, slave_db_configs=  None, max_conn=5):
        self.master_db_config = master_db_config
        self.slave_db_configs = slave_db_configs if slave_db_configs else [master_db_config]

        # 初始化连接池
        self.master_pool = self.create_pool(master_db_config, max_conn)
        self.slave_pools = [self.create_pool(db_config, max_conn) for db_config in self.slave_db_configs]

    def create_pool(self, db_config, max_conn):
        try:
            pool = PooledDB(
                creator=psycopg2,  # 使用 psycopg2 作为数据库驱动
                maxconnections=max_conn,
                blocking=True,  # 设置阻塞模式
                **db_config  # 其他数据库连接参数
            )
            logging.info(f"Pool created successfully for {db_config['host']}")
            return pool
        except OperationalError as e:
            logging.error(f"Error while creating pool for PostgreSQL at {db_config['host']}: {e}")
            return None

    def get_connection(self, is_master=True):
        pool = self.master_pool if is_master else self.choose_read_pool()
        if pool:
            try:
                connection = pool.connection()
                if connection:
                    logging.info(f"Successfully retrieved connection from pool")
                    return connection
            except OperationalError as e:
                logging.error(f"Error getting connection from pool: {e}")
                return None
        return None

    def put_connection(self, conn, is_master=True):
        if conn:
            conn.close()

    def choose_read_pool(self):
        for pool in self.slave_pools:
            if pool:
                return pool
        logging.warning("No available slave pools, defaulting to master pool")
        return self.master_pool

    def execute_query(self, query: str, params: Tuple[Any, ...] = (), is_read_query: bool = False):
        connection = self.get_connection(is_master=not is_read_query)
        if connection:
            with closing(connection.cursor()) as cursor:
                try:
                    cursor.execute(query, params)
                    if not is_read_query:
                        connection.commit()
                        return cursor.rowcount  # 对于非读操作，返回影响的行数
                    else:
                        result = cursor.fetchall()  # 对于读操作，返回查询结果
                        return result
                except DatabaseError as e:
                    if not is_read_query:
                        connection.rollback()
                    logging.error(f"Error while executing query: {e}")
                    return None
                finally:
                    self.put_connection(connection, is_master=not is_read_query)

    def execute_read_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[Tuple[Any, ...]]:
        return self.execute_query(query, params, is_read_query=True)

    # 关闭连接池的方法不再需要，因为 DBUtils 管理其连接的关闭
