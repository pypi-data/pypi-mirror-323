CREATE TABLE usr_netsec.t_zjygywxfhyzxtjxx_sjzx
(
    name varchar(10),
    severity varchar(20),
    value bigint,
    jump_flag varchar(10),
    ts bigint    NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (severity, ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_zjygywxfhyzxtjxx_sjzx.name IS '威胁等级（中文）';
COMMENT ON COLUMN usr_netsec.t_zjygywxfhyzxtjxx_sjzx.severity IS '威胁等级';
COMMENT ON COLUMN usr_netsec.t_zjygywxfhyzxtjxx_sjzx.value IS '次数';
COMMENT ON COLUMN usr_netsec.t_zjygywxfhyzxtjxx_sjzx.jump_flag IS '是否跳转';
COMMENT ON COLUMN usr_netsec.t_zjygywxfhyzxtjxx_sjzx.ts IS '入库时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_zjygywxfhyzxtjxx_sjzx IS '最近一个月威胁防护严重性统计信息';

ALTER TABLE usr_netsec.t_zjygywxfhyzxtjxx_sjzx
    OWNER TO usr_netsec;