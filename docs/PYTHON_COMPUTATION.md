# Python, SymPy, and certified computation

Python is the default orchestration and exact-certificate language for this
template. The harness itself remains standard-library only. Scientific projects
may add pinned dependencies, but must declare which library is discovery support,
which is a generator, and which lies in the trusted verification boundary.

## 1. Arithmetic classes

Use the narrowest class that supports the claim:

- `int` and `fractions.Fraction` for exact integer/rational algorithms;
- `sympy.Integer`, `Rational`, `Poly`, and exact domains for symbolic algebra;
- `decimal.Decimal` only with an explicit context and error model;
- `mpmath` for high-precision diagnostics, never directed enclosure by itself;
- Arb/python-flint or another justified interval package for outward-rounded
  transcendental and interval conclusions;
- NumPy/SciPy for exploration, numerical linear algebra, and empirical work with
  a stated floating-point error or statistical model.

Never create theorem-bearing rationals through a binary float:

```python
from fractions import Fraction
import sympy as sp

good_q = Fraction(1, 10)
good_s = sp.Rational(1, 10)
good_text = sp.Rational("0.1")
# Avoid Fraction(0.1) and sp.Rational(0.1) in exact evidence.
```

When reproducibility requires SymPy's pure-Python rational domain, set
`SYMPY_GROUND_TYPES=python` before importing SymPy and test that forbidden
accelerator imports do not occur. If FLINT is part of the trusted boundary,
pin and record it instead; do not let backend selection change silently.

## 2. Symbol assumptions are not proofs

`symbols("x", positive=True)` tells SymPy how to simplify an abstract symbol.
It does not prove that a value derived elsewhere is positive, nonzero, real, or
in the target domain. Record and prove the substitution conditions separately.

Likewise, a CAS identity for a ratio does not establish:

- denominator nonvanishing;
- existence or normalization of the objects represented;
- domain membership or endpoint limits;
- monotonicity on the required interval;
- strictness of an integral or determinant;
- identity between the encoded expression and the public target object.

Use symbolic checks as one edge in the claim graph, not as a status shortcut.

## 3. Exact identity checks

Choose a canonical check matched to the expression class:

```python
residual = lhs - rhs

# Polynomial identity in declared generators.
assert sp.Poly(sp.expand(residual), *generators, domain=sp.QQ).is_zero

# Rational-function identity after separately proving denominators nonzero.
assert sp.cancel(sp.together(residual)) == 0

# Structured factored identity when expansion would swell.
numerator, denominator = sp.fraction(sp.together(residual))
assert sp.Poly(numerator, *generators).is_zero
```

`simplify(...) == 0` is acceptable as a diagnostic but is a broad heuristic and
poor sole verifier for expensive result-bearing identities. Prefer explicit
domains, generators, and normal forms. Verify that the normal form itself did
not introduce excluded denominator cases.

## 4. Control expression swell

- Do not call `expand`, `factor`, `simplify`, or `together` on the largest
  expression by reflex. Measure term count before and after.
- Extract required coefficients during construction instead of expanding the
  full substituted expression and truncating later.
- Represent sparse polynomials as exponent-tuple dictionaries when SymPy object
  overhead dominates.
- Use `Poly` with an explicit domain and generator order.
- Factor known geometry and forced zeros before absolute coefficient bounds.
- Keep tiny rational constants outside large polynomial arithmetic when
  possible; combine them at the residual stage.
- Memoize powers, derivatives, recurrence terms, and cofactors by immutable
  arguments.
- Use common-subexpression elimination for evaluation code, not as a substitute
  for a proof of the transformed identity.
- Prefer exact recurrences to repeated symbolic differentiation.
- Split regimes when a single expansion center or coordinate is ill-conditioned.

Before adopting a custom integer/sparse kernel, compare it end-to-end against
the direct SymPy expression on fixed-seed random rational inputs and exact edge
cases. Then let the small certificate verifier, not the comparison test, carry
the claim.

## 5. Determinants and linear algebra

For small fixed matrices, a direct fraction-free or permutation formula may be
more auditable than a generic floating solver. For larger exact matrices use
domain-aware algorithms and exploit symmetry, band, Toeplitz, block, or low-rank
structure before elimination.

Never decide a strict determinant sign from an ill-conditioned double-precision
value. Discovery may locate a candidate numerically; final evidence needs exact
arithmetic, a directed enclosure bounded away from zero, or a formal proof.

## 6. Series and transcendental functions

Every truncation needs:

- exact recurrence or coefficient definition;
- convergence domain;
- explicit remainder bound with orientation;
- monotonicity or ratio condition used by the tail bound;
- precision/rounding behavior;
- special handling of cancellation, endpoints, and argument reduction.

For alternating or positive series, encode the mathematical remainder theorem
rather than estimating the last term heuristically. Argument reduction can turn
a weak global expansion into a strong local one, but its reconstruction error
must be enclosed.

## 7. Directed intervals

An interval certificate records the whole function range, not midpoint samples.

- Construct interval inputs without an intermediate binary float.
- Confirm every library operation rounds outward at the selected precision.
- Widen midpoint evaluation by a proved derivative/Lipschitz/Taylor bound when
  direct interval evaluation loses too much dependence.
- Preserve shared variables with Taylor models or correlated forms.
- Prove that the list of boxes covers the domain without gaps.
- Store undecided cells; never drop them from the denominator.
- Require a lower bound `> 0` or upper bound `< 0` for a strict sign.
- Repeat a representative calculation at changed precision or partition as a
  robustness check, while retaining one declared certificate as canonical.

Converting an already-enclosed quantity to float for display or an integer loop
count can be harmless; using the float inside a mathematical bound is not.

## 8. Discovery, quick audit, full replay

Label commands truthfully:

- **discovery**: search, plotting, sampling, heuristic simplification;
- **quick audit**: checks identities, hashes, or selected outputs without
  reproducing all base calculations;
- **full replay**: regenerates every result-bearing certificate from canonical
  input;
- **release verification**: independently checks stored certificates and the
  theorem/claim bridge in the frozen environment.

A quick wrapper must not be described in the paper as the full directed
calculation. `paper/RELEASE_MANIFEST.md` should map each claim to the actual
full and quick commands separately.

## 9. Generator and verifier implementation

Generator requirements:

- may search or adapt, but logs all branches and budgets;
- emits a versioned canonical manifest;
- checkpoints long work without trusting partial completion;
- writes outputs atomically;
- records exact parameters, environment, runtime, and hashes.

Verifier requirements:

- smaller than the generator where practical;
- reconstructs the proposition from canonical input;
- rejects missing, duplicate, reversed, overlapping-invalid, or malformed
  records;
- performs no network access and no heuristic search;
- ignores generator-supplied truth labels;
- returns nonzero on undecided or incomplete coverage;
- prints a concise stable final status suitable for hashing.

## 10. Reproducibility and environment

Pin direct scientific dependencies in a lockfile or requirements file and
record transitive resolution for a release. The manifest should include:

- Python implementation/version and executable checksum when appropriate;
- operating system/platform and architecture;
- dependency names and exact versions;
- arithmetic backend and precision;
- source, input, output, and verifier SHA-256 values;
- command, working directory, seed, locale, and relevant environment variables;
- wall time, peak memory, term/cell counts, and expected final predicate;
- environment image digest, or an honest `unavailable` plus a fingerprint.

Do not invent a container or image identity that was not used.

## 11. Testing requirements

- exact unit cases with known answers;
- boundary, zero, sign, parity, and degenerate cases;
- generator/verifier corruption tests;
- fixed-seed rational cross-checks against an independent formulation;
- numerical diagnostics at increased precision;
- regression on term counts, output digest, and performance budget;
- clean-environment full replay for release.

Random testing can find counterexamples and implementation mismatches. Passing
random tests does not establish a universal mathematical statement.

## 12. Script shape

Result-bearing scripts should have a `main`, explicit paths relative to the
repository root, deterministic output, typed pure core functions, and no import-
time heavy computation. Avoid hidden current-directory assumptions and mutable
module globals. Prefer structured exceptions and a nonzero exit to bare asserts
for user/input validation; exact internal invariants may use asserts when Python
optimization flags are prohibited by the replay command.

For long runs, emit stage progress at intervals shorter than the operator's
monitoring window and write resumable checkpoints atomically. A checkpoint is a
performance aid, not a certificate until the verifier confirms complete output.
