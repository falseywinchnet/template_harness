# RXXXX — short round name

- Mode: `advance` or `refine`
- Status: open, closed, or interrupted
- Started: ISO-8601 UTC
- Project items: `P...`
- Starting claims/evidence: IDs or exact paths
- Question: one bounded question
- Acceptance: observable stopping condition
- Model boundary: expected time/cost and context reserve from `PROJECT.md`

## Boundary

State what this round may change and what is explicitly out of scope.

For a formal-proof round, name the exact declaration-chain link being worked:
object identity, domain/interior witness, instantiation, initialization,
preservation, target, counterexample equivalence, or audit. Do not use “prove
the theorem” as a round boundary when several of these remain open.

## Starting state

Name the smallest sufficient inputs. Do not restate the whole project.

## Work log

Use `./h note` for recovery checkpoints. Preserve calculations and attempts in
this directory. Before the context reserve or deliberate compaction, write the
bounded manual handoff with `./h context save`.

## Close

Record result, evidence boundary, failures, claim-status changes, and the exact
next item. Completion of the round does not imply completion of every item.
