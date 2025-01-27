CREATE TABLE usr_netsec.t_aqqs_sjzx
(
    index int,
    time varchar(20),
    low bigint,
    medium bigint,
    high bigint,
    information bigint,
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (index, ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_aqqs_sjzx.index IS '序号，主键';
COMMENT ON COLUMN usr_netsec.t_aqqs_sjzx.time IS '统计时间';
COMMENT ON COLUMN usr_netsec.t_aqqs_sjzx.low IS '严重等级（低）';
COMMENT ON COLUMN usr_netsec.t_aqqs_sjzx.medium IS '严重等级（中）';
COMMENT ON COLUMN usr_netsec.t_aqqs_sjzx.high IS '严重等级（高）';
COMMENT ON COLUMN usr_netsec.t_aqqs_sjzx.information IS '严重等级（提示）';
COMMENT ON COLUMN usr_netsec.t_aqqs_sjzx.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_aqqs_sjzx IS '安全趋势';

ALTER TABLE usr_netsec.t_aqqs_sjzx
    OWNER TO usr_netsec;