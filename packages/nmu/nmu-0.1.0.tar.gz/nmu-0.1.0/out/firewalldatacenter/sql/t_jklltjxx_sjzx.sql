CREATE TABLE usr_netsec.t_jklltjxx_sjzx
(
    sj timestamp NOT NULL,
    ll int,
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (sj, ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_jklltjxx_sjzx.sj IS '统计时间';
COMMENT ON COLUMN usr_netsec.t_jklltjxx_sjzx.ll IS '流量(Mbps)';
COMMENT ON COLUMN usr_netsec.t_jklltjxx_sjzx.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_jklltjxx_sjzx IS '接口流量统计信息';

ALTER TABLE usr_netsec.t_jklltjxx_sjzx
    OWNER TO usr_netsec;