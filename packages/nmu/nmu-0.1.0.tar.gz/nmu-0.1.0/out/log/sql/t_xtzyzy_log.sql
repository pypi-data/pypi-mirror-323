CREATE TABLE usr_netsec.t_xtzyzy_log
(
    type varchar(20),
    occupancy bigint,
    occupation varchar(255),
    occupancy_total bigint,
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (type, ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_xtzyzy_log.type IS '资源类型';
COMMENT ON COLUMN usr_netsec.t_xtzyzy_log.occupancy IS '资源占用率';
COMMENT ON COLUMN usr_netsec.t_xtzyzy_log.occupation IS '资源占用情况';
COMMENT ON COLUMN usr_netsec.t_xtzyzy_log.occupancy_total IS '资源总占用率';
COMMENT ON COLUMN usr_netsec.t_xtzyzy_log.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_xtzyzy_log IS '系统资源占用';

ALTER TABLE usr_netsec.t_xtzyzy_log
    OWNER TO usr_netsec;