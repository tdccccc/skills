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

把 `helm` 链到 ZCode 会扫描的目录，例如：

```bash
mkdir -p ~/.zcode/skills ~/.agents/skills
ln -sfn /path/to/skills/helm ~/.zcode/skills/helm
ln -sfn /path/to/skills/helm ~/.agents/skills/helm
```

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
4. 按步骤执行（默认本会话；需要时再委托 tocodex）  
5. 不对劲时按档位改 plan 或改 goal，并记 journal  

## 产物在哪

工作发生在**你正在做的那个项目**里，不是 skills 仓库里：

```text
docs/helm/<initiative-id>/
  goal.md           # 要什么、怎样算成、阶段索引（保持薄）
  journal.md        # 转向/弃坑时追加（可懒创建）
  research.md       # 可选草稿笔记
  phases/
    01-<slug>.md    # 当前阶段怎么做
    02-<slug>.md
```

`<initiative-id>` 形如：`2026-07-19-password-strength`。

| 文件 | 写什么 | 别写什么 |
|------|--------|----------|
| `goal.md` | Intent、成功标准、Non-goals、阶段**标题** | 逐步实现细节 |
| `phases/NN-*.md` | 当前步骤、验收、何时该停 | 所有未来阶段的长 plan |
| `journal.md` | 为什么改了目标/路径 | 日常流水账（可选） |

一次只维护**一个** active phase；后面的阶段在 goal 里留标题即可。

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

## 可选：和 tocodex 一起用

默认在本会话执行。某一小块想交给 Codex 时再说「这一步用 tocodex」。

- 执行产物仍在 `docs/tocodex/<task-id>/`
- task 的 Context 里应链上本次 `goal.md` 和当前 phase
- 报告回来后先对照 goal/phase，再决定是否转向

## 什么时候别用

- 改一行、修个显而易见的小 bug  
- 纯 brainstorm、短期内不打算动手  
- 紧急 hotfix（流程成本高于风险时）

## 文件从哪来

skill 自带模板（安装目录下）：

- `templates/goal.md`
- `templates/phase.md`
- `templates/journal-entry.md`

agent 协议全文见同目录 `SKILL.md`。
