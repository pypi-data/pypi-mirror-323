CREATE TABLE usr_netsec.t_zxssjk_sjzx
(
    xjljsl bigint,
    bfljs bigint,
    udpbfljs bigint,
    tcpbfljs bigint,
    zxips bigint,
    zxyhs bigint,
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_zxssjk_sjzx.xjljsl IS '新建连接速率';
COMMENT ON COLUMN usr_netsec.t_zxssjk_sjzx.bfljs IS '并发连接数';
COMMENT ON COLUMN usr_netsec.t_zxssjk_sjzx.udpbfljs IS 'UDP并发连接数';
COMMENT ON COLUMN usr_netsec.t_zxssjk_sjzx.tcpbfljs IS 'TCP并发连接数';
COMMENT ON COLUMN usr_netsec.t_zxssjk_sjzx.zxips IS '在线IP数';
COMMENT ON COLUMN usr_netsec.t_zxssjk_sjzx.zxyhs IS '在线用户数';
COMMENT ON COLUMN usr_netsec.t_zxssjk_sjzx.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_zxssjk_sjzx IS '在线实时监控';

ALTER TABLE usr_netsec.t_zxssjk_sjzx
    OWNER TO usr_netsec;