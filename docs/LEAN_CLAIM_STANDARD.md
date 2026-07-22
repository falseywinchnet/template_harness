# Lean claim standard

This standard governs when a Lean development may support a scientific or
mathematical publication claim. Kernel acceptance is necessary but not
sufficient. A proof term can be impeccable while the project overclaims through
its definitions, hypotheses, object map, omitted initialization theorem, empty
domain, or prose. The release boundary therefore audits four different things:

1. **Kernel validity:** Lean checks the exact declaration in the pinned tree.
2. **Instantiation:** every helper hypothesis is derived for the actual target.
3. **Statement fidelity:** the exported declaration and frozen public target
   imply one another under exactly the same definitions and conventions.
4. **Interpretation:** the formal object is the independently defined object
   named in the paper, including normalization and representation choices.

Passing an earlier layer never grants a later status automatically.

## 1. Falsification normal form

For a universally quantified claim, define the public pieces independently:

```text
Admissible(x)     the target domain and side conditions
Conclusion(x)     the claimed result
Counterexample(x) := Admissible(x) and not Conclusion(x)
Target            := for every x, Admissible(x) implies Conclusion(x)
```

The formalization must prove that its exported target has this counterexample
interface. For a strict inequality `f x > 0`, the falsifier is `f x <= 0`, not
merely `f x < 0`. For equality it is inequality; for containment it is a source
object whose encoded image is not in the target set. Endpoint, degenerate, and
confluent instances belong to `Admissible` unless explicitly excluded by the
frozen public statement.

The counterexample definition must not be constructed as `False`, use an empty
subtype, or repeat the theorem as an assumption. It must expose actual data that
could be constructed before the theorem is known. A search that finds no
counterexample is evidence about the search, not the universal proof.

## 2. Objective target interior

Every target-bearing development must contain an **objective target-interior
witness**. Here “interior” first means an independently constructible, genuine
instance inside the target domain and on the claimed side of the boundary; it
does not assert a topological interior unless the theorem supplies a topology.

The witness must provide:

- an object built without a proof of the desired conclusion in its type;
- a proof that it satisfies the independently defined admissibility predicate;
- an instantiation of the actual result predicate for that same object;
- for a strict/nondegenerate claim, the positive margin, nonzero quantity,
  positive-length interval, distinct points, or other fact excluding equality;
- a trace to the public target object or to a canonical instance of its
  quantified domain.

The result proof must be target-independent: it may not invoke the exported
universal/containment theorem whose anchoring it is meant to test. Audit its
transitive dependencies. Deriving `ObjectiveInterior` from the finished target
and a domain witness is logically valid but circular for this gate.

`x : {x // Conclusion x}`, a structure field `hConclusion`, or a hypothesis
`h : Conclusion x` is not an objective witness. It merely stores the desired
fact. Construct raw data first and prove the property afterward. If meaningful
topological interior is claimed, additionally prove an explicit radius or
neighborhood contained in the property; do not infer robustness from one strict
sample.

An interior witness does not prove a universal theorem. It proves that the
formal target has at least one real instance and that the definitions can touch
the intended phenomenon. Universal coverage remains a separate obligation.

The narrow exception is a frozen theorem whose conclusion is itself
nonexistence or emptiness. Such a claim cannot have an instance satisfying its
conclusion. It must instead construct an independently inhabited ambient domain,
define the prohibited object without contradiction, and record that an actual
prohibited object is the exact counterexample. This exception cannot be used to
excuse an empty antecedent in an ordinary positive or containment claim.

## 3. Containment and invariant claims

For a source algorithm/object class `A`, target region `B`, encoding `encode`,
and transition relation `R`, keep these propositions distinct:

```text
object identity:  encode denotes the public analytical object
initialization:   A(x) implies B(encode(x))
preservation:     B(x) and R(x,y) imply B(y)
reachability:     every generated state follows from an initialized state by R
containment:      every generated public object lies in B
```

Preservation or “no outward seam” does not prove initialization. A closed region
can be disjoint from the source objects. A proof of `B x -> B (step x)` cannot be
named or published as `A subset B` unless initialization and the semantic map
are also proved. In static work, prove `A x -> B (encode x)` directly. In dynamic
work, prove initialization and preservation, then derive containment by the
inductive reachability relation.

Each exported containment claim must name separate declarations for object
identity and initialization. If preservation is irrelevant, say so; do not use
an invariance theorem as decorative support.

## 4. Assumption budget

Helper lemmas may be conditional. The target-facing theorem may quantify only
over assumptions present in the frozen public target. Every additional technical
hypothesis must be discharged by an instantiation theorem for the actual public
object before the result can be promoted.

In particular, do not leave these as target-facing parameters when they are the
substance of the project:

- positivity, nonvanishing, normalization, convergence, or integrability;
- membership in the claimed class;
- the sign of the final determinant, residual, derivative, or certificate;
- equality between a computational surrogate and the public object;
- surjectivity when only an actual-range inverse was constructed;
- existence of a crossing, optimizer, measure, solution, or witness.

Maintain an assumption ledger from every exported theorem to its origin. A
project theorem with a convenient structure argument is not closed merely
because some future caller could construct that structure.

## 5. Definition audit

Definitions can launder conclusions without any axiom or placeholder. Audit
every target-reachable definition before the proof:

- Is the public object constructed independently rather than selected from a
  subtype already carrying the result?
- Does a predicate encode the standard mathematical concept, not a weakened
  project-specific proxy?
- Are absolute values, squares, maxima, truncations, defaults, or coercions
  hiding the sign or branch that must be proved?
- Are denominators, orientations, units, index subtraction, Fourier signs, and
  normalization constants identical to the public convention?
- If two representations are used, is their equality proved for the complete
  domain in both directions?

Theorem names, comments, namespaces, and notation have no evidentiary force.
Fully unfold or print target-facing definitions during the statement audit.

## 6. Required declaration chain

For each public formal claim, record distinct declarations for:

1. raw public-object construction;
2. representation/object-identity theorem;
3. admissible-domain witness;
4. objective target-interior theorem;
5. side-condition and assumption discharge;
6. initialization/membership theorem where containment is claimed;
7. preservation and reachability theorem where dynamics are claimed;
8. exported target theorem;
9. counterexample-normal-form equivalence;
10. strict exterior witness when an exact-order or failure-beyond-the-boundary
    classification is claimed;
11. `#print axioms` audit for every declaration above that carries the result.

“Not applicable” requires a written mathematical reason. Combining several
links into one theorem is allowed only if its statement exposes each obligation
and the audit can still identify where it is discharged.

## 7. Adversarial derivation review

Before promotion, a reviewer who did not build the main proof tries to break the
claim along these axes:

- replace the target object with an arbitrary object satisfying the helper
  assumptions; if the proof still works, check whether actual instantiation is
  missing;
- delete initialization and retain preservation; verify that the public claim
  no longer follows;
- construct a concrete admissible instance without using the conclusion;
- expand every subtype and structure field to find stored result assumptions;
- negate the exact conclusion and ensure the recorded counterexample has data;
- check equality and boundary cases for every strict conclusion;
- compare both implication directions between the Lean declaration and target;
- trace the named paper object through all representation changes;
- inspect every target-reachable imported theorem and its actual hypotheses;
- search for a smaller theorem that the code proves while the prose states a
  larger one.

The main author or model does not certify its own semantic interpretation alone.
Independent review can share the Lean kernel but must reconstruct the target map
from the frozen contract.

## 8. Status language

Use these distinctions in reports and papers:

- `KERNEL_CHECKED`: the exact Lean declaration builds and its axioms are known.
- `TARGET_INSTANTIATED`: helper assumptions are discharged for the public object.
- `STATEMENT_FAITHFUL`: two-way target and interpretation audits pass.
- `FORMALLY_PROVED`: all preceding gates, objective interior, falsification
  interface, clean build, and independent review pass.

Never shorten `KERNEL_CHECKED` to “proved” when the target map remains open.

`formal/CLAIMS.json` is the lightweight promotion register. Every public formal
claim gets one entry with its claim kind, target version, declaration, status,
and the declaration names supporting the earned gate. The project audit rejects
status promotion when required links are blank. This registry is an index, not
evidence: a dishonest declaration name remains dishonest, and the Lean build and
independent semantic review must still verify every link.
The policy audit also requires each registered declaration in
`Formal/Audit.lean`, its target version in `research/TARGET.md`, and its claim ID
in `research/CLAIM_INDEX.md`.

Required fields progress with status:

- `KERNEL_CHECKED`: `claim_id`, `kind`, `target_version`, `declaration`, and
  `axiom_audit`;
- `TARGET_INSTANTIATED`: additionally `object_identity`, `domain_witness`, and
  `actual_instantiation`;
- `STATEMENT_FAITHFUL`: additionally `objective_interior` and
  `interior_dependency_audit` (or the explicit nonexistence replacement),
  `counterexample_equivalence`, both fidelity
  directions, `definition_audit`, and `independent_reviewer`;
- `FORMALLY_PROVED`: additionally `audit_declarations` and `release_gate`.

Containment claims also require `initialization`; invariant claims require
`initialization`, `preservation`, and `reachability`; exact-order claims require
an `exterior_witness`. At `STATEMENT_FAITHFUL`, containment/invariant entries
also require an `initialization_dependency_audit`; invariant entries require a
`dynamics_dependency_audit`, preventing the final claim from being smuggled into
its own prerequisites.
Nonexistence claims use kind `nonexistence` and require
`ambient_domain_witness` plus `nonexistence_boundary` instead of a positive
objective-interior witness.

## 9. Source restrictions

The target-bearing tree contains no placeholders, custom axioms/constants,
unsafe or foreign proof bridges, native-evaluation proof shortcuts, runtime
tactics, generated declarations accepted without source review, or local
resource-limit/implicit-variable overrides masking an intractable or
underspecified proof. Diagnostic evaluation is kept outside theorem-bearing
modules. `scripts/audit_project.py` enforces a
conservative syntactic subset; semantic gates remain human and mathematical.

The generic vocabulary in `Formal/ClaimContract.lean` does not discharge a
project claim. It only makes the distinctions executable. A project must
instantiate them using its independently defined objects and list the resulting
declarations in `research/FORMALIZATION.md` and `Formal/Audit.lean`.
