CREATE TABLE usr_netsec.t_zjygywxfhsj_sjzx
(
    id        varchar(255) NOT NULL,
    name      varchar(255),
    statistic bigint,
    severity  varchar(10),
    ts        bigint       NOT NULL DEFAULT EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000,
    PRIMARY KEY (id, ts)
);

-- 为字段添加注释
COMMENT ON COLUMN usr_netsec.t_zjygywxfhsj_sjzx.id IS '主键，唯一标识每条记录';
COMMENT ON COLUMN usr_netsec.t_zjygywxfhsj_sjzx.name IS '签名名称';
COMMENT ON COLUMN usr_netsec.t_zjygywxfhsj_sjzx.statistic IS '命中次数';
COMMENT ON COLUMN usr_netsec.t_zjygywxfhsj_sjzx.severity IS '威胁级别';
COMMENT ON COLUMN usr_netsec.t_zjygywxfhsj_sjzx.ts IS '入库实际时间';

-- 为表添加注释
COMMENT ON TABLE usr_netsec.t_zjygywxfhsj_sjzx IS '数据中心防火墙最近一个月威胁防护攻击事件';

ALTER TABLE usr_netsec.t_zjygywxfhsj_sjzx OWNER TO usr_netsec;