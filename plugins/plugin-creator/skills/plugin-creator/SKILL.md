---
name: plugin-creator
description: 创建 LessChaos 插件包。用于 plugin.json、Skill 与 MCP 接入声明、本机安装，以及发布到当前组织的企业共享平台。
---

<!-- 本 Skill 拥有插件创建、本机试用与企业共享的工作步骤。权限、包校验、安装事务及发布回执归正式宿主能力。 -->

# 创建插件

读取用户要解决的重复任务，目标明确时直接创建包。包完成后按用户意图选择本机试用或企业共享；企业发布通过正式工具完成，用户不用手动转到管理页面。

## 1. 选组成

- 任务主要是「指导模型做某类工作」→ 纯 Skill 包（只有 plugin.json + skills/）。
- 需要连接一个 MCP 服务 → 包根加 mcp.json；两种组成可以共存。
- 模型已有的能力（命令执行、`@路径`、其他已装插件的技能）不要打包，Skill 正文直接引用。
- 包内程序不自动成为 Tool；作为技能附带脚本经既有受控执行使用，作为 Stdio 接入端点写进 mcp.json。

## 2. 包结构

```text
my-plugin/
├── plugin.json        # 必需
├── skills/
│   └── my-skill/
│       └── SKILL.md   # name 必须与目录同名
├── mcp.json           # 可选
└── com.lesschaos/     # 可选
    ├── Plugin.md      # 可选：职责、组成与使用入口
    └── assets/icon.svg
```

所有路径解析后必须留在包根。

## 3. plugin.json

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "一句话短用途：做什么、何时选用。",
  "keywords": ["sample"]
}
```

- `name`：1–64 个小写字母、数字、`-`、`.`；首尾是字母或数字；不含 `--` 与 `..`。
- `version` 用 SemVer；官方发布要求它与目录条目一致。
- `description` 是 UI 与模型发现共用的唯一短用途，不另写第二份摘要。
- 展示名与图标放 `extensions.com.lesschaos.interface`（`displayName`；`icon` 用 `./com.lesschaos/assets/<文件>`）。

## 4. Skill

- 位置固定在 `skills/` 的直接子目录；`name` 与目录同名，小写字母、数字、单连字符，至多 64。
- frontmatter 子集：`name`、`description`（缺失或全空白该技能被丢弃并记诊断）、可选 `disable-model-invocation`。
- 正文写直接指令，写法遵循内置 skill-creator 技能的指引。
- 配套 `references/`、`scripts/` 按技能目录的相对路径引用。

## 5. mcp.json

只有包根这一个位置，只有 `$schema` 与 `mcpServers` 两个字段。

- `stdio`：`type`、`command`、`args`、`env`、`cwd`。`command` 是单一可执行名或 `./` 开头的包内路径，必须是字面量；`cwd` 缺省 `${PLUGIN_ROOT}`，可用 `./相对路径`、`${PLUGIN_ROOT}/…`、`${PLUGIN_DATA}/…`；`env` 不得覆盖 `PLUGIN_ROOT` 与 `PLUGIN_DATA`。
- `streamable-http`：`type`、`url`、`headers`。URL 须 HTTPS（本机 loopback 可 HTTP），不带用户信息；`headers` 不得含 `authorization`、`proxy-authorization`、`x-api-key`——凭据不进包声明，授权在安装后经产品完成。
- `sse` 不支持。接入声明有效与连接就绪是两件事，失败诊断如实呈现。

## 6. 本机试用

用户要求本机试用时执行本节；企业共享沿第 7 节完成。

1. 包目录就绪后装载并调用 `builtin.plugin_install`，参数是包目录的绝对路径；不需要先压缩，ZIP 路径也可以。用户在对话里批准这次安装。
2. 返回安装结果即完成：名称、版本、组成与非致命诊断。技能在下一条消息进入 `<available_skills>` 清单（带 `<plugin>` 归因行），届时用 `/技能名` 验证。返回错误则按原文修包重试——校验诊断、名称冲突（同名已装，先卸载）都如实呈现，不绕过。
3. 含 Stdio 接入的包不能对话内直装（需要启动信任）：打成 ZIP（包根内容为压缩根），指引用户在插件工作区「添加 → 上传插件压缩包」走候选确认。

对话内安装的插件同样是固定快照，没有更新检查；改版先卸载同名安装再装新内容。纯 Skill 原型可以先落在 `~/.agents/skills/<name>/` 快速试用，注意自管同名技能会遮蔽插件技能，正式打包前改名或移除原型。

## 7. 企业共享

1. 通过 `capability.load` 装载 `builtin.plugin_publish_status`、`builtin.plugin_publish` 的实际定义。先调用资格查询，使用本 Run 的当前组织，核对 `canPublish` 与 `storageConfigured`。查询失败是资格未知，不当作无权限或有权限；权限不足时交付已完成的包并说明缺口。存储未配置时说明需要平台管理人员准备，保留成果。
2. 用户已说“发布给公司使用”“上传到企业共享平台”等明确要求时继续发布。只要求创建插件且共享意图未明确时，先完成可检查的包；具备发布资格后询问是否企业共享。有权限本身不是发布意图。
3. 调用 `builtin.plugin_publish`，只传包目录或 ZIP 的绝对路径；发布者和组织由可信宿主取得。纯 Skill 与含 MCP 的包都可发布；发布不会启动包内程序或替同事完成登录。
4. 以工具返回的正式回执确认成功，交付组织、插件名、版本和发布 ID。上传或响应中断时说明结果未知；保留同一份包，按原发布意图重试或核查组织目录。同版本内容不能变更，修改后递增版本再发布。
5. 同事选用共享内容时，装载 `builtin.organization_plugins` 查询真实目录，再通过 `builtin.plugin_install_organization` 使用指定发布 ID。安装与连接分别核对；工具返回 `requires_startup_trust` 时，用其实际 `packagePath` 指引“插件 → 添加 → 上传插件压缩包”完成启动信任。

宿主没有这些工具时，交付已完成的包并说明企业发布尚未接入；保留已有本机试用流程。使用宿主的正式发布能力，不自行取得存储密钥或把写入 bucket 当作企业发布。

## 8. 其他分发

给他人 ZIP；或放进 Git 仓库并提供 `marketplace.json`（`name` 加 `plugins` 数组，每项 `name`、`source`、`description`），接收方可“添加 → 添加插件市场”登记固定 commit 快照。公开生态贡献通过 lesschaos-ecosystem 仓库的 Issue／Pull Request；组织共享不会自动公开到官方生态。

## 完成条件

本机试用以正式安装结果及后续技能发现为准；Stdio 包以用户完成启动信任为准。企业共享以实际发布回执为准，包已生成、上传已接收、已安装与已发布分别报告。
