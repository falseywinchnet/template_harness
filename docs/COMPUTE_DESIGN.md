# Compute-first algorithm design

Computational tractability is part of the mathematical design, not a cleanup
step after the formulas are fixed. Before implementing a serious search,
certificate, symbolic reduction, interval cover, simulation, or formal
generator, write the computation contract in `computations/COMPUTE_PLAN.md`.

## 1. Start from the checked proposition

Name the exact output predicate first. Then work backward:

- Which inputs are canonical and which are derived?
- Which values must be exact, directed, statistical, or merely diagnostic?
- What finite certificate would let a smaller independent verifier decide the
  predicate?
- What theorem connects that finite predicate to the scientific claim?
- What failure or undecided output is honest?

An algorithm without a statement bridge may be useful exploration, but it is
not theorem-bearing or result-bearing verification.

## 2. Complexity contract before code

Estimate and record:

- input dimensions, parameter ranges, and number of cases/cells;
- polynomial degrees, series order, matrix sizes, and expected term counts;
- coefficient domain and expected bit growth;
- asymptotic time and memory of the core operation;
- precision schedule and outward-rounding requirement;
- cacheable subproblems and invalidation keys;
- acceptable wall time, peak memory, output size, and checkpoint interval;
- completeness/termination argument for adaptive work;
- a smaller instance whose result can be checked independently.

If these are unknown, begin with an instrumented scale test, not the full run.
Log term counts, degrees, bit lengths, cells accepted/undecided, time per stage,
and peak memory. Stop when observed growth invalidates the design budget.

Every local scale test and material run uses `./h run` and must finish as a
bounded subtask within 240 seconds. The runner serializes material work, applies
lower scheduling priority and common numerical single-thread limits, and kills
the whole process group on timeout. See `docs/RESOURCE_SAFETY.md`. Memory-budget
requests are useful measurements but are not a dependable enforcement boundary.

## 3. Representation before optimization

The largest gains usually come from changing the mathematical representation.

- Expose symmetry, parity, translation, ordering, or block structure before
  enumeration.
- Factor forced zeros, collision powers, Vandermonde factors, denominators, and
  positive geometry before taking absolute values.
- Choose coordinates in which the core objects are polynomial, Laurent
  polynomial, affine, sparse, or monotone.
- Preserve common variables and correlations; replacing one shared quantity by
  independent intervals can destroy the cancellation that makes the theorem
  true.
- Use exact recurrences or coefficient dictionaries when only a bounded series
  order is needed. Do not construct the full multivariate expression and divide
  afterward.
- Split collision/near-boundary and separated regimes when one representation
  is ill-conditioned in both.
- Fixed small arity may deserve specialized code. Generalize only when it reduces
  total proof and compute cost rather than adding abstraction debt.

Dense symbolic expansion before forced-factor division is a known path to
expression swell. Blind subdivision is a known non-solution to dependency loss.

## 4. Cost ladder

Use progressively more expensive tools:

1. algebra and asymptotics on paper;
2. small exact examples and invariants;
3. floating/high-precision diagnostics for discovery;
4. structure-preserving symbolic prototype;
5. exact or directed certificate generator;
6. small independent verifier;
7. formal statement bridge where required;
8. full clean replay.

Do not run a global adaptive cover before proving the uncovered residue is
bounded. Do not spend precision to compensate for a poor coordinate system.
Do not infer a sign from a run that exhausted its budget or left undecided cells.

## 5. Sparse and structured arithmetic

Prefer data structures matched to the operations:

- sparse maps from exponent tuples to exact coefficients;
- univariate truncated series whose coefficients retain symbolic geometry;
- factored bases with memoized powers and common cofactors;
- block decompositions by error monomial or symmetry class;
- fraction-free elimination or domain-aware polynomial arithmetic;
- streaming cell/certificate records with incremental hashes;
- compact manifests that identify large regenerable outputs.

Remove zero coefficients immediately. Cache only pure, expensive functions with
content-derived keys. Record schema and code version with serialized caches.
Never use an opaque pickle as a public proof object; regenerate it or export a
canonical JSON/text certificate that the verifier can inspect.

## 6. Adaptive and interval algorithms

An interval covering algorithm is a proof only if:

- initial boxes cover the declared domain;
- every split covers its parent exactly;
- accepted boxes satisfy a directed predicate over the whole box;
- rejected/undecided boxes remain visible;
- the queue ends empty for a completion claim;
- the unbounded part is closed analytically;
- termination or a finite subdivision limit and failure status are declared;
- every accepted box and parameter is reproducible from the manifest.

If shrinking a box does not reduce dependency width, redesign the evaluator:
use shared Taylor models, multiple centers, divided differences, mean-value
forms, monotonicity, or a coordinate change. Subdivision that compensates for
lost correlation can grow forever even when the claim is true.

## 7. Precision strategy

Precision is part of the algorithm contract.

- Estimate the margin and conditioning before choosing precision.
- Use low precision for triage, then rerun accepted results at the declared
  directed precision.
- Escalate precision only when width comes from rounding; it does not cure model
  dependency or a false target.
- Record precision per stage, not only a global maximum.
- Require strict certified separation from zero for strict-sign conclusions.
- Cross-check near-zero diagnostics with a different representation or
  implementation before investing in a certificate.

## 8. Parallelism and determinism

Parallelize only independent units such as cells, parameter cases, or Monte
Carlo replicates. Keep deterministic ordering for work assignment, reduction,
and output. Use stable seeds and record them. Reduction of exact objects must be
order-independent or use a canonical order.

Do not parallelize Lean builds by default. Do not launch multiple memory-bound
symbolic expansions simply because cores are idle. Measure total throughput and
peak memory first.

Local template operation is serial by default. Worker pools and background jobs
are prohibited for material work because invisible or surviving descendants can
overlap a later run. Evaluate parallel implementations only in a separately
isolated environment after measuring the serial baseline and total—not per
worker—memory. A returned execution session/cell identifier is an active job,
not permission to start another.

## 9. Generator/verifier split

The generator may use heuristics, search, caching, high precision, and expensive
algebra. The verifier should be smaller and more boring:

- canonical inputs;
- explicit domain and statement;
- no trust in labels like `positive=true`;
- reconstruction of identities or inequalities;
- deterministic failure on missing or malformed records;
- exact or directed arithmetic appropriate to the claim;
- no network access or hidden mutable state;
- bounded resource behavior where practical.

Validate optimized generators against an older direct implementation on small
exact rational cases. Such randomized or sampled equality checks are regression
tests for implementation equivalence, not proof of the global claim.

## 10. Performance records

For each material run, record:

- command, commit, environment, seed, and input digest;
- cold/warm cache state;
- wall/user/system time and peak resident memory;
- stage timings and term/cell counts;
- precision and arithmetic backend;
- output/certificate digest;
- accepted, rejected, undecided, and failed counts;
- whether the run is discovery, quick audit, full replay, or release gate.

Keep a benchmark small enough for routine regression and a full-scale benchmark
for release. A faster implementation is adopted only after exact equivalence or
the new soundness argument is recorded.

## 11. Stop and pivot conditions

Stop a computation rather than promoting it when:

- term or memory growth exceeds the predeclared envelope;
- an adaptive tree has no termination/completeness argument;
- more precision does not shrink the decisive enclosure;
- subdivision is masking correlation loss;
- the unbounded domain has not been reduced analytically;
- the algorithm checks a nearby object instead of the target object;
- the only positive margin comes from a supplied assumption;
- output cannot be independently verified.

An implementation failure is not a counterexample. An unfinished calculation is
not evidence. Preserve both with the reason for the pivot.
