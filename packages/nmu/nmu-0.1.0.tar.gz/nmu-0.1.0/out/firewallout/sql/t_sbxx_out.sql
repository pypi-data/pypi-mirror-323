CREATE TABLE usr_netsec.t_sbxx_out
(
    state_version varchar(255),
    state_time varchar(40),
    system_run_time varchar(255),
    state_fanState varchar(20),
    state_envir varchar(20),
    state_hrpState varchar(20),
    state_onlineUsr bigint,
    state_productVersion varchar(255),
    state_hostName varchar(255),
    device_sn varchar(255),
    state_vfw varchar(40),
    state_ipv6 varchar(40),
    state_nat64 varchar(40),
    state_pwrState varchar(255),
    state_agilenetState boolean,
    lastLoaded_success boolean,
    state_lastLoaded varchar(255),
    cpuUsedData varchar(10),
    memoryUsedPer varchar(10),
    flashPer varchar(10),
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (device_sn, ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_version IS '版本信息';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_time IS '时钟信息';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.system_run_time IS '运行时长';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_fanState IS '风扇状态';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_envir IS '设备温度';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_hrpState IS '双机热备状态';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_onlineUsr IS '在线用户数';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_pwrState IS '电源状态';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_productVersion IS '产品版本号';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_hostName IS '设备名称';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.device_sn IS '产品序列号';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_vfw IS '虚拟系统';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_ipv6 IS 'IPv6';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_nat64 IS '敏捷网络功能';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_agilenetState IS 'AgileNet 状态';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.lastLoaded_success IS '上次登录是否成功';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.state_lastLoaded IS '上次登录信息';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.cpuUsedData IS 'CPU占用率';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.memoryUsedPer IS '内存占用率';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.flashPer IS 'CF卡占用率';
COMMENT ON COLUMN usr_netsec.t_sbxx_out.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_sbxx_out IS '设备信息';

ALTER TABLE usr_netsec.t_sbxx_out
    OWNER TO usr_netsec;