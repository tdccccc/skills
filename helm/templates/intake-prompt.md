# Intake recon — read-only delegation prompt (template)

Copy this into a delegation contract when the main session needs ground truth for a new or resumed
initiative without reading the whole repo itself. The main session is the helm owner; this delegate
is read-only research, never an owner. Main session dumps the returned report into `research.md`
for reuse when planning.

Fill the three placeholders, keep or drop the optional section, and ship the rest as-is.

---

Read-only recon for a helm intake. **Do not modify or create any files** (no file writes, no git
write commands, no installs) — report only.

Repository: `<repo path>`
Initiative: `<one-line intent, e.g. "per-article summary checkpoints with interruption recovery">`
Context: `<optional — constraints, non-goals, or terms the user already gave>`

Report back concisely (≤ ~20 lines), structured:

1. **Verdict — resume or new.** Run `grep -H "^status:" docs/helm/*/goal.md` first (if the dir
   exists); do not read every goal.md to check. Full-read only candidates with `status: active` or
   a still-open `proposed`. For each candidate: initiative-id, owner, status, current active phase,
   and one line on match or no-match with the initiative above. If nothing matches, say so plainly.
2. **Vocabulary.** Read the repo root `CONTEXT.md` / `CONTEXT-MAP.md` (if present) and list the
   domain terms the initiative must use — plus any term that conflicts with how the initiative was
   described above.
3. **Doc format.** Which existing goal.md (and phase file, if useful) is the closest writing-format
   reference, and its shape (sections, project-specific conventions). Read the candidate(s) only —
   this is about format, not content.
4. **Code anchors (scoped).** Only for the parts this initiative will plausibly touch: entry
   points, state/storage locations, existing tests/abstractions. Give `file:line` for a handful of
   anchor points; `file:section` is enough elsewhere. If the phase boundary is not settled yet,
   state what you verified and what you left unverified — do not sweep the whole repo.
5. **Unknowns.** Anything you could not verify quickly, or that looks inconsistent with the user's
   description.

Rules: prefer `grep`/`ls`/status lines over full-file reads; file:line only where it matters; a
report with honest gaps beats a padded one — never invent file references.

---

Optional add-ons, when the main session needs them:
- *Suggested phase boundaries:* rough candidate phase splits aligned to the code anchors above
  (outcomes only — details stay in the phase plan).
- *Existing tests to run:* test entry points relevant to the anchors (names/commands only, don't run them).
