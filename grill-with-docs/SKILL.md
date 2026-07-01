---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADRs and glossary) as we go. Combines grilling with domain-modeling.
install-targets: claude
source: Adapted from mattpocock/skills — https://github.com/mattpocock/skills
---

Run a `/grilling` session, using the `/domain-modeling` skill.

This means:

1. **First, `/domain-modeling`** — establish or review the project's domain language (CONTEXT.md) and create ADRs for key decisions as they emerge during discussion.

2. **Then/meanwhile, `/grilling`** — interview the user relentlessly about every aspect of their plan, resolving each branch of the design tree one question at a time.

Use **AskUserQuestion tool** for every question, one at a time, with 2-4 concrete multiple-choice options. If a question can be answered by exploring the codebase, explore it instead of asking.

When finished, provide a concise summary of all decisions made and what documentation was created/updated.
