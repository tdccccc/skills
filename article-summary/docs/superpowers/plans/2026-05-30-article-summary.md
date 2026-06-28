# article-summary Skill 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个纯指令型 Claude Code skill，把天文/学术论文（arXiv/PDF/LaTeX/DOI）转成中文结构化总结，默认展示、按需存档。

**Architecture:** 纯指令型 skill：一个 `SKILL.md`（触发描述 + 工作流 + 精简模板）加一个 `references/summary-template.md`（完整模板）。只用原生工具 WebFetch / Read / Bash(curl) / Write / WebSearch，零外部依赖。验证靠行为测试（真实论文端到端跑通），非单元测试。

**Tech Stack:** Markdown + YAML frontmatter；Claude Code 原生工具。

> 说明：这是指令/文档类产物，没有可写的单元测试。每个"验证"步骤是**行为检查**或对文件内容的轻量结构检查，给出明确的预期结果。
> 路径约定：Task 1 把目录重命名为 `article-summary`，**其后所有路径都基于** `/home/tiandc/Documents/code/skills/article-summary/`。
> 提交约定：本环境有全局 commit-msg 钩子，**所有提交必须用 Conventional Commits**（`type(scope): subject`）。

---

### Task 1: 把目录重命名为 `article-summary`

**Files:**
- Rename: `/home/tiandc/Documents/code/skills/article_summary/` → `/home/tiandc/Documents/code/skills/article-summary/`

skill `name` 用连字符 `article-summary`，目录名需保持一致。git 跟踪的是内容不是目录名，重命名顶层目录不产生 diff，无需提交。

- [ ] **Step 1: 从父目录原子地重命名并切入新目录**

Run:
```bash
cd /home/tiandc/Documents/code/skills && mv article_summary article-summary && cd article-summary && pwd && git status --short
```
Expected: 打印 `/home/tiandc/Documents/code/skills/article-summary`，且 `git status` 干净（无未跟踪/改动，因为只是改了顶层目录名）。

- [ ] **Step 2: 确认 git 仓库仍可用**

Run:
```bash
git -C /home/tiandc/Documents/code/skills/article-summary log --oneline -1
```
Expected: 显示上一条 `docs(article-summary): add design spec for the skill` 提交。

> 若后续命令报"目录不存在"，说明 shell 仍指向旧路径——执行 `cd /home/tiandc/Documents/code/skills/article-summary` 重新锚定即可。

---

### Task 2: 创建完整输出模板 `references/summary-template.md`

**Files:**
- Create: `/home/tiandc/Documents/code/skills/article-summary/references/summary-template.md`

- [ ] **Step 1: 写模板文件**

写入以下完整内容：

````markdown
# 论文总结输出模板

每份总结严格按本结构输出。`<...>` 为填写指引，实际输出请替换。无法从论文获取的字段，写「论文未涉及」而非编造。

```markdown
# <论文标题（原文，可在括号内附中文译名）>
**<第一作者 et al.> · <年份> · <期刊名 或 arXiv:ID>**

## TL;DR
<一到两句话：这篇论文做了什么 + 最重要的发现/结论。让读者据此判断要不要精读。>

## 结构化拆解
- **背景与动机**：<研究要解决的科学问题、为什么重要>
- **观测 / 方法**：<用了什么望远镜/巡天/数值方法/数据处理流程>
- **数据样本**：<样本量、波段、红移范围、数据来源等关键参数>
- **主要结果**：<最重要的 2-4 条定量结果，带关键数值>
- **科学意义**：<结果对该领域意味着什么>

## 公式与图表解读
- **关键公式**：<列出核心公式，逐一解释各物理量含义；无核心公式则写「无关键公式」>
- **主要图表**：<挑 1-3 张最重要的图，说明每张图展示了什么、支持了什么结论>

## 局限 · 未来 · 相关工作
- **局限**：<作者承认的或明显的局限性、系统误差、样本偏差>
- **未来工作**：<作者提出的后续方向>
- **相关文献**：<与本文紧密相关、值得一并了解的工作>
```

## 语言规则
- 正文用中文。
- 以下保留英文：专业术语（redshift、metallicity、star formation rate）、天体名（M31、NGC 1068、Sgr A*）、巡天/仪器（JWST、SDSS、ALMA、Gaia）、物理量与单位（M⊙、kpc、erg/s）、作者名。
- 关键术语首次出现可加中文注，如「光度函数 (luminosity function)」。

## 仅有摘要时
- 在标题下方加一行 `⚠️ 仅基于摘要，正文未获取`。
- 能从摘要填的块照填，其余写「摘要未涉及」。
````

- [ ] **Step 2: 验证文件结构**

Run:
```bash
grep -E '^## (结构化拆解|公式与图表解读|局限)' /home/tiandc/Documents/code/skills/article-summary/references/summary-template.md
```
Expected: 三行标题都打印出来，确认四块结构齐全（TL;DR 在代码块内不计）。

- [ ] **Step 3: 提交**

Run:
```bash
cd /home/tiandc/Documents/code/skills/article-summary && git add references/summary-template.md && git commit -m "feat(article-summary): add full summary output template"
```
Expected: 提交成功（Conventional Commits 通过钩子）。

---

### Task 3: 创建 `SKILL.md`

**Files:**
- Create: `/home/tiandc/Documents/code/skills/article-summary/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**

写入以下完整内容：

````markdown
---
name: article-summary
description: 总结天文/学术论文为中文结构化笔记。当用户提供 arXiv 链接或 ID、论文 PDF、LaTeX/文本文件、DOI 或期刊/ADS 链接，并希望得到结构化中文总结（TL;DR、方法、结果、公式与图表解读、局限）时使用。Summarize astronomy/academic papers into structured Chinese notes.
---

# 天文/学术论文总结

## 何时使用
当用户提供论文来源——arXiv ID/链接、本地 PDF、本地 LaTeX/文本、DOI/期刊/ADS 链接——并希望得到中文结构化总结时。

## 工作流
1. 识别输入类型（arXiv / 本地 PDF / 本地 LaTeX-文本 / DOI-期刊-ADS）。
2. 按下面对应方式获取论文内容。
3. 按「输出模板」生成中文总结（术语保留英文）。完整模板见 `references/summary-template.md`。
4. 在对话中展示完整总结。
5. **仅当**用户要求保存（说"存一下/保存"或给出路径）时，才用 Write 写文件。默认不落盘。

## 获取论文内容

### arXiv ID 或链接
- 从输入规范化出 arXiv ID（如从 `arxiv.org/abs/2401.12345`、`arxiv.org/pdf/2401.12345v2` 提取 `2401.12345`）。
- 优先用 WebFetch 抓全文 HTML：`https://ar5iv.labs.arxiv.org/html/<id>`（含正文、公式、图注，最适合总结）。
- 若 ar5iv 无此论文或抓取失败：用 Bash 下载 PDF 到 /tmp，再用 Read 读取：
  ```bash
  curl -sL "https://arxiv.org/pdf/<id>" -o /tmp/<id>.pdf
  ```
  然后 Read `/tmp/<id>.pdf`。

### 本地 PDF
- 直接用 Read 读取。
- 论文较长（>20 页）时用 Read 的 `pages` 参数分批读：先读摘要+引言，再读方法、结果、结论所在页。

### 本地 LaTeX / 文本
- 直接用 Read 读取，公式与章节结构原样保留。

### DOI / 期刊 / ADS
- 用 WebFetch 抓落地页，提取标题、作者、年份、摘要。
- 若正文被付费墙挡住：用 WebSearch 或在 arxiv.org 按论文标题搜预印本；找到 arXiv 版后改走「arXiv」流程拿全文。
- 若始终拿不到全文：仅基于摘要总结，并在标题下方标注 `⚠️ 仅基于摘要，正文未获取`。

## 输出模板（精简）
完整版（含每字段填写指引）见 `references/summary-template.md`。结构：

```markdown
# <论文标题>
**<作者> · <年份> · <期刊/arXiv:ID>**

## TL;DR
<一两句话：做了什么 + 最重要的发现>

## 结构化拆解
- **背景与动机**：…
- **观测 / 方法**：…
- **数据样本**：…
- **主要结果**：…
- **科学意义**：…

## 公式与图表解读
- **关键公式**：<公式> — 各物理量含义
- **主要图表**：Fig X 表明…

## 局限 · 未来 · 相关工作
- **局限**：…
- **未来工作**：…
- **相关文献**：…
```

## 语言规则
- 正文用中文。
- 保留英文：专业术语（redshift、metallicity）、天体名（M31、NGC 1068）、巡天/仪器（JWST、SDSS、ALMA）、物理量与单位、作者名。
- 关键术语首次出现可加中文注，如「光度函数 (luminosity function)」。

## 存档
- 默认只在对话中展示，不写文件。
- 用户要求保存时：写入 `summaries/<arxiv-id 或标题缩写>.md`（默认当前目录的 summaries/ 子目录；用户给了路径就用其路径）。文件名去掉空格与特殊字符。

## 诚实原则
- 内容拿不到就如实说，**绝不编造**数据、结论或图表含义。
- 仅有摘要时明确标注，无法填写的块写「摘要未涉及」。
- PDF 是扫描件/乱码时，提示用户改用 arXiv ID 或文本版。
````

- [ ] **Step 2: 验证 frontmatter 与目录名一致**

Run:
```bash
cd /home/tiandc/Documents/code/skills/article-summary && grep -E '^name: article-summary$' SKILL.md && [ "$(basename "$PWD")" = "article-summary" ] && echo "NAME_OK"
```
Expected: 打印 `name: article-summary` 那一行，然后 `NAME_OK`。

- [ ] **Step 3: 验证 description 含关键触发词**

Run:
```bash
grep -E '^description:' /home/tiandc/Documents/code/skills/article-summary/SKILL.md | grep -oE 'arXiv|PDF|论文|总结' | sort -u
```
Expected: 至少打印出 `arXiv`、`PDF`、`总结`、`论文` 这几个触发词。

- [ ] **Step 4: 提交**

Run:
```bash
cd /home/tiandc/Documents/code/skills/article-summary && git add SKILL.md && git commit -m "feat(article-summary): add SKILL.md with workflow and template"
```
Expected: 提交成功。

---

### Task 4: 行为验证（真实论文端到端）

**Files:** 无（这是运行验证，不改文件）

这是本 skill 的"测试"：用真实论文跑一遍，检查 skill 能否被正确触发并产出合规总结。

- [ ] **Step 1: 选一个真实 astro-ph 论文**

Run:
```bash
curl -sL "https://arxiv.org/list/astro-ph/recent" -o /tmp/astro_recent.html && grep -oE 'arXiv:[0-9]{4}\.[0-9]{4,5}' /tmp/astro_recent.html | head -1
```
Expected: 打印一个近期 astro-ph 的 arXiv ID。若取不到，用已知存在的回退 ID `1502.01589`（Planck 2015 宇宙学参数）。

- [ ] **Step 2: 按 SKILL.md 工作流总结该论文**

按 SKILL.md 流程处理上一步的 arXiv ID：WebFetch 抓 ar5iv 全文（失败则下载 PDF 再 Read），按模板生成中文总结并在对话中展示。

- [ ] **Step 3: 对照检查清单验证输出**

逐项确认（行为检查，预期全部满足）：
- [ ] 有 `# 标题` 与 `**作者 · 年份 · arXiv:ID**` 行
- [ ] 四块齐全：`TL;DR`、`结构化拆解`、`公式与图表解读`、`局限 · 未来 · 相关工作`
- [ ] 正文中文，术语/天体名/仪器名保留英文
- [ ] 数值/结论来自论文，无编造（与 ar5iv/PDF 内容可对上）
- [ ] 未主动写文件（默认只展示）

- [ ] **Step 4: 验证"仅摘要"路径**

模拟拿不到全文的情形：仅用 WebFetch 抓 `https://arxiv.org/abs/<id>`（只有摘要），按工作流总结。
Expected: 标题下出现 `⚠️ 仅基于摘要，正文未获取`，无法填写的块写「摘要未涉及」。

- [ ] **Step 5: 验证按需存档**

明确要求"把刚才的总结存一下"。
Expected: 在 `summaries/<id>.md` 生成文件；文件名无空格/特殊字符。
Run:
```bash
ls /home/tiandc/Documents/code/skills/article-summary/summaries/
```
Expected: 列出刚生成的 `.md` 文件。

> 说明：summaries/ 是运行产物，加入 `.gitignore`，不提交（见 Task 5）。

---

### Task 5: 让 skill 可被发现 + 收尾

**Files:**
- Create: `/home/tiandc/Documents/code/skills/article-summary/.gitignore`
- Symlink（可选，需与用户确认）：`~/.claude/skills/article-summary` → 本目录

- [ ] **Step 1: 写 .gitignore（排除运行产物）**

写入 `/home/tiandc/Documents/code/skills/article-summary/.gitignore`：
```
summaries/
*.pdf
```

- [ ] **Step 2: 安装到 Claude Code skills 目录（先与用户确认）**

Claude Code 从 `~/.claude/skills/` 加载个人 skill。确认用户希望以软链接方式安装后：
```bash
ln -s /home/tiandc/Documents/code/skills/article-summary ~/.claude/skills/article-summary && ls -l ~/.claude/skills/article-summary
```
Expected: 软链接创建成功，指向开发目录。
> 若用户用别的方式管理（如已整体软链 `~/Documents/code/skills`，或作为 plugin），跳过本步并按其方式安装。

- [ ] **Step 3: 提交收尾文件**

Run:
```bash
cd /home/tiandc/Documents/code/skills/article-summary && git add .gitignore SKILL.md references/ docs/ && git commit -m "chore(article-summary): add gitignore for runtime artifacts"
```
Expected: 提交成功（若 SKILL.md/references 已在前面提交则只提交 .gitignore 与计划文档）。

- [ ] **Step 4: 终检**

Run:
```bash
cd /home/tiandc/Documents/code/skills/article-summary && ls -R . && git log --oneline
```
Expected: 看到 `SKILL.md`、`references/summary-template.md`、`.gitignore`、`docs/superpowers/`，以及一串 Conventional Commits 历史。

---

## 自检（写计划后回看 spec）

- **Spec 覆盖**：定位(Task3)、四类输入(Task3)、四块模板(Task2/3)、语言规则(Task2/3)、按需存档(Task3/4)、错误处理(Task3/4)、验证(Task4)、重命名(Task1) —— 均有对应任务。✓
- **占位符**：SKILL.md 与模板里的 `<...>` 是给最终输出的填写指引，非计划空缺；其余步骤均有具体命令与预期。✓
- **一致性**：全程 skill 名 `article-summary`、目录 `article-summary`、模板四块字段在 Task2/3/4 中一致。✓
