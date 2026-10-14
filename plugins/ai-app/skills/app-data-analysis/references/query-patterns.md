<!-- 本文拥有 App 查询、聚合与跨来源对账的操作示例；实时参数和合法操作由当前 Tool 定义拥有。 -->

# 查询与对账模式

示例中的 ID 是演示身份。先从当前定义解析真实 ID 与选项，再把参数传给当前目录中的对应 Tool。成功输出中的 `result` 是业务信封，读取其 `kind` 与 `value`，不要把外层 `resource` 当作业务数据。

## 筛选明细并续页

假设定义已确认 `orders` 中 `status` 是单选、`won` 是已成交选项，`amount` 是金额字段。查询成交订单中金额至少 1000 的记录：

```json
{
  "appId": "sales",
  "query": {
    "tableId": "orders",
    "fields": ["order_no", "customer_code", "amount", "status"],
    "filter": {
      "kind": "and",
      "children": [
        {
          "kind": "leaf",
          "field": "status",
          "operator": "eq",
          "value": {
            "kind": "literal",
            "value": { "kind": "select", "value": "won" }
          }
        },
        {
          "kind": "leaf",
          "field": "amount",
          "operator": "greater_equal",
          "value": {
            "kind": "literal",
            "value": { "kind": "number", "value": "1000" }
          }
        }
      ]
    },
    "sort": [{ "fieldId": "amount", "direction": "desc" }],
    "limit": 100
  }
}
```

下一页保持 `query` 不变，在外层增加 `cursor`，值为返回的 `nextCursor` 原文。游标是不透明字符串。字段投影取返回的 `echo.fields`；行身份和版本取 `recordId`、`revision`；查询依据取 `basis.definitionVersion`、`basis.datasetSequence`。

修改排序、筛选或投影后从第一页开始。读取某条指定记录优先 `app_read_record`，不要把 `anchor` 误当筛选条件。

## 服务端聚合

按地区统计成交金额，并检查缺失金额：

```json
{
  "appId": "sales",
  "tableId": "orders",
  "filter": {
    "kind": "leaf",
    "field": "status",
    "operator": "eq",
    "value": {
      "kind": "literal",
      "value": { "kind": "select", "value": "won" }
    }
  },
  "groupBy": "region",
  "statistics": [
    { "field": "amount", "func": "sum" },
    { "field": "amount", "func": "filled" },
    { "field": "amount", "func": "empty" }
  ]
}
```

分组结果使用 `groups[].key`、`count` 和 `statistics`；不分组时使用 `statistics`。统计值可为 `number`、`day` 或 `null`，数值载荷仍是字符串。`null` 表示没有可统计的非空值，保留这个含义。

时间范围在请求前按用户业务时区确定；日期字段与时间戳字段分别使用其支持的 FilterTree 操作。需要按月趋势而当前 Tool 无时间分桶时，按明确月区间分别聚合，或完整读取必要日期和数值后分桶；不得给 `groupBy` 填 SQL 表达式。

## 跨 App 回款对账

用户要求“比较销售订单和财务回款，找未收齐的订单”时：

1. 分别读取销售与财务定义，确认两侧共同使用的稳定订单业务编号、币种、金额及状态；各 App 的 `recordId` 不天然相同。
2. 销售侧按用户口径排除取消订单；财务侧区分已入账与待确认回款。先按订单编号和币种各自汇总，再匹配。
3. 一笔订单多次回款属于一对多。先加总回款再与订单额比较，不把订单额复制到每笔回款行相加。
4. 将订单分为未回款、部分回款、已收齐、超额回款。缺编号、重复订单编号、币种不一致和孤立回款单列，不能强行匹配。
5. 某来源拒绝访问时，已读取来源仍可展示，但不交付“未收齐订单全集”。两来源读取先后不同，说明对账依据分别来自哪次读取。

只要求找差异就止于对账结果；冲销、补录或改状态属于独立的记录写入任务。
