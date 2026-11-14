# Source provenance — standalone evidence harness

This is an independently maintained Apache-2.0 derivative; no endorsement from WaterSheep maintainers is implied.

**Source:** `https://github.com/es-3581100/WaterSheep`; **PR:** `#2`; **pinned commit:** `cdce968a7ed7c6a4f4f983c07438a49702157000`.

**Target:** `https://github.com/es-3581100/watersheep-rust-wasm-harness` (existing Apache-2.0 LICENSE must remain unchanged).

**Audit:** `reports/extraction-audit.md`, SHA-256 `c170e8692f050cbf1468927c1e7bbe367cd0659b0a031551d351e1619104ebc9`.

Original Git blob identifiers are **SHA-1 object IDs**, not evidence receipt SHA-256. All 27 source blob IDs were verified against the pinned local Git commit. Six unchanged files match those blobs byte-for-byte. Destination hashes in the manifest describe the original staging artifact, prior to documented integration formatting and CI changes.

## Provenance ledger

| Source path | Git blob SHA-1 | Destination path | Classification | Changes and justification |
|---|---|---|---|---|
| `.github/workflows/rust-harness.yml` | `75e3240a9950377e0915760e04b22c0ecd8634a4` | `.github/workflows/verify.yml` | refactor | Standalone-path CI; tests native Rust/Go, offline smoke, Node WASM runtime and TS declarations; exact wasm-bindgen version from lock. |
| `go-bridge/README.md` | `ae446789f6ccee0a0bd210ec067d4c2c8148f59f` | `go-bridge/README.md` | refactor | Standalone supervisor documentation and scoped approval names. |
| `go-bridge/cmd/watersheep-supervisor/main.go` | `6f77e6a449b62f86faceeb58fee64b0567af9cc0` | `go-bridge/cmd/watersheep-supervisor/main.go` | refactor | Standalone Go import and module identity; scoped debug log consent; optional application readiness request; local-only configuration. |
| `go-bridge/go.mod` | `4eae1866663026bc6ada31757ea00eb24680de32` | `go-bridge/go.mod` | refactor | Rename Go module to independent es-3581100 standalone repository. |
| `go-bridge/internal/supervisor/supervisor.go` | `e209b4b8b22f9675e892b4208c63639dfed3dd30` | `go-bridge/internal/supervisor/supervisor.go` | refactor | Standalone ownership identifier; loopback enforcement; operation-scoped debug approval; bounded request handling; child shutdown; optional JSON readiness. |
| `go-bridge/internal/supervisor/supervisor_test.go` | `7b0d7a39ccfd750b25f5f3bf002d972eda5d018d` | `go-bridge/internal/supervisor/supervisor_test.go` | refactor | Previously unchanged reuse candidate upgraded to refactor: use operation-scoped log consent; original test assumption no longer valid. |
| `rust-harness/Cargo.toml` | `4dd66b755c44351e71dc016d85cee438cbccdea5` | `rust-harness/Cargo.toml` | refactor | Update repository metadata and standalone package description; preserve Rust crate name, features, and dependencies. |
| `rust-harness/README.md` | `ea074ded65566ed22e0ba838f63aff1b885a1ed3` | `README.md` | refactor | Replace upstream monorepo and downstream-specific README with independent README and correct commands. |
| `rust-harness/examples/request.json` | `d017f2e3733376cc168c61bafe5e47b6e15757a4` | `rust-harness/examples/request.json` | unchanged | Reused unchanged, byte-identical to pinned Git blob. |
| `rust-harness/schema/watersheep-harness-receipt-v1.schema.json` | `40d3a69ef47680db667b575e06a57629de9430c2` | `rust-harness/schema/watersheep-harness-receipt-v1.schema.json` | refactor | Update $id to independent repository, preserve v1 schema/producer/authority and properties. |
| `rust-harness/src/bin/watersheep-harness.rs` | `5d8a58a28f4fc6babc010c8dc7d9162382bf4ee6` | `rust-harness/src/bin/watersheep-harness.rs` | refactor | Add --dev plus per-call approval to raw --response-out export; preserve original projection/validate behavior. |
| `rust-harness/src/client.rs` | `d912e99b60fedca94768c0a57bfd95608ad94c92` | `rust-harness/src/client.rs` | unchanged | Reused unchanged, byte-identical to pinned Git blob. |
| `rust-harness/src/contracts.rs` | `9d164590c85b2405a3bd9ecce3a8bae9c8a2324c` | `rust-harness/src/contracts.rs` | unchanged | Reused unchanged, byte-identical to pinned Git blob. |
| `rust-harness/src/lib.rs` | `1c0141ad4b11ef13b9e8656f685444ce58ce8edc` | `rust-harness/src/lib.rs` | unchanged | Reused unchanged, byte-identical to pinned Git blob. |
| `rust-harness/src/receipt.rs` | `b528982e4d6b9b94249451f59f185144e72f562f` | `rust-harness/src/receipt.rs` | unchanged | Reused unchanged, byte-identical to pinned Git blob. |
| `rust-harness/src/wasm.rs` | `99b194606559ab05bd78bfb2701452748a562aa4` | `rust-harness/src/wasm.rs` | unchanged | Reused unchanged, byte-identical to pinned Git blob. |
| `tools/pybundle/watersheep_bundle.py` | `492cf0e9f4edec804356097894c1cdef7069f73b` | `tools/smoke.py` | refactor | Replace source-relative launcher with deterministic synthetic offline supervisor fake, explicit dev/debug gate checks and native receipt tests. |

## Boundary and dependency trace

Original WaterSheep inference remains an optional separate runtime. The Go supervisor forwards inference and reports lifecycle observation; Rust derives typed JSON receipts; WASM projects receipts without transport; TypeScript declarations are generated from Rust types. The 10 excluded PR files are enumerated only in `reports/extraction-manifest.v1.json`, and none are included as implementation files.

## Licensing

All transferred source files originated under the upstream Apache-2.0 license and upstream NOTICE identifying Samrat Dutta (2026). This derivative retains a standalone NOTICE and license text. An installation overlay **never overwrites** the target repository’s existing LICENSE, verified upstream/target original Git blob `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`. The staging bundle includes a distro-standard Apache-2.0 license text with different byte hash than the original target, and must not be used to replace that target file. Original model weights, datasets and training data are not redistributed.

## Protocol invariants

The unchanged Rust `contracts.rs`, `receipt.rs`, `client.rs`, `lib.rs`, `wasm.rs` and neutral request example preserve original v1 protocol semantics. Go and CLI refactors do not change receipt serialization. Hashes describe **typed canonicalized JSON**, not wire bytes or unique request correlation. The native source oracle and actual Node WASM equivalence passed for the supplied golden vector.
