# Target-reachable dependency graph

## Main chain

```text
C001 primary claim
├── C002 prerequisite claim
│   ├── E001 preserved source or dataset
│   └── O001 unresolved verification obligation
└── C003 independent falsification boundary
    └── E002 replayable experiment or formal theorem
```

## Typed edges

- `C001 because C002, C003`.
- `C002 supported-by E001`.
- `C003 checked-by E002`.
- `O001 blocks C002`.
- `C001 instantiated-by T001` (actual target satisfies helper hypotheses).
- `T001 identifies O001` (formal object equals the public object).
- `C001 anchored-by W001` (raw admissible objective-interior witness).
- `T001 initialized-by I001` (source object enters the claimed region).
- `C001 excludes-counterexample X001` (exact falsification interface).

## Expansion rule

Expand every inferential edge until each reachable leaf is one of:

1. a preserved external source with exact locator;
2. a preserved dataset and acquisition record;
3. a replayable computation with environment and expected output;
4. a formal theorem with exact statement and audited assumptions;
5. a declared trusted assumption or foundation;
6. an explicit unresolved obligation.

Cycles remain visible as named components. Contextual citations that are not
used inferentially do not enter the critical dependency closure.

Closure/preservation edges cannot discharge initialization or containment
edges. Object identity, actual-target instantiation, objective interior, and
counterexample exclusion are target-reachable dependencies, not prose metadata.

## Current unresolved target leaves

- `O001` — replace with the first real unresolved boundary.

## Deliberately non-reachable work

List interesting branches that are not allowed to support the target. This
prevents an adjacent conjecture or experiment from lending evidence backward.
