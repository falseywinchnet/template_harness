# Context and model-compute economy

This control limits repeated orientation cost without pretending that a smooth
summary preserves scientific judgment. It separates curated retrieval cues,
manual working state, and full documentation.

## 1. Progressive disclosure contract

`./mind how TOPIC` returns a hot card of at most 900 bytes. The card anticipates
the first operational questions: where to start, which distinction controls the
decision, which recurrent failure to avoid, which command to run, and when to
stop. Its order follows expected usefulness rather than document order.

`./mind how TOPIC more` returns one warm card of at most 2,400 bytes and a
`FULL` line naming authoritative cold documents. There is one `more` tier. Read
the full document only when the warm card leaves a material question unresolved
or the active task requires comprehensive audit.

Cards are maintained judgments. They are not generated abstracts, tables of
contents, or substitutes for normative documents. Add a cue after a repeated
mistake or expensive lookup; remove a cue that no longer changes behavior. Run
`./mind audit` after editing the index.

## 2. Reading policy

At session start, run `./h`. Query one relevant hot card before opening a broad
guide. Stop at the first tier that resolves the current decision. A card's
`FULL` paths are the only promised continuation; a model must not recursively
request broader summaries.

The cold documents remain complete and may overlap. The hot and warm tiers
should not mirror that completeness. They preserve high-frequency decisions,
hard boundaries, likely worries, failure pivots, and exact next commands.

## 3. Manual handoff contract

`./h context save` writes `.harness/context.json` atomically. `STATE` and `NEXT`
are required; the complete handoff is capped at 2,200 characters. Its fields are:

- `STATE`: established facts and decisions, without chronology;
- `NEXT`: one smallest exact continuation;
- `WHY`: intent, invariant, or decision reason that must survive;
- `FILES`: authoritative paths, symbols, claim IDs, or locations;
- `RISKS`: unresolved questions, live counterevidence, and forbidden assumptions;
- `VERIFY`: last checks and the exact evidence boundary they earned.

When a round is open, saving a handoff also records `STATE` and `NEXT` as the
round checkpoint. The handoff captures the register digest, active round, Git
revision, and worktree fingerprint. `./h context` marks it stale when those
observable state boundaries change. A fresh marker establishes consistency with
those boundaries; it does not certify that the author's judgment was complete.

Use shorthand. Preserve exact identifiers and errors. Keep disagreements and
unknowns jagged. Do not store secrets. Do not spend the reserved context
explaining the transcript.

## 4. Compaction protocol

For Codex CLI, `/status` and the `context-remaining` status-line item expose the
remaining capacity. Current command-hook inputs do not expose a documented token
count, so the repository does not fabricate a meter from transcript bytes. In
other clients, use any visible product meter; otherwise checkpoint before a
large phase or output rather than waiting for an inferred threshold.

The default action point is 30% remaining context. Before a deliberate
`/compact`, stop other work and run:

```sh
./h context save \
  --state "established facts and decisions" \
  --next "one exact action" \
  --why "intent or invariant" \
  --files "authoritative paths and IDs" \
  --risks "unknowns and forbidden assumptions" \
  --verify "last checks and their boundary"
```

After compaction, run `./h context` before any other read or command. Treat the
automatic transcript distillation as provisional where it conflicts with the
manual handoff or durable project state.

## 5. Codex integration and limits

`.codex/config.toml` supplies an intent-driven compaction prompt. The prompt
prioritizes the manual handoff, exact next action, evidence, failures, paths,
uncommitted edits, and unresolved risks while discarding tool chatter.

`.codex/hooks.json` configures three lifecycle checks:

- `PreCompact` verifies freshness and surfaces a warning; the preceding
  `./h context save` output places the exact handoff in the transcript for the
  compact prompt;
- manual compaction with a stale handoff is stopped and requests a save;
- automatic compaction with a stale handoff continues to avoid a hard-limit
  failure, then `PostCompact` requests recovery from durable state;
- `SessionStart` on resume or compact injects the durable handoff as model
  context and requests the same re-entry read.

Command hooks cannot ask a model to author a judgment before automatic
compaction. Codex currently runs command handlers; prompt and agent hook handlers
are skipped. `PreCompact` warning text is UI output rather than model context;
the model-visible re-entry occurs through `SessionStart`. The custom compact
prompt is therefore a fallback, not a manual handoff. Review and trust project
hooks with `/hooks`; untrusted project hooks are skipped.

`model_auto_compact_token_limit` is intentionally unset. It is an absolute
model-specific number. During bootstrap, record the verified context window,
desired reserve, expected output risk, and acceptable round cost; then configure
an absolute threshold only for that project and provider. A useful starting
policy is to reserve 25–30% of the verified window, followed by measurement and
revision.

## 6. Cost discipline

Before opening a round, state its bounded question and stopping condition. Use
the cheapest evidence class capable of deciding the next gate. Move read-heavy
exploration or long logs out of the main context only when delegation or an
artifact genuinely lowers total model tokens; parallel agents multiply model
cost and are not a default economy measure.

Record expected round time, model cost, context reserve, and any provider limit
in `PROJECT.md`. A round that reaches its cost or context boundary closes or
checkpoints with a smaller continuation. It does not continue merely because
unused scientific tasks remain.

## 7. Compatibility and product references

The checked-in integration was validated with `codex-cli 0.142.5`. The durable
commands and files remain usable when another client lacks these hooks; only the
automatic warnings, manual-compaction stop, and re-entry injection are absent.
Recheck the hook schema after a client upgrade that rejects the configuration.

- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Codex slash commands](https://learn.chatgpt.com/docs/reference/slash-commands)
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [OpenAI Codex compact-hook implementation](https://github.com/openai/codex/blob/main/codex-rs/hooks/src/events/compact.rs)
