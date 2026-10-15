---
name: plugin-creator
description: 创建 LessChaos 插件包。用于 plugin.json、Skill、MCP 接入、本机试用，以及向当前组织提交共创改进并跟进审核发布。
---

<!-- 本 Skill 拥有插件创建、本机试用与企业共享的工作步骤。权限、包校验、安装事务及发布回执归正式宿主能力。 -->

# 创建插件

读取用户要解决的重复任务，目标明确时直接创建包。包完成后按用户意图选择本机试用或组织共创；能由正式工具执行的步骤直接推进，管理员在产品差异页作出真实审核决定。

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

## 7. 组织共创与共享

用户要求“供公司使用”“上传企业平台”或改进组织插件时，读取 [组织共创流程](references/organization-sharing.md)，按真实资格提交候选、观察审核并发布已批准修订。普通 Desktop 席位可以提交；审核与正式发布各自核对权限，管理员也先提交再审核。

只要求创建插件时，先交付可检查的包，再询问是否提交组织。用户已经明确共享意图时，继续获准步骤。完成时分别报告包、待审修订、审核决定、正式发布与本机安装的实际结果。

## 8. 其他分发

给他人 ZIP；或放进 Git 仓库并提供 `marketplace.json`（`name` 加 `plugins` 数组，每项 `name`、`source`、`description`），接收方可“添加 → 添加插件市场”登记固定 commit 快照。公开生态贡献通过 lesschaos-ecosystem 仓库的 Issue／Pull Request；组织共享不会自动公开到官方生态。

## 完成条件

本机试用以正式安装结果及后续技能发现为准；Stdio 包以用户完成启动信任为准。组织提交以待审回执为准；审核以真实审核决定为准；共享发布以正式发布回执为准。能力或权限缺口交付已完成包、具体修订和下一项可执行动作。
