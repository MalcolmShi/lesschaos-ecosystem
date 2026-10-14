<!-- 本文拥有 Page 生成时需要的源码、绑定和版本操作说明；正式 wire 与准入由当前 Page Tools 拥有。 -->

# Page 资源与绑定

## 生成 document

`app_page_save` 参数为 `appId`（归属）、`pageId`、`expectedRevision` 和 `document`。document 包含 `name`、`source` 和命名 `bindings`：

```json
{
  "name": "回款工作台",
  "source": {
    "sdkVersion": 1,
    "entry": "src/Page.tsx",
    "files": {
      "src/Page.tsx": "export default function Page({ total }: { total?: string }) { return <main><h1>回款工作台</h1>{total === undefined ? <p role=\"status\">实时数据尚未接入</p> : <output aria-label=\"订单总额\">{total}</output>}</main>; }"
    }
  },
  "bindings": {
    "order_totals": {
      "appId": "sales",
      "tableId": "orders",
      "fields": [
        { "fieldId": "amount", "fieldType": "number", "cardinality": "one" }
      ],
      "operation": {
        "kind": "aggregate",
        "statistics": [{ "field": "amount", "func": "sum" }]
      }
    },
    "open_invoices": {
      "appId": "finance",
      "tableId": "invoices",
      "fields": [
        { "fieldId": "invoice_no", "fieldType": "text", "cardinality": "one" },
        { "fieldId": "amount", "fieldType": "number", "cardinality": "one" },
        { "fieldId": "status", "fieldType": "select", "cardinality": "one" }
      ],
      "operation": {
        "kind": "records",
        "filter": {
          "kind": "leaf",
          "field": "status",
          "operator": "eq",
          "value": {
            "kind": "literal",
            "value": { "kind": "select", "value": "open" }
          }
        },
        "sort": [{ "field": "amount", "direction": "desc" }]
      }
    }
  }
}
```

这是资源编码示例，演示 ID 必须替换为正式定义中的身份；示例展示组件的 `total` 是内部输入，并未接上 `order_totals`。真实页面按任务继续生成列表、状态和交互，再依据宿主实际 SDK 装配。数据连接缺失时保持可见的未接入状态，不用常量数字冒充查询结果。

## 文件与绑定准入

- `source.files` 保存完整文本，路径为相对 TS、TSX 或 CSS 路径；入口指向非空 TSX。当前限制 1–64 个文件、总文本至多 2 MiB，路径不带空段、`.`、`..`、反斜杠或绝对地址。
- binding 名为 1–80 个 ASCII 字母、数字或下划线，至多 128 个；名字表达数据用途，修改布局时保留仍有效的名字。
- `fields` 包含该绑定实际用到的所有字段，记录当前 `fieldType` 和 `one / many`。records 必须有显式字段投影。
- records 的排序字段键是 `field`；`app_query` 的排序字段键是 `fieldId`。两种输入分别按各自 Tool 定义生成。
- aggregate 的 `groupBy` 为可分组的单字段 ID，`statistics` 非空，项为 `{field, func}`；筛选、分组和统计字段全部在 fields 中。
- action 的 operation 为 `{"kind":"action","action":"create|update|delete"}`，其中 action 取一个实际枚举值。create／update 只声明可写字段，delete 的 fields 为空。

bindings 描述数据依赖和允许的操作形状，不携带用户、凭据或现成数据。Page Owner 与来源 App 的当前访问权分别核对；保存绑定不授予页面查看者读取该来源的权限。

## 版本操作

| 目的             | 操作                                                           |
| ---------------- | -------------------------------------------------------------- |
| 发现现有 Page    | `app_page_list({appId})`                                       |
| 读当前文档和诊断 | `app_page_read({appId, pageId})`                               |
| 创建             | `app_page_save`，新 pageId，expectedRevision 为 null           |
| 修改             | 读取当前 revision，保存完整下一版 document                     |
| 发布选择         | `app_page_publish({appId, pageId, expectedRevision, version})` |
| 回滚             | 发布选择指向仍保留的旧 version，expectedRevision 仍使用当前值  |
| 删除             | `app_page_remove({appId, pageId, expectedRevision})`           |

revision 是资源并发门，version 是不可变源码身份，definitionVersion 是来源 App 的结构依据。保存新源码产生新 version 和 revision；发布选择改变 revision，保留源码版本身份。三者不能互换。

## 诊断到修复

`app_page_read` 返回 `page`、`content`、`issues`。按问题中的 binding 定位，保留未受影响的内容：

| 诊断                                                               | 修复依据                                                                   |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| source_unavailable / table_missing / field_missing                 | 重新发现真实来源；无法取得时说明受影响区域，取得用户决定后才移除该功能     |
| field_shape_changed                                                | 读取当前类型与 cardinality，同时修改取值、展示和操作，不能只改声明消除诊断 |
| filter_invalid / sort_invalid / group_invalid / statistics_invalid | 核对引用字段已声明，并使用当前字段类型支持的操作                           |
| action_fields_invalid                                              | 去除系统与派生字段，确认只剩用户需要修改的正式可写字段                     |
| version / revision conflict                                        | 重读当前 Page，重新合并目标变化后提交                                      |

没有 issues 不证明源码能编译；编译通过不证明查看者能读所有来源；发布选择成功不证明已有可运行 URL。
