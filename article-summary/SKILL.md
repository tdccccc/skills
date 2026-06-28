---
name: article-summary
description: 总结天文/学术论文为中文结构化笔记。当用户提供 arXiv 链接或 ID、论文 PDF、LaTeX/文本文件、DOI 或期刊/ADS 链接，并希望得到结构化中文总结（TL;DR、方法、结果、公式与图表解读、局限）时使用。Summarize astronomy/academic papers into structured Chinese notes.
install-targets: claude
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
