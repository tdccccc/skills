# Helm user-facing README

status: done
updated: 2026-07-19

## Intent

Give helm a short user-facing README so a person can install and run the skill without reading SKILL.md.

## Success criteria

- [x] `helm/README.md` exists and explains install, basic usage, artifacts, and mid-flight course correction
- [x] A new user can start an initiative from the README examples alone
- [x] Root package layout lists `helm/README.md`

## Non-goals

- Duplicating the full agent protocol from SKILL.md
- English/Chinese dual README pair (one clear doc is enough for now)
- Changing helm workflow behavior

## Constraints

- Keep the README scannable (roughly one screen of core path + short reference)
- Match tone/structure of sibling skill READMEs (tocodex-style practicality)
- Do not invent paths or status values that disagree with SKILL.md

## Phases

1. P1 — ship user-facing `helm/README.md` and wire it in package layout — status: done

## Current focus

(none — done)
