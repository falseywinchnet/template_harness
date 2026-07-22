# Computation workspace

Use this directory for maintained result-bearing computational machinery. Raw
experiments remain inside their `work/R.../` round until a refinement round
promotes them.

Before implementing a material computation, copy and complete
`COMPUTE_PLAN.md`. The plan is not bureaucracy: representation, complexity,
precision, completeness, and verifier shape determine whether the algorithm can
ever become a scientific result.

Recommended layout after the first real artifact exists:

```text
computations/
├── COMPUTE_PLAN.md
├── BENCHMARKS.md
├── requirements.lock or pyproject/lock files
├── generators/
├── verifiers/
├── manifests/
└── fixtures/
```

Do not create empty directories as progress. Keep large regenerable caches and
cell streams out of Git; commit compact canonical manifests, verification code,
small fixtures, and hashes. Never use pickle or a private cache as the public
certificate boundary.

See `docs/COMPUTE_DESIGN.md` and `docs/PYTHON_COMPUTATION.md`.
