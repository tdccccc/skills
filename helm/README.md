# Helm

先定目标，再分阶段做，走偏了还能改方向。

Helm 是一个个人向的 **intent 工作流 skill**：用文件把「要做什么」和「眼下怎么做」分开，执行中途可以改 plan 或改 goal，而不是只在聊天里口头调整。

> goal = 目的地 · phase plan = 当前航向 · journal = 航海日志

## 安装

### 随本仓库安装（Claude Code）

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
# 或 clone 后：
./install.sh
# 开发时推荐软链：
./install.sh --link
```

### ZCode（用户级 skill）

把 `helm` 和它编排的独立 `technical-report` 链到一个 ZCode 会扫描的目录，例如：

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/skills/helm ~/.agents/skills/helm
ln -sfn /path/to/skills/technical-report ~/.agents/skills/technical-report
```

也可以改用 `~/.zcode/skills/`，但同一份 skill 选择一个发现目录即可，避免重复安装。

装完后**新开会话**（或重启客户端）再使用。

## 怎么用

对 agent 说清楚意图即可，例如：

```
用 helm 做：给登录页加密码强度指示器，要可测，别动 auth 后端
这个支付回调重构有点大，用 helm 先定 goal 再分 phase
继续上次 helm 的 password-strength
目标变了：成功标准改成……
```

也可以显式：`/helm …` 或提到 `goal.md` / `先定目标再做` / `re-steer`。

Agent 会：

1. 先找有没有进行中的 initiative（`docs/helm/*/goal.md` 且 `status: active`）→ 有则接着做  
2. 没有则写薄 `goal.md`（目标 + 成功标准 + 阶段标题）  
3. 只细写**当前** phase 的 plan  
4. 按步骤执行（默认本会话；可委托 subagent 执行某个 phase）  
5. 每个 meaningful chunk 通过验证并由 Checkpoint 接受后，若项目启用了技术报告，调用独立 `technical-report` skill 同步当前实现
6. 每个被接受的 chunk、每次 phase 转换 / 转向 / 收尾后 git commit（实现代码与 helm 产物分开提交）
7. 不对劲时按档位改 plan 或改 goal，并记 journal

## 产物在哪

工作发生在**你正在做的那个项目**里，不是 skills 仓库里：

```text
docs/helm/<initiative-id>/
  goal.md           # 要什么、怎样算成、阶段索引与状态（保持薄，状态唯一在这）
  journal.md        # 转向/弃坑/交接时追加（可懒创建）
  research.md       # 可选草稿笔记（决策记 journal，不记这）
  phases/
    01-<slug>.md    # 当前阶段怎么做（不含状态）
    02-<slug>.md
```

`<initiative-id>` 形如：`2026-07-19-password-strength`。

| 文件 | 写什么 | 别写什么 |
|------|--------|----------|
| `goal.md` | Intent、成功标准、Non-goals、阶段标题与**状态**、owner | 逐步实现细节 |
| `phases/NN-*.md` | 当前步骤、验收、何时该停 | 所有未来阶段的长 plan、状态字段 |
| `journal.md` | 为什么改了目标/路径、交接记录 | 日常流水账（可选） |

一次只维护**一个** active phase；后面的阶段在 goal 里留标题即可。

## git 提交

Helm 把 commit 挂在既有检查点上，别让已验收的工作悬在 working tree 里：

- **chunk 被验收后**：只提交这个 chunk 的实现和测试（隔离提交，不混入无关改动），再勾任务
- **phase 转换 / L1/L2/L3 转向 / 交接 / Close**：提交对应的 `goal.md`、phase 文件、`journal.md`
- 不提交未验收的半成品；提交信息写清 chunk 或转换，例如 `feat(login): password strength meter`、`docs(helm): P2 done`

## 开工前：对齐语言

开新项目或接手已有项目时，agent 会先看项目根有没有 `CONTEXT.md`（或 `CONTEXT-MAP.md`）：

- 有 → 用它的词汇写 goal，术语冲突先澄清再定目标
- 没有 → 首个术语定型时懒创建一个
- 新术语写回 `CONTEXT.md`，不塞进 goal.md（goal 继承项目的语言，不定义语言）

如果项目已有技术报告，先确定这次 initiative 的范围，再只看报告的简短概览、目录和相关章节；默认不把长报告全文塞进上下文。技术报告只用于快速定位当前系统，重要事实仍要回到代码和可执行配置核验。

## 技术报告联动

Helm 只负责**什么时候同步**，不负责技术报告**写什么**。项目已经存在技术报告（默认 `docs/technical-report.md`），或你明确要求启用时，每个已验证且被 Checkpoint 接受的 meaningful chunk 都交给独立 `technical-report` skill。首次启用但报告尚不存在时，第一个 handoff 走 `init` 建立完整当前态报告，之后走增量 `update`：

```text
实现 → 验证 → Helm 接受 chunk → technical-report 调查并同步 → 继续 phase
```

Helm 提供这一个 chunk 的准确范围、隔离后的 diff / changed paths、实际验证结果和 phase context，供专职 skill 定位实现。Helm 不预判是否有影响、不指定章节或结论，也不直接改报告。

`technical-report` 返回：

- `updated`：报告已按当前实现同步；
- `no-impact`：调查后确认报告无需改动，Helm 接受该判断；
- `blocked`：无法可靠同步；Helm 展示 blocker，不代写，也不完成该 chunk、phase 或 initiative，解决后重试。

技术报告只写项目**当前怎么实现、怎么运行**。改动过程、改动原因、用户 prompt、Helm phase/journal 和测试执行流水都不进入报告。

## 中途改方向

不必背术语，按感觉说就行：

| 你的情况 | 会怎么处理 |
|----------|------------|
| 步骤/库/顺序不对，目标还对 | **改当前 plan**（L1） |
| 这条 phase 路径失败了，大目标还对 | **换路径 / 作废旧 phase**（L2） |
| 成功标准或意图变了 | **停手 → 改 goal → 重切 phase**（L3） |

L2/L3 时 agent 应先用一句话说明档位，再改文件。  
改了文件才算改了方向——只改聊天记录不够。

## 多会话接着做

下次直接说：

```
继续 helm
接着 docs/helm 里 active 的那个
```

应 **resume** 已有 initiative，而不是默认新建一个。

> 并行/接力：goal.md 有 `owner` 字段，一个 initiative 同时只有一个 owner。
> 交接 = journal 记一条（结果 + 下一步）+ 改 `owner`。别和另一个 agent 同时改同一个 phase。
> 委托出去的 subagent 不是 owner：只读 goal.md/journal，只写自己的产物；状态变更留给 owner。

## 委托 subagent

默认在本会话执行。某一小块想交给 subagent 时，契约里写清：

- 读什么：`goal.md`、当前 phase、最近几条 journal、有则读 `CONTEXT.md`
- 写权限：goal/journal 只读；最终 task 勾选和所有状态变更留给 owner
- execution report 返回：候选改动范围、隔离后的 diff / 精确 changed paths、验证及实际结果、相关 phase context
- 普通执行 subagent 不判断技术报告影响、不调用 `technical-report`、不编辑技术报告
- 「完成」由主会话 Checkpoint 判定，不是 subagent 自己说了算；接受后再由 owner 发起技术报告 handoff

> 做只读调研（intake recon）时，用模板 `templates/intake-prompt.md`（同安装目录）组织委托契约：先 grep status 行再决定读哪些 goal.md、代码核验只限近期 phase 会碰到的模块；已有长技术报告时只看概览和相关章节。主会话把报告要点存进 `research.md` 供写 plan 复用。

## 什么时候别用

- 改一行、修个显而易见的小 bug  
- 纯 brainstorm、短期内不打算动手  
- 紧急 hotfix（流程成本高于风险时）

## 文件从哪来

skill 自带模板（安装目录下）：

- `templates/goal.md`
- `templates/phase.md`
- `templates/journal-entry.md`
- `templates/intake-prompt.md`（只读 Intake 调研委托提示词）

agent 协议全文见同目录 `SKILL.md`。
