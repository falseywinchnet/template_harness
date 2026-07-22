# Target contract

Target version: `TARGET-v1`

Status: draft until bootstrap acceptance

## Object or population

Define the exact mathematical object, physical system, dataset population, or
experimental domain. Record representations and prove or test equivalence when
multiple forms are used.

## Primary claim

State the main claim with all quantifiers, domains, conditions, estimands, and
units. Avoid motivational paraphrase here.

## Falsification condition

State a concrete observation, counterexample, interval, test outcome, or theorem
failure that contradicts or materially weakens the primary claim.

## Secondary claims

List only claims needed for the deliverable. Give each a stable claim ID.

## Non-goals

- conclusions outside the specified domain;
- causal claims not identified by the design;
- stronger generalizations not supported by the evidence;
- toolchain or hardware verification unless explicitly included.

## Statement-fidelity gate

For every exported result, compare the checked statement to this contract in
both directions. Stronger assumptions, fewer cases, a different object, a weak
inequality, or a changed estimand does not satisfy the target merely because a
tool accepted it.
