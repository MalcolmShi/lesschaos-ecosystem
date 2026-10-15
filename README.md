# LessChaos Ecosystem

LessChaos 官方开源生态仓库，维护插件、Skill 与配套的标准 AI 成员模板，帮助组织建立 AI 团队。生态内容开源公开、不设套餐门槛；这些内容为配合 LessChaos Agent 工作而生，离开 LessChaos 客户端不构成独立产品。

## AI 成员与配套插件

标准 AI 成员模板提供岗位身份、工作方法、默认展示信息及所需插件的引用；配套插件提供 Skill、工具和外部系统接入。模板与插件共同维护，成员配置、插件安装与实际执行各有自己的职责和生命周期。

产品接入流程为：用户先安装岗位配套插件；具有 AI 员工管理权限的管理员再在「AI 团队」选择标准模板，为新员工命名并明确创建。安装、取消命名或打开模板都不会自动创建员工；同一模板可显式创建多位员工，创建结果未知时按原意图核对，不重复新增。

模板只是创建起点。命名后的员工是当前组织持久保存的独立身份，档案由具有管理权限的人维护；模板或插件更新不会覆盖已创建员工的姓名、岗位提示词和记忆。使用者仍需在自己的客户端安装、启用配套插件；插件不携带员工 ID、使用者凭据或长期记忆，安装不授予额外数据访问权限。

首期员工在使用者的 LessChaos Desktop 中执行，继承所在对话的模型、基础工具、工作目录和运行策略。连接及软件缺口按实际状态显示；模板不是云电脑或常驻云端运行服务，安装与创建也不自动启动团队协作。

## 结构

- `plugins/` — 官方插件源码，一个插件一个目录，包含 `plugin.json`、Skill 与配套材料。
- `release` 分支 — 发布产物：`plugins/catalog.json` 与按摘要寻址的 `plugins/packages/<archive_digest>.zip`，由 GitHub Pages 静态服务。
- 客户端目录地址：`https://malcolmshi.github.io/lesschaos-ecosystem/plugins/catalog.json`。

## 官方插件

- `plugin-creator`（插件管理）：设计、创建和排查插件与 Skill。
- `data-reviewer`（数据核验）：数据核验员工模板与 `data-review` Skill；核对周报 CSV、指标口径、重复及缺失，交付行级证据。
- `report-writer`（报告整理）：报告整理员工模板与 `report-writing` Skill；从核验结果生成基础 Markdown 周报并保留待核对项。两项岗位插件均使用宿主既有文件与命令能力；可选辅助程序仅依赖本机 Python 3 标准库，不需要外部 MCP 或服务。
- `ai-app`（AI应用）：包含数据分析（`app-data-analysis`）、结构搭建（`app-schema-builder`）、记录修改（`app-record-editor`）和自由页面生成（`app-page-builder`）四个独立 Skill，共用可信原生 App Tools，支持当前 Organization 内获授权的跨 App 任务。执行实现由 LessChaos 宿主提供，包内不分发业务内核或页面运行器。

## 发布

发布由维护者在 LessChaos 主工程内运行发布命令完成：先校验插件包，再按摘要写入只读包，最后原子替换目录。外部贡献不直接修改 `release` 分支。

## 贡献

- 插件、Skill 和标准 AI 成员模板的增改通过 Issue 与 Pull Request 提出。
- Skill 遵循 agentskills.io 声明协议的 LessChaos 支持子集；插件包结构以发布校验为准，AI 成员模板位于包内 `com.lesschaos/members/`，由 `plugin.json` 的 `extensions.com.lesschaos.aiMembers` 引用，定义中的 `sources` 以 `self` 绑定本包。模板与岗位 Skill 同一不可变版本发布。

## 客制化

官方插件内容不可变：安装副本按摘要校验、随目录自动更新，改动会被判为损坏。客制化的正确路径是参照源码自建插件：

1. 复制 `plugins/<name>` 源码目录，修改 `plugin.json` 的 `name`——与已安装插件同名会被拒绝安装，技能同名会被先装载者遮蔽并记诊断。
2. 在 LessChaos 中以本地目录或 ZIP 导入，或登记 Git 市场（登记时固定快照，更新靠重新登记）。
3. 自建插件不进官方目录、不被自动更新；官方原件继续自动更新，两者互不影响。
