# Claude Codex Runner

[English](README.md)

在 Claude Code 中把任务交给 Codex CLI 执行，然后总结结果。

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
```

## 使用

一句话就能用：

```
你：搜一下今天 arxiv 上 astro-ph.CO 更新了多少篇文章
你：把这个函数改成异步版本
你：给登录页面加一个密码强度指示器
```

Claude 会自动：
1. 判断任务复杂度，生成合适的 task.md
2. 通过 Agent 在后台调用 `codex exec`
3. 完成后读取报告并总结

查看进度：在 Claude Code 界面按 **↓ 方向键**查看 Agent 实时输出。

## 任务复杂度判断

| 简单（极简模板） | 复杂（完整模板） |
|---|---|
| 只读/搜索/画图 | 多文件改动 |
| 单文件 ≤ 50 行 | 单文件 > 50 行 |
| 不涉及测试/配置/依赖/安全 | 涉及测试/配置/依赖/安全 |
| 一次性脚本 | 需要验证步骤 |

## 任务文件结构

```
<project>/
  docs/
    tasks/
      YYYY-MM-DD-slug/
        task.md
        codex-report.md
  .codex-runs/
    YYYY-MM-DD-slug/
      stdout.log
      stderr.log
```
