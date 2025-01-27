CREATE TABLE usr_netsec.t_ydzssllpm_sjzx
(
    index int,
    sourceip varchar(40),
    "user" varchar(40),
    vsysname varchar(255),
    upflow bigint,
    downflow bigint,
    flow bigint,
    sessionNum bigint,
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (index, ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx.index IS '序号，主键';
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx.sourceip IS '源地址';
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx."user" IS '用户';
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx.vsysname IS '防火墙虚拟系统资源分配配置实例';
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx.upflow IS '上行流量（单位：Mbps）';
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx.downflow IS '下行流量（单位：Mbps）';
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx.flow IS '总流量（单位：Mbps）';
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx.sessionNum IS '会话数';
COMMENT ON COLUMN usr_netsec.t_ydzssllpm_sjzx.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_ydzssllpm_sjzx IS '源地址实时流量排名';

ALTER TABLE usr_netsec.t_ydzssllpm_sjzx
    OWNER TO usr_netsec;