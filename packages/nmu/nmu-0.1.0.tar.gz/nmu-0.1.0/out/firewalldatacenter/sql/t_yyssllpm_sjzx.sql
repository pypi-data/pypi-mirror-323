CREATE TABLE usr_netsec.t_yyssllpm_sjzx
(
    index int,
    application varchar(255),
    vsysname varchar(255),
    upflow bigint,
    downflow bigint,
    flow bigint,
    sessionNum bigint,
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (index, ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_yyssllpm_sjzx.index IS '序号，主键';
COMMENT ON COLUMN usr_netsec.t_yyssllpm_sjzx.application IS '应用名称';
COMMENT ON COLUMN usr_netsec.t_yyssllpm_sjzx.vsysname IS '防火墙虚拟系统资源分配配置实例';
COMMENT ON COLUMN usr_netsec.t_yyssllpm_sjzx.upflow IS '上行（单位：Mbps）';
COMMENT ON COLUMN usr_netsec.t_yyssllpm_sjzx.downflow IS '下行（单位：Mbps）';
COMMENT ON COLUMN usr_netsec.t_yyssllpm_sjzx.flow IS '总流量（单位：Mbps）';
COMMENT ON COLUMN usr_netsec.t_yyssllpm_sjzx.sessionNum IS '会话数';
COMMENT ON COLUMN usr_netsec.t_yyssllpm_sjzx.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_yyssllpm_sjzx IS '应用实时流量排名';

ALTER TABLE usr_netsec.t_yyssllpm_sjzx
    OWNER TO usr_netsec;