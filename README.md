# LessChaos Ecosystem

LessChaos 官方插件、Skill 与 Expert 生态的源码与发布产物仓库。生态内容开源公开、不设套餐门槛；插件为配合 LessChaos 的 agent 工作而生，离开 LessChaos 客户端不构成独立产品。

## 结构

- `plugins/` — 官方插件源码，一个插件一个目录（含 `plugin.json`、Skill 与配套材料）。
- `release` 分支 — 发布产物：`plugins/catalog.json` 与按摘要寻址的 `plugins/packages/<archive_digest>.zip`，由 GitHub Pages 静态服务。
- 客户端目录地址：`https://malcolmshi.github.io/lesschaos-ecosystem/plugins/catalog.json`。

Expert 生态源码目录待其目录协议定稿后开放；Skill 生态当前随插件包分发。

## 发布

发布由维护者在 LessChaos 主工程内运行发布命令完成：先校验插件包，再按摘要写入只读包，最后原子替换目录。外部贡献不直接修改 `release` 分支。

## 贡献

- 插件、Skill 的增改通过 Issue 与 Pull Request 提出，源码放对应目录。
- Skill 遵循 agentskills.io 声明协议的 LessChaos 支持子集；插件包结构以发布校验为准，命名与版本语义在评审中约定。
