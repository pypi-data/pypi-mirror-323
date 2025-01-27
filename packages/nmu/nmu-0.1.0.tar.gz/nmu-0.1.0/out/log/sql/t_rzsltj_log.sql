CREATE TABLE usr_netsec.t_rzsltj_log
(
    total bigint,
    today bigint,
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_rzsltj_log.total IS '日志总数（单位：个）';
COMMENT ON COLUMN usr_netsec.t_rzsltj_log.today IS '今日日志总数（单位：个）';
COMMENT ON COLUMN usr_netsec.t_rzsltj_log.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_rzsltj_log IS '日志数量统计';

ALTER TABLE usr_netsec.t_rzsltj_log
    OWNER TO usr_netsec;