<!-- 本文拥有 plugin-creator 的组织共创、审核观察与发布工作步骤。权限判断、正式事实及安装事务由宿主提供。 -->

# 组织共创流程

先完成用户要改进的包，再沿提交、审核、发布和安装各自的正式回执推进。组织与提交者由本 Run 的可信宿主范围取得。

## 1. 核对宿主与资格

用 `capability.load` 读取下表所需工具的真实定义，再调用 `builtin.plugin_publish_status`。按当前返回定义传参；下表是支持这些工具的宿主合同，工具缺失时采用文末恢复路径。

| 工具                                  | 参数与结果                                                                                                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `builtin.plugin_publish_status`       | `{}`；返回 `organizationId`、`canRead`、`canSubmit`、`canReview`、`canPublish`、`storageConfigured`                                                                                  |
| `builtin.plugin_proposals`            | `{}`；返回 `organizationId`、`proposals`、`baselines`、`partial`。基线条目是正式发布的 `id`、`name`、`version`                                                                       |
| `builtin.plugin_propose`              | `path`（绝对目录或 ZIP）、`proposalId`（稳定 UUID）、`expectedRevision`（创建用 0）、可选 `baselineId`（正式发布 ID）；返回确定待审回执                                              |
| `builtin.plugin_proposal_inspect`     | `proposalId`、`revision`；可选 `receiptOnly: true` 只查审核和发布事实。读差异时不传 receiptOnly：无 `file` 返回文件索引，可用 `offset` 继续；指定 `file` 取得该文件有界 before/after |
| `builtin.plugin_publish`              | `proposalId`、`revision`；返回正式发布回执。路径形式是兼容入口，同样要求确定候选已批准，不能替代审核                                                                                 |
| `builtin.organization_plugins`        | `{}`；返回当前组织已正式发布的目录                                                                                                                                                   |
| `builtin.plugin_install_organization` | `id`（正式发布 ID）；返回本机安装结果或启动信任要求                                                                                                                                  |

`canSubmit` 决定当前 Desktop 席位是否可提交，不能用 `canPublish` 代替。`canReview` 和 `canPublish` 分别用于审核管理和正式发布，均不表示已存在审核决定。`storageConfigured` 只说明共享包存储是否配置。查询失败时资格未知，保留包并交付实际错误。

## 2. 提交确定候选

1. 从 `plugin_proposals` 的 `baselines` 核对当前组织同名插件的正式版本。已有组织插件使用它的发布 ID 作 `baselineId`，后续版本提高 SemVer；新插件省略基线。`partial: true` 时结果不完整，不能据未出现就判断不存在；有歧义时先请用户确认正式基线。
2. 保留完整包，包含未修改的 Skill、脚本、MCP 声明和资源。凭据沿产品登录取得，不写进包。组织候选保持原插件名，改版递增版本；从官方插件另建组织插件须选择独立名称，避免已装同名冲突。
3. 为本次提案生成一次 UUID 并保留，用 `plugin_propose` 提交。新提案 `expectedRevision: 0`；修改自己的已有提案时使用当前修订号。用户已要求组织共享时直接执行可获准步骤，工具自身的动作批准仍照常处理。
4. 记录回执的 `id`、`organizationId`、`revision`、`baselineId`、`state`、`release.name`、`release.version`、`release.content_digest`、`release.archive_digest`。成功提交的 `state` 是 `pending`，交付“已提交待审核”。它不安装、不替换正式版本，也不改变员工配置。

响应中断或结果未知时，保持同一 `proposalId`、`expectedRevision`、基线和包字节，先查询列表与确定修订；必要时重试同一提交。观察不到不等于提交失败；不要改 UUID 盲目新增。新内容使用新修订，不能复用旧批准。

## 3. 跟进真实审核

用 `plugin_proposal_inspect` 观察确定修订，先读回执，再按需读取文件差异。结果以 `Proposal revision:` 和 `Details:` 两段文本提供，Details 含 `proposal`、`review`、`publication`；不要假设整个工具文本是单个 JSON。`nextOffset` 指示索引的下一段，二进制和截断文字按标记报告，未展开内容不称已审完。

管理员或授权审核者在“插件 → 组织共创”的确定修订差异页批准或拒绝；交付提案编号、修订及待办动作。宿主没有供模型写入审核的工具，聊天中“同意”“我是管理员”也不能替代产品产生的审核回执。普通席位提交后可继续独立工作，待管理员完成审核再接续。

| `proposal.state` | 下一步                                                                     |
| ---------------- | -------------------------------------------------------------------------- |
| `pending`        | 等待管理员在差异页审核；保持待审状态                                       |
| `approved`       | 检查 `review.decision` 是 `approved`、具体审核人和时间，再核对当前发布资格 |
| `rejected`       | 交付拒绝决定；需要调整时创建新修订重新提交                                 |
| `stale`          | 正式基线或当前修订已变化，核对新基线并提交新修订重新审核                   |
| `published`      | 读取实际 `publication`，报告已存在的正式发布，不重复创建                   |

`receiptOnly: true` 只取得正式存储中的审核和发布事实，适合核对中断结果；包暂时不可取得时仍可查回执。包不可取得也不能宣称已完成包检查或新发布。

## 4. 发布已批准修订

共享意图已明确、确定修订已有真实批准且当前 `canPublish` 为 true 时，调用 `plugin_publish` 的 `proposalId` 和 `revision` 形式。服务仍会重验发布资格、候选内容、当前修订及正式基线。没有发布资格时交付已批准修订，请有资格的人发布，不代用他人身份。

成功以返回 `id`、`organizationId`、`release`、`publishedBy`、`publishedAt` 的正式回执为准；核对组织、插件名、版本与候选摘要，交付发布编号。`approved` 只证明已审核，不能称已发布。响应未知时先以相同修订 `receiptOnly: true` 核对 `publication`；确需重试也使用相同修订，不能改包或转用路径形式绕过原决定。

## 5. 安装与同事使用

正式发布不会替任何同事安装，也不会改变当前 Run、连接登录或启动信任。用户要求本机使用时，以 `organization_plugins` 的实际发布 ID 调用 `plugin_install_organization`；同事在其账号分别选择安装。

返回 `requires_startup_trust` 时，使用返回的 `packagePath` 指引“插件 → 添加 → 上传插件压缩包”，由用户完成 Stdio 启动信任。普通名称冲突沿插件安装诊断处理；安装前先保留正在使用的内容，切换版本和插件登录分别报告。组织受管更新、自动替换安装或员工模板迁移不由这次发布推导。

## 旧宿主与失败恢复

- 任何必需的候选、检查或发布工具缺失：交付已完成的包、所需缺失工具及宿主升级入口；继续已可用的本机试用。旧版只有 `plugin_publish(path)` 也不能跳过候选与审核，不自行调用 HTTP、取得存储密钥或上传 bucket 伪装发布。
- 没有 `canSubmit`：交付包与席位缺口；没有审核或发布资格仍可完成获准的候选提交，不把普通席位误判为不能共创。
- 存储未配置或不可用：交付包与实际存储缺口；没有成功回执就保持未确认。资格不足、存储失败、拒绝和结果未知分别表达。
- 组织切换或登录失效：旧 Run 不改投新组织，保留候选身份与包；在用户目标组织的有效对话接续。

组织共享是私有分发。公开到 LessChaos 生态仍走开源仓库维护者的独立发布流程，不因组织提交、批准或安装而自动公开。
