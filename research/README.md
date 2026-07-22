# Research control plane

These files keep the public scientific target separate from exploratory work.

- `TARGET.md` freezes the exact question, claim surface, and non-goals.
- `DEPENDENCIES.md` expands each target claim into immediate prerequisites.
- `CLAIM_INDEX.md` is the status/evidence crosswalk.
- `EVIDENCE_LEDGER.md` identifies preserved sources, datasets, replays, and
  formal boundaries.
- `TRUSTED_BASE.md` names assumptions and systems outside the checked boundary.
- `NON_VACUITY.md` audits whether implications apply to actual target objects.
- `FORMALIZATION.md` scopes optional formal or certified work.
- `claims/CLAIM_TEMPLATE.md` is copied for claims needing a full audit record.

IDs are project-local and stable. A recommended convention is `C001` for claims,
`E001` for evidence boundaries, and `O001` for unresolved obligations. Do not
reuse an ID after a claim is dropped or superseded.

Lean projects follow `docs/LEAN_CLAIM_STANDARD.md`. `KERNEL_CHECKED` records a
tool fact; only the complete target-object, objective-interior, instantiation,
falsification, and independent statement-fidelity chain earns
`FORMALLY_PROVED`.
