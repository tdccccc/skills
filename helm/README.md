# Helm

先定目标，再分阶段执行；发现方向不对时，及时调整 plan 或 goal。

Helm 适合准备实际执行的多步骤 feature、refactor、migration 或其他 initiative。它把长期目标和当前步骤分开，避免一次规划太远，也避免明知走偏还继续完成旧计划。

> goal = 目的地 · phase = 当前航向 · journal = 航海日志

## 安装

### Claude Code

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
```

本地开发可以使用 `./install.sh --link`。

### ZCode

把 Helm 和必需的执行规则链到一个用户级目录：

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/skills/code-change-discipline ~/.agents/skills/code-change-discipline
ln -sfn /path/to/skills/helm ~/.agents/skills/helm
```

目标或设计尚未确定时，还可以安装可选的设计 skills：

```bash
ln -sfn /path/to/skills/grill-me ~/.agents/skills/grill-me
ln -sfn /path/to/skills/grill-with-docs ~/.agents/skills/grill-with-docs
ln -sfn /path/to/skills/domain-modeling ~/.agents/skills/domain-modeling
```

也可以使用 `~/.zcode/skills/`。安装或更新后新开会话。

## 怎么用

直接描述目标即可：

```text
用 Helm 给登录页增加密码强度提示，不改 auth 后端
这个支付回调重构比较大，先定目标再分阶段做
继续上次 Helm 的 password-strength
目标变了：成功标准改成……
```

也可以显式使用 `/helm`，或提到 `goal.md`、phase、re-steer。

## 它会怎么做

1. 先检查项目里是否有相关的进行中工作，有则继续。
2. 写一个精简的 `goal.md`，确定意图、成功标准和阶段。
3. 只详细规划当前 phase，后续阶段暂时保留标题。
4. 分块执行，每块完成验证后经过 Checkpoint 验收。
5. 发现路径或目标不合适时，立即调整并记录原因。
6. 默认把被接受的代码块和阶段转换分别提交，避免改动长期堆积；你也可以明确要求不提交。

## 逻辑改动怎么测试

Helm 会遵守 `code-change-discipline`：

- **功能和 Bug**：先看到测试按预期失败，再做最小实现，测试通过后跑相关回归。
- **纯重构和优化**：先建立基线并保持结果正确，不强造失败测试。
- **无法先测**：说明原因，并使用可行的替代验证。

## 会生成什么

产物放在当前项目中：

```text
docs/helm/<initiative-id>/
  goal.md        # 目标、成功标准、阶段和当前状态
  phases/        # 当前阶段的详细计划
  journal.md     # 重要转向、决定和交接记录；需要时创建
  research.md    # 可选的调研草稿
```

`initiative-id` 默认使用 `YYYY-MM-DD-语义化名称`，不会把小时分钟塞进目录名。若同名目录存在，Helm 会先判断是否应该继续已有工作；确实是不同任务时，优先细化名称，最后才使用 `-02`、`-03`。精确创建和更新时间记录在 `goal.md` 中。

`goal.md` 保持精简；具体任务和验证放进当前 phase。

## 中途改方向

| 情况 | Helm 会怎么处理 |
|------|-----------------|
| 步骤、库或文件选错，目标仍正确 | 调整当前 plan |
| 当前路径失败，大目标仍正确 | 将旧 phase 标为 superseded，用下一个编号创建替代 phase |
| 已完成的旧 phase 被新证据挑战 | 保留旧文件，用下一个编号创建复查或修正 phase，并检查后续 phase 是否仍可信 |
| 成功标准或核心意图变了 | 停止实现，修改 goal 并重新分阶段 |

例如 P1–P5 已完成后发现 P3 需要修正，Helm 会创建 P6，而不是重写 P3 或创建 P3b。P3 在原验收仍成立时保留 `done`；若新证据推翻了它，则改为 `superseded`，并只重新处理真正受到影响的后续阶段。

下次直接说“继续 Helm”，它会优先恢复已有的 active initiative。

## 什么时候别用

- 改一行或修一个显而易见的小 Bug
- 只想讨论，暂时不准备执行
- 紧急修复，Helm 的流程成本高于当前风险

这些场景不需要启用 Helm。只要涉及可执行逻辑，仍然遵守 `code-change-discipline`。

具体代理协议、状态规则和模板说明见 `SKILL.md` 与 `REFERENCE.md`。
