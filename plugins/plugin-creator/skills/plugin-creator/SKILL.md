---
name: plugin-creator
description: 设计并创建 LessChaos 插件包。用于插件结构规划、plugin.json 与 mcp.json 声明、打包校验与对话内安装；不登记市场或发布。
---

<!-- 本 Skill 拥有插件包的设计、打包与对话内安装指引；安装批准与事务、市场登记和发布归宿主与用户。 -->

# 创建插件

先和用户确认要解决的重复任务，再按下述步骤产出包目录，然后经 `builtin.plugin_install` 安装（每次安装由用户在对话里批准）。本 Skill 不登记市场、不发布。

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

## 6. 安装与分发

1. 包目录就绪后装载并调用 `builtin.plugin_install`，参数是包目录的绝对路径；不需要先压缩，ZIP 路径也可以。用户在对话里批准这次安装。
2. 返回安装结果即完成：名称、版本、组成与非致命诊断。技能在下一条消息进入 `<available_skills>` 清单（带 `<plugin>` 归因行），届时用 `/技能名` 验证。返回错误则按原文修包重试——校验诊断、名称冲突（同名已装，先卸载）都如实呈现，不绕过。
3. 含 Stdio 接入的包不能对话内直装（需要启动信任）：打成 ZIP（包根内容为压缩根），指引用户在插件工作区「添加 → 上传插件压缩包」走候选确认。
4. 分发给他人：给对方 ZIP；或放进 Git 仓库并提供 `marketplace.json`（`name` 加 `plugins` 数组，每项 `name`、`source`（仓库内相对路径）、`description`），让接收方「添加 → 添加插件市场」登记，登记锁定 commit 快照。

对话内安装的插件同样是固定快照，没有更新检查；改版先卸载同名安装再装新内容。纯 Skill 原型可以先落在 `~/.agents/skills/<name>/` 快速试用，注意自管同名技能会遮蔽插件技能，正式打包前改名或移除原型。

## 完成条件

`builtin.plugin_install` 返回安装成功、技能出现在清单并能被 `/技能名` 调用；Stdio 包则用户完成插件页候选确认。
