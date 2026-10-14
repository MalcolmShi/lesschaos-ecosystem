<!-- 本文拥有记录写入的值编码、并发依据与命令回执示例；合法值和原子提交由 App 域拥有。 -->

# 记录写入模式

## 单条记录读改写

用户要求“把这笔订单标为已成交”时，读取 `app_read_record` 的目标状态及必要判断字段。假设正式结果确认定义版本 7、数据集序列 42、记录 revision 3，且 `won` 是当前单选项 ID，调用 `app_update_record`：

```json
{
  "appId": "sales",
  "tableId": "orders",
  "recordId": "order_42",
  "commandId": "019b3470-a04e-7b89-93fc-55b81cc00002",
  "operationGroupId": "019b3470-a04e-7b89-93fc-55b81cc00003",
  "expectedDefinitionVersion": 7,
  "expectedDatasetSequence": 42,
  "expectedRevision": 3,
  "values": { "status": { "kind": "select", "value": "won" } }
}
```

这里的三个 expected 值都来自同一次有效读取，示例数字不能用于真实请求。已有状态就是目标值时不必强行制造更新；说明无需变化。

## 值编码

| 语义             | 值形状                                                                                             |
| ---------------- | -------------------------------------------------------------------------------------------------- |
| 修改文本         | `{"kind":"text","value":"客户回访"}`                                                               |
| 精确数字         | `{"kind":"number","value":"1280.50"}`                                                              |
| 清空             | `{"kind":"null"}`                                                                                  |
| 勾选             | `{"kind":"checkbox","value":true}`                                                                 |
| 单选／多选       | `{"kind":"select","value":"won"}` / `{"kind":"selects","values":["tag_a","tag_b"]}`                |
| 日期／带时间日期 | `{"kind":"date","value":"2026-10-14"}` / `{"kind":"date_time","value":"2026-10-14T02:00:00.000Z"}` |
| 人员／多人       | `{"kind":"user","value":"member_id"}` / `{"kind":"users","values":["member_a","member_b"]}`        |

未提供的字段保持原值。清空多值字段使用 Null；多值数组表示完整替换，追加一人或一个标签需先读原集合再构造目标集合。附件值引用已存在的附件身份；当前工具没有上传能力时，不把本地路径或外部 URL 当附件 ID。

## 关联使用元素补丁

读取时关联值可能是 `link` 或 `links`，写入时不把这两种值放进 create／update 的 values。使用 `app_command` 的以下 mutation，命令仍携带正式 definitionVersion 与 datasetSequence：

```json
{
  "kind": "link_patches",
  "recordId": "order_42",
  "fieldId": "customer",
  "patches": [{ "kind": "add", "target": "customer_a" }]
}
```

单值关联 Add 会替换原目标，Remove 命中原目标时清空。多值关联按元素 Add／Remove，不替换未触及的边；清空或完整替换前必须取得完整旧集合，无法证明读全时保留缺口。修改单个关联元素只提交需要的元素补丁。

新建订单并设置客户时，显式确定新订单 Record ID，同一 Command 先 Create 普通字段，再对这个 Record ID 执行 LinkPatches；目标客户也可引用本命令前面已创建的记录。任一部分被拒绝，整条单 App Command 不提交。关联的 target 使用该字段已声明目标表中的真实记录身份，跨 App 数据组合不等于可以任意跨 App 建边。

## 单 App 跨表 Command

同一 App 内“创建跟进记录并更新订单状态”可放入一个 Command：

```json
{
  "appId": "sales",
  "command": {
    "commandId": "019b3470-a04e-7b89-93fc-55b81cc00004",
    "operationGroupId": "019b3470-a04e-7b89-93fc-55b81cc00005",
    "expected": { "definitionVersion": 7, "datasetSequence": 42 },
    "tables": [
      {
        "tableId": "followups",
        "mutations": [
          {
            "kind": "create",
            "recordId": "followup_42",
            "values": { "title": { "kind": "text", "value": "确认成交" } }
          }
        ]
      },
      {
        "tableId": "orders",
        "mutations": [
          {
            "kind": "update",
            "recordId": "order_42",
            "expectedRevision": 3,
            "values": { "status": { "kind": "select", "value": "won" } }
          }
        ]
      }
    ]
  }
}
```

删除使用 `{"kind":"delete","recordId":"…","expectedRevision":3}`，不带 values。只有用户明确要求的删除才进入变更集；查询未返回某条记录不能证明它已被删除。

## 核对回执与重试

Tool 的 `result` 中有 `kind` 和 `value`。`app_update_record` 成功返回 `modelOutcome`；`app_command` 返回 `commandOutcome`。其 `value.kind` 为 `committed` 或 `unchanged`；提交回执字段直接位于 `value`，不额外假设嵌套 `receipt`。

跨 App 例：销售状态更新已 committed，财务补录 denied。记录两个独立结果，只重做尚未成功且有明确处置方案的财务部分。财务 outcome unknown 时原样重试财务 Command，销售部分保持已完成；重试仍未知就交付部分完成及未知命令身份。

创建记录和导入还要检查用户给定的业务唯一键。正常新建与未知命令重试不同：前者生成新身份，后者复用原载荷；不能因为重读时暂未看到记录就把未知写入改为新的创建请求。
