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

For a universal formal claim, put it in falsification normal form:

- `Admissible(x)`: independently defined target-domain conditions;
- `Conclusion(x)`: the exact claimed predicate;
- `Counterexample(x) := Admissible(x) ∧ ¬ Conclusion(x)`;
- exact Lean declarations proving that the exported target excludes precisely
  these counterexamples.

For `f x > 0`, equality is part of the counterexample condition. “No outward
seam,” failure to find a sample, or closure of a proposed target region is not a
falsification boundary for source-object containment.

## Objective target interior

Give at least one raw, independently constructed object in the target domain and
prove the actual conclusion for that same object. Name the strict margin or
nondegeneracy fact preventing a boundary/equality-only witness. Do not use a
subtype, structure field, or hypothesis that already stores the conclusion.

- Raw witness:
- Admissibility proof:
- Result/interior proof:
- Strictness or nondegeneracy source:
- Lean declarations or evidence:

This witness establishes contact with the intended phenomenon, not universal
coverage. If topological interior or robustness is claimed, record and prove an
explicit neighborhood/radius separately.

## Initialization and containment

If the claim says that one object, algorithm, model, or class lies inside
another, state separately:

- source predicate and independently defined source object;
- semantic encoding/object-identity theorem;
- initialization or direct membership theorem `A x → B (encode x)`;
- preservation theorem, if a transition system is involved;
- reachability theorem connecting generated states to initialization;
- final containment theorem.

Closure or preservation alone does not establish initial membership.

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
