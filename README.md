# Personal Skills

一组面向日常开发的个人 skills，覆盖代码修改、长期任务推进、技术文档、任务委托、领域建模和配置安全检查。

## 安装

### Claude Code

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
```

安装完成后重启 Claude Code。克隆仓库开发时可以使用软链：

```bash
git clone <repo-url> personal-skills
cd personal-skills
./install.sh --link
```

常用选项：

```bash
./install.sh --no-force
./install.sh --dest /path/to/skills
./install.sh --dry-run
```

### ZCode

把需要的 skill 链到 `~/.agents/skills/` 或 `~/.zcode/skills/`。同一份 skill 选择一个目录即可，例如：

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/skills/helm ~/.agents/skills/helm
```

安装或更新后新开会话。

## 有哪些 skills

- [code-change-discipline](code-change-discipline/README.md)：修改代码前先选择测试策略；功能和 Bug 默认先测试后实现，小修也适用。
- [helm](helm/README.md)：先定目标、一次规划一个阶段，并在执行中按证据调整方向。
- [handoff](handoff/SKILL.md)：把当前工作整理成可核验的跨会话交接文档，或在新会话中核验并恢复任务锚点。
- [architecture-map](architecture-map/SKILL.md)：基于代码和可执行配置创建、更新或审计当前实现的交互式架构地图报告。
- [tocodex](tocodex/README.md)：把明确任务委托给 Codex CLI，并读取结果。
- [grill-me](grill-me/SKILL.md)：通过持续追问帮助梳理和检验设计。
- [grill-with-docs](grill-with-docs/SKILL.md)：在设计访谈过程中同步形成领域术语和 ADR。
- [domain-modeling](domain-modeling/SKILL.md)：维护领域语言、术语和架构决策。
- [security-audit](security-audit/README.md)：检查 Claude Code 配置中的可疑 hooks、MCP servers 和命令。

## 怎么用

安装后直接描述需求，相关 skill 会按场景启用。也可以显式指定：

```text
修复空端口被解析成 0 的 Bug
用 Helm 做这个支付回调重构
更新当前项目的架构地图报告
把这个任务交给 Codex
```

多步骤代码工作通常由 Helm 管理目标和阶段，同时由 `code-change-discipline` 管理测试策略。

## 更新与卸载

再次运行安装命令即可更新。卸载时删除对应的 skill 目录，然后重启客户端：

```bash
rm -rf ~/.claude/skills/<skill-name>
```

本仓库中的每个 skill 都是独立目录，具体行为和规则见各自的 `SKILL.md`。
