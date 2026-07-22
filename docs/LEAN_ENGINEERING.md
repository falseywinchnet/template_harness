# Lean engineering requirements

This guide governs any project that selects Lean as a trust boundary. It is
specific enough to prevent the failure modes encountered in a large analysis
formalization, but theorem-independent. `research/TARGET.md` remains the source
of mathematical truth; Lean is required to implement that target, not redefine
it into something easier.

## 1. Entry conditions

Do not begin a large formalization from manuscript prose alone. Before adding
theorem-bearing code, freeze:

1. the exact target statement, quantifier order, domains, and conclusion;
2. definitions of the public objects and every alternative representation;
3. target-reachable dependencies and imported results;
4. non-vacuity, denominator, endpoint, convergence, and strictness obligations;
5. the allowed axioms and external certificate boundary;
6. a first module graph and expected rebuild direction.

Complete `research/FORMALIZATION.md`. Formalize the target skeleton early, even
while its proof remains open, so later work cannot silently drift to a stronger
hypothesis, smaller domain, different object, or weaker conclusion.

## 2. Pinned environment

Pin all three moving components:

- `lean-toolchain`: exact Lean release or commit;
- `lakefile.toml`: exact mathlib tag or commit;
- `lake-manifest.json`: resolved dependency graph for a release.

After changing Lean or mathlib, obtain the matching binary cache before building:

```sh
./h run --cwd formal --label lean-update -- lake update
./h run --cwd formal --label lean-cache -- lake exe cache get
```

Do not rebuild mathlib from source accidentally. Record the Lean, Lake, mathlib,
platform, and cache state in `paper/RELEASE_MANIFEST.md`. A version label without
the resolved commit is incomplete release metadata.

## 3. Module architecture is a performance decision

Design the import DAG before files become large.

- Put slow-moving definitions and generic algebra low in the graph.
- Put frequently edited instance assembly, target wrappers, and audits at leaves.
- Separate generic mathematics from project-specific estimates.
- Separate object identities from sign or order transfers.
- Isolate expensive normalization engines from small final assembly theorems.
- Prefer several coherent modules over one concatenated file or generated
  monolith.
- Keep the root umbrella importing graph leaves; make `Audit.lean` import the
  public umbrella.

An edit near the root invalidates every descendant. A mathematically elegant
single chain can therefore be an unusable development graph. Split a slow file
when changes to its final theorem repeatedly pay for unrelated algebra,
integration, or normalization.

Import narrowing is a compiled refactor. Replacing `import Mathlib` changes
available notation, dot resolution, instances, tactics, and simp lemmas. Narrow
one coherent region, compile it, and commit only after the full gate passes.

## 4. Build ladder

Use the cheapest check that answers the current question, but never confuse it
with a release gate.

### Fast source check

```sh
./h run --cwd formal --label lean-source -- lake env lean Formal/Foo.lean
```

This checks one source file and is good for tight iteration. It does **not**
create an importable `Foo.olean`.

### Importable target build

```sh
./h run --cwd formal --label lean-target -- lake build Formal.Foo
```

Use this before another new module imports `Formal.Foo`.

### Staleness probe

```sh
./h run --cwd formal --label lean-staleness -- lake build --no-build
```

Use this as a cheap check that the build graph agrees with the source tree. It
is not a compilation.

### Epoch gate

```sh
./h run --cwd formal --label lean-epoch -- lake build
./h run --cwd formal --label lean-audit -- lake env lean Formal/Audit.lean
```

Every commit that claims a maintained Lean result must have both commands pass
in the same working tree being committed. A direct source check, old build log,
generated code claim, commit message, or agent report is not a build.

### Release gate

Repeat the epoch gate in a clean clone or CI environment with the pinned
manifest. Record exact commands, exit status, wall time, peak memory when known,
and axiom output. The clean gate must check the exported target, not merely a
helper module.

Run one Lean/Lake process at a time unless the project has measured and
documented safe isolation. Multiple memory-heavy elaborators commonly make all
of them slower or cause nondeterministic resource failure.

All local Lean/Lake commands use `./h run`: one global compute lock, scheduling
priority at least `nice` 10, and a 240-second process-group watchdog. A tool yield
is not completion. Never respond by launching another compilation, and never
wrap files in `ThreadPoolExecutor`, `Promise.all`, shell background jobs, or
similar fan-out. If a focused target exceeds four minutes, inspect contention;
otherwise narrow imports, split the module, or change the proof/definition. Move
a deliberately longer clean replay to an isolated provisioned runner, expressed
as bounded stages, rather than weakening the desktop guard.

The template pins Lean and mathlib to `v4.32.0` and retains the recovered Lake
options: Unicode function pretty-printing, `relaxedAutoImplicit = false`, the
mathlib standard-set linter, and `maxSynthPendingDepth = 3`. Change these only as
an explicit toolchain migration with cache retrieval, full verification, and a
performance record.

## 5. Mandatory source policy

The theorem-bearing tree must contain no:

- `sorry`, `admit`, or generated equivalent;
- undeclared custom mathematical `axiom` or `constant`;
- `unsafe` bridge used to inhabit or prove a proposition;
- foreign/runtime result presented as a theorem without a named trust boundary;
- theorem whose public statement differs from the target contract;
- imported certificate result without a checked statement bridge.

`scripts/audit_project.py` enforces the syntactic subset of this policy. It is a
guardrail, not a proof of soundness. Legitimate classical reasoning is allowed;
hidden trust is not.

## 6. Axiom audit

Add a `#print axioms` line to `Formal/Audit.lean` in the same change that exports
a theorem. `formal/AXIOMS.md` must state:

- toolchain and resolved mathlib revision;
- audit command;
- every target-facing declaration audited;
- exact printed axiom set;
- whether the audit is exhaustive or a selected transitive surface.

Diff the axiom output at every epoch gate. An audit covers only the declarations
it names; a new module is not protected by an old audit file.

## 7. Statement and non-vacuity audit

For each exported theorem record:

1. the fully elaborated Lean declaration;
2. a target-to-Lean substitution map;
3. a Lean-to-target implication argument;
4. an inhabitant or construction for constrained domains;
5. provenance of every hypothesis;
6. object-identity theorems connecting alternative definitions;
7. branches, endpoints, degeneracies, signs, and orderings covered;
8. the source of every strict inequality;
9. the concrete counterexample condition.

Lean can correctly check a vacuous implication. It does not know that a fresh
positive parameter was supposed to be a value derived from the public object.

## 8. Tactic and elaboration discipline

Prefer proof terms that match the goal shape over broad normalization or search.

- Use exact `HasDerivAt`/continuity/integrability combinators with the correct
  multiplication or composition orientation instead of `convert` followed by
  large algebraic cleanup.
- Instantiate universal hypotheses explicitly before `positivity`, `gcongr`, or
  bound tactics; these tactics do not guess every local instance.
- Register one compositional `@[fun_prop]` lemma for a project definition instead
  of unfolding that definition throughout the tree.
- Use `simp only [...]` in new theorem-bearing code. Bare `simp` is slower and
  inherits version-sensitive global rewrite sets.
- Clear one known denominator with `div_eq_iff`, `eq_div_iff`, or a local lemma
  when possible. Reserve `field_simp` for genuinely multi-denominator goals.
- Normalize after exposing the mathematical cancellation, not before. Global
  `field_simp`, `ring_nf`, or unfolding can hide the hypothesis shape needed by
  the next rewrite.
- Remove tactics after a previous tactic closes the goal; warning-clean scripts
  make real regressions visible.
- Prove repeated fixed-size expansions once and rewrite with the lemma rather
  than re-running determinant/sum normalization at every use.
- Supply explicit endpoints, types, and namespaces when elaboration relies on
  fragile inference.

Do not increase heartbeats, recursion depth, or memory limits as the first
response to a slow proof. First inspect import depth, generated term size,
normalizer scope, duplicated expansions, and theorem shape.

## 9. Performance budget

Create `formal/PERFORMANCE.md` before the project is large. Record:

- cold invocation overhead and warm-cache behavior;
- targeted build time for each expensive module;
- full incremental and clean build times;
- axiom-audit time;
- known peak memory and serialized-build requirement;
- the top invalidation edges in the module DAG.

Use `./h run --cwd formal --label lean-profile -- lake build Formal.Foo`, a
controlled touched-file rebuild, or local `set_option profiler true` to identify regressions. Treat adjacent timings as
observations, not universal benchmarks. Optimize the slowest repeated path, not
the most visible isolated tactic.

Batch Lake invocations when cold startup dominates. During local iteration,
one targeted source check is usually cheaper than a sequence of Lake target
plans; at integration, one `lake build` is cheaper and more truthful than a
handwritten list that may omit stale descendants.

## 10. Certificates and generated Lean

Generated declarations are held to the same policy as handwritten ones. Keep
generators, generated sources, and verifiers distinct. The generator may search;
the verifier must reconstruct the exact proposition from canonical input.

When an external exact or interval certificate remains in the trusted base,
formalize the statement bridge: prove that the certificate's object, domain,
normalization, and conclusion are those consumed by the theorem. A matching
output hash proves reproducibility, not mathematical soundness.

## 11. Failure records

Preserve failed formulations when they teach a stable engineering lesson:

- missing imports discovered only by compilation;
- `convert` producing opaque function/typeclass equalities;
- broad denominator clearing obscuring cancellation;
- blanket automation leaving placeholders or huge terms;
- direct source checks mistaken for importable builds;
- monolithic generated files that cannot replay sequentially.

Label these as formalization failures unless they refute the mathematics.

## 12. Lean definition of done

- exact public target is exported;
- same-tree full build and axiom audit pass;
- clean-clone build passes with pinned dependencies;
- audit includes every target-facing declaration;
- `formal/AXIOMS.md` and project status match printed output;
- no placeholders, hidden axioms, unsafe bridges, or warning debt;
- non-vacuity and statement fidelity are recorded;
- performance remains within the declared release budget.
