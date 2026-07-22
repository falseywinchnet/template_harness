# Trusted base

Everything listed here is outside at least one checked boundary. Minimize the
list; do not hide assumptions in prose.

## Scientific assumptions

- Population, model, regularity, measurement, or foundational assumptions.

## External data and instruments

- Dataset origin, instrument calibration, acquisition software, and custody.

## Software and formal systems

- Operating system and hardware boundary.
- Language runtime, solver, compiler, libraries, and exact versions.
- Formal kernel, imported theorem library, axioms, classical principles, or
  quotient constructions accepted by the project.

## Human judgments

- Inclusion/exclusion decisions, labels, adjudication, transformations, and
  interpretation choices.

## Semantic naming boundary

- Equality between the independently defined formal object and the object named
  in the publication, including units, signs, normalization, and conventions.
- Any remaining interpretation that is argued in prose rather than proved as a
  target-reachable Lean declaration.

Do not hide this boundary behind a familiar theorem or namespace name. Reduce it
with an object-identity theorem or disclose it as an unresolved limitation.

## Reduction plan

For every high-risk trusted component, state whether it will be independently
reproduced, cross-checked, formally reduced, sensitivity-tested, or disclosed as
a limitation.
