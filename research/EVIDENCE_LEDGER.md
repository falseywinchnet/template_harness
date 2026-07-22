# Evidence ledger

| Evidence | Kind | Local path | Origin / locator | Integrity | Reproduction command | Supports | Status |
|---|---|---|---|---|---|---|---|
| `E001` | source / dataset / replay / formal | `sources/...` | author, repository, instrument, or URL | SHA-256 or version | exact command or `n/a` | `C002` | missing |

## Rules

- Preserve original bytes before normalization or transformation.
- Record checksums for immutable inputs and release artifacts.
- Record license, consent, privacy, and access constraints for data.
- Separate exploratory output from result-bearing evidence.
- A replay entry includes the environment, command, expected exit status, and a
  stable output digest or exact acceptance predicate.
- A formal entry includes the elaborated theorem, toolchain revision, dependency
  revision, and axiom or trust audit.
