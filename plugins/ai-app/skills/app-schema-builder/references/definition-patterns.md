<!-- 本文拥有 App 初始定义、关联配置与结构演进的示例；定义校验和数据迁移规则由 App 域拥有。 -->

# 建模与定义提交

## 客户与订单的初始定义

用户要跟踪客户和订单时，先确定一行订单是订单头还是商品明细。下面是订单头模型的 `app_create` 参数示例；真实创建使用本次确定的新稳定身份。

```json
{
  "appId": "019b3470-a04e-7b89-93fc-55b81cc00001",
  "name": "客户与订单",
  "expectedVersion": null,
  "tables": [
    {
      "id": "customers",
      "name": "客户",
      "primaryFieldId": "customer_name",
      "fields": [
        {
          "id": "customer_name",
          "name": "客户名称",
          "fieldType": "text",
          "cardinality": "one"
        },
        {
          "id": "customer_code",
          "name": "客户编号",
          "fieldType": "text",
          "cardinality": "one"
        }
      ],
      "uniques": [["customer_code"]]
    },
    {
      "id": "orders",
      "name": "订单",
      "primaryFieldId": "order_no",
      "fields": [
        {
          "id": "order_no",
          "name": "订单号",
          "fieldType": "text",
          "cardinality": "one"
        },
        {
          "id": "customer",
          "name": "客户",
          "fieldType": "link",
          "cardinality": "one",
          "config": {
            "link": {
              "targetTable": "customers",
              "direction": "one_way",
              "cardinality": "many_to_one"
            }
          }
        },
        {
          "id": "amount",
          "name": "订单金额",
          "fieldType": "number",
          "cardinality": "one",
          "config": {
            "number": {
              "kind": "currency",
              "currencyCode": "CNY",
              "decimalPlaces": 2
            }
          }
        },
        {
          "id": "status",
          "name": "状态",
          "fieldType": "select",
          "cardinality": "one",
          "config": {
            "select": {
              "options": [
                { "id": "draft", "label": "草稿" },
                { "id": "won", "label": "已成交" }
              ]
            }
          }
        }
      ],
      "uniques": [["order_no"]]
    }
  ]
}
```

`Field.cardinality` 是 `one / many`；`config.link.cardinality` 是关系的 `one_to_one / many_to_one / one_to_many / many_to_many`，两者不同。关联目标键是 `targetTable`。双向关联必须按完整定义声明一对匹配字段和反向身份，不能只加一个 `backFieldId` 就假定系统已补齐另一端。

App 创建接收完整初始定义，图标和颜色不属于这个请求。当前 Tool 定义若缺少提交所需的结构字段，应报告接线不匹配，不能自行拼 HTTP 请求补齐。

## 为已有订单增加负责人

1. 读现有定义及 `definitionVersion`，确定负责人是否已存在，避免同义重复列。
2. 保留每张表的 `fields`、`primaryFieldId`、`uniques`、`rules`、`views`，以及定义级 `userAttributes`、`disclosures`。这些内容组成下一版定义的基底。
3. 只向目标表增加用户需要的字段，例如单人员：

```json
{ "id": "owner", "name": "负责人", "fieldType": "user", "cardinality": "one" }
```

4. 将读取的 `definitionVersion` 映射为请求的 `expectedVersion`，连同完整 `tables` 调用 `app_define`。
5. 重读新定义，核对负责人字段和所有原有声明。用户只要求加字段时，现有记录保持原值，后续分配负责人使用记录技能。

已有人员从单值改为多值会改变字段形状，Page bindings 等下游声明可能因此失效；将这一影响随变更说明，不擅自重写页面。

## 公式与跨 App 引用的处理

公式表达式、Lookup 来源及授权身份必须来自当前合同或已存在且已核对的定义，不能把熟悉的电子表格语法当作产品已经支持。当前插件若没有提供公式语言、诊断或来源授权工具，复杂需求先交付明确的依赖与缺口，仍可完成其他可独立落地的结构。

一次 `app_define` 只演进一个 App。需要修改多个 App 时逐个保存回执，后一个失败不回滚前一个；同一完整定义中的表和字段保持各自原有稳定 ID。
