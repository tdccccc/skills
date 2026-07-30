# P1 — write-readme

goal_ref: ../goal.md
status: done

## Outcome

`helm/README.md` is written for humans, and the root README layout mentions it.

## Assumptions

- Readers already use Claude Code or ZCode and can install a local skill.
- They care about “what to say” and “what files appear,” not agent internals.

## Approach

Write a practical README: what/why → install (Claude + ZCode) → how to talk to the agent → artifacts → steer in plain language → when not to use → optional tocodex. Then add the file to the package layout list.

## Tasks

- [x] Draft `helm/README.md` (user-facing)
- [x] Update root `README.md` layout to include `helm/README.md`
- [x] Sanity-check paths and status names against SKILL.md

## Verification

- `helm/README.md` is present and readable end-to-end
- Root layout block lists the README
- No contradiction with `docs/helm/...` or tocodex paths in SKILL.md

## Abort / reshape triggers

- If the README starts becoming a second SKILL.md, cut ruthlessly (L1/L2).
- If install paths for ZCode are wrong for this machine’s conventions, stop and fix facts before shipping.
