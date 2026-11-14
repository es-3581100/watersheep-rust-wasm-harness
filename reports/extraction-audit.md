# WaterSheep Rust/WASM Evidence Harness — Read-only extraction audit

**Canonical status:** `READ_ONLY_AUDIT_COMPLETED__EXTRACTION_NOT_PERFORMED`  
**Audit date:** 2026-11-13 (UTC)  
**Source:** [https://github.com/es-3581100/WaterSheep/pull/2](https://github.com/es-3581100/WaterSheep/pull/2) (open, **not merged**, 27 changed files; 3,753 added lines at audit)  
**Pinned PR head:** `cdce968a7ed7c6a4f4f983c07438a49702157000`  
**Pinned PR base:** `aa308f7778a06bad77c1adb3e3109e27bed03736` (`upstream-main`)  
**Target remote:** [https://github.com/es-3581100/watersheep-rust-wasm-harness](https://github.com/es-3581100/watersheep-rust-wasm-harness) (`main` contains only `LICENSE` in inspected Git tree)  
**Requested local target:** `/home/sticky-ricky/repos/es-3581100/watersheep-rust-wasm-harness` (**not accessible/mounted here**)  
**Scope:** Read-only identification and extraction design. No source mutation, target mutation, commit, push, publishing, copying code, or PR merge.

## Decision

**PROCEED TO REVIEW; NOT YET READY FOR EXTRACTION ACCEPTANCE.** Isolate the Rust evidence core and Go supervisor without importing the application-specific integration subtree. The source commit has successful CI, but this does **not** prove the standalone harness, true cross-runtime parity, raw-output approval, or end-to-end domain independence.

**27 PR file classifications:** **7** candidate reuse unchanged, **10** requiring domain-neutral/refinement changes, **10** hard excluded. An unchanged candidate is *eligible for copying with its current source bytes*, not a claim that the eventual standalone package is production-ready. No actual code was copied.

## Component inventory and dependency relationships

```text
External WaterSheep runtime / compatible POST /v1/systemone server
    ^                                    (the inference engine is NOT bundled)
    | native HTTP
Go supervisor: cmd/watersheep-supervisor/main.go
    -> internal/supervisor/supervisor.go  (child lifecycle, proxy, GET /v1/status)
    -> POST /v1/systemone                (raw proxy, not a Rust receipt)
    -> DEV-only /v1/debug/*              (observation-only, header gate)
    ^
    | Rust client::WaterSheepClient (reqwest, native feature)
Rust CLI (ask | project | validate)
    -> contracts.rs (SystemOneRequest/Response, QuestionSpec, Answer, Usage)
    -> receipt.rs   (validation -> typed JSON canonicalization -> SHA-256)
       -> HarnessReceipt v1 {authority: evidence-only, request_sha256,
                            response_sha256, usage, decisions[]}
       -> schema/watersheep-harness-receipt-v1.schema.json
       -> src/wasm.rs (wasm-bindgen: offline validate_request_json,
                                        offline project_receipt)
       -> ts-rs derives (TypeScript declarations on Rust tests/exports)
    -> read-only downstream adapter (only displays/inspects, never authorizes)
Fake upstream + smoke: tools/pybundle/watersheep_bundle.py
    -> Go build/test and temporary supervisor/child processes
    -> native Rust test + CLI ask (when Cargo installed)
CI: .github/workflows/rust-harness.yml -> native Rust, Go, smoke, wasm32 check
```

### Evidence contract details

- Request: `state` is arbitrary JSON; `questions` is a sorted `BTreeMap<String, QuestionSpec>` with `noul|choice|score|multi`, `instructions`, optional `criteria`, and an optional threshold for multi-label questions.
- Response: `model`, sorted `answers`, optional/default token `usage`. Answer details include choice/score/probabilities/confidence, score `legend`, `truncated`, and in-band `error`.
- Receipt: `schema=watersheep.harness.receipt/v1`, `producer=watersheep-rust-harness`, enum-only `authority=evidence-only`, `endpoint`, both lowercase-hex SHA-256 digests, `model`, `usage`, and a deterministically sorted list of normalized decisions.
- Projection: yes/no synthesizes `yes`/`no` probabilities, selected label and confidence; choice retains selected label; score retains scalar/legend; multi returns selected choices; errors produce `status=error`; truncation propagates.
- Response matching: the set of response answer names must **exactly equal** the request question names. This rejects mismatches but **does not bind requests to responses with the same names**.
- Hash semantics: `hash_json` serializes *validated, deserialized typed objects* via `serde_json::to_value`, recursively sorts object keys, serializes JSON and computes SHA-256. This is deterministic under object-key reordering as directly covered by one Rust unit test. **It is not a raw HTTP wire-body digest and is not claimed to be RFC 8785 JCS.** Defaults, ignored unknown fields and numeric representations need explicit cross-runtime documentation.
- WebAssembly: transport-free `validate_request_json` and `project_receipt` call the same Rust logic; WASM is not an inference engine, supervisor or HTTP client.
- TypeScript: `ts-rs` derives under `typescript` feature for contracts; generated `.ts` files are build outputs, not part of PR's 27 paths. Verify generated declarations independently.

## Extraction manifest (complete PR inventory)

The source blob IDs below are **Git blob SHA-1 identifiers, not SHA-256 content receipts**. Pin each candidate to PR head `cdce968a7ed7c6a4f4f983c07438a49702157000`; do not read floating branch names at extraction time.

| PR file / component | Class | Pinned Git blob SHA-1 | Rationale |
| --- | --- | --- | --- |
| `.github/workflows/rust-harness.yml` | REFACTOR | `75e3240a9950377e0915760e04b22c0ecd8634a4` | Root-path workflow, pin toolchains; add actual WASM JS/TS and fixture gates. |
| `go-bridge/README.md` | REFACTOR | `ae446789f6ccee0a0bd210ec067d4c2c8148f59f` | Replace source-monorepo launch and downstream assumptions; describe standalone dev boundary. |
| `go-bridge/cmd/watersheep-supervisor/main.go` | REFACTOR | `6f77e6a449b62f86faceeb58fee64b0567af9cc0` | Change Go import module path; review child launch and dev/smoke-only override. |
| `go-bridge/go.mod` | REFACTOR | `4eae1866663026bc6ada31757ea00eb24680de32` | Change module from upstream SamratDuttaOfficial/WaterSheep/go-bridge to standalone repository. |
| `go-bridge/internal/supervisor/supervisor.go` | REFACTOR | `e209b4b8b22f9675e892b4208c63639dfed3dd30` | Update status module identifier and harden readiness, debug exposure and process handling. |
| `go-bridge/internal/supervisor/supervisor_test.go` | REUSE | `7b0d7a39ccfd750b25f5f3bf002d972eda5d018d` | Domain-neutral unit tests for status ownership, debug approval and log-ring buffer. |
| `kol-watersheep/.gitignore` | EXCLUDE | `86847de23c58e8e71312110dd1c221605560ca2d` | Entire application-specific integration subtree prohibited. |
| `kol-watersheep/README.md` | EXCLUDE | `822db60af38884707aeaf35e263d72aa3c66a4a9` | Application-specific documentation prohibited. |
| `kol-watersheep/assets/compat_adapter.py` | EXCLUDE | `0d0cf37536d963fec28b44b43b607d098b5baeaf` | Application-specific adapter prohibited. |
| `kol-watersheep/assets/environment.yml` | EXCLUDE | `2c6812f2820b824ed29aeb49670354f8a3e4d6b3` | Application-specific dependency environment prohibited. |
| `kol-watersheep/assets/kolstack` | EXCLUDE | `f8805637ffeef825c2c68d92435f5cade8a8bd3d` | Application-specific launcher/integration prohibited. |
| `kol-watersheep/go.mod` | EXCLUDE | `c8632cccc7a400fae591c268e10f16dda46ad805` | Application-specific Go module prohibited. |
| `kol-watersheep/main.go` | EXCLUDE | `1d0364458e94b9fab9e31b7f1e6ee0946742e58d` | Application-specific executable prohibited. |
| `kol-watersheep/main_test.go` | EXCLUDE | `7b72c48f620ad8cfc113bc225cc19f2aa8cb8783` | Application-specific fixture/test code prohibited. |
| `kol-watersheep/tests/test_http_bridge.py` | EXCLUDE | `f0ac684503fb34300de36f829090d4af7cebe232` | Application-specific bridge test prohibited. |
| `kol-watersheep/tests/test_launcher.py` | EXCLUDE | `0a0c236efa49dae2977425073ddeb08b2d4f4eb3` | Application-specific launcher test prohibited. |
| `rust-harness/Cargo.toml` | REFACTOR | `4dd66b755c44351e71dc016d85cee438cbccdea5` | Package repository metadata currently points to upstream WaterSheep; set standalone provenance/lockfile. |
| `rust-harness/README.md` | REFACTOR | `ea074ded65566ed22e0ba838f63aff1b885a1ed3` | Remove named downstream application/matrix, update paths and distinguish audit evidence from permission. |
| `rust-harness/examples/request.json` | REUSE | `d017f2e3733376cc168c61bafe5e47b6e15757a4` | Neutral customer-support example; no application-specific data. |
| `rust-harness/schema/watersheep-harness-receipt-v1.schema.json` | REFACTOR | `40d3a69ef47680db667b575e06a57629de9430c2` | Update $id/provenance for standalone; retain v1 wire contract while adding schema validation. |
| `rust-harness/src/bin/watersheep-harness.rs` | REFACTOR | `5d8a58a28f4fc6babc010c8dc7d9162382bf4ee6` | Review unguarded --response-out raw observation export against per-call approval policy. |
| `rust-harness/src/client.rs` | REUSE | `d912e99b60fedca94768c0a57bfd95608ad94c92` | Domain-neutral native HTTP transport to WaterSheep-compatible endpoint. |
| `rust-harness/src/contracts.rs` | REUSE | `9d164590c85b2405a3bd9ecce3a8bae9c8a2324c` | Typed generic System One contracts; BTreeMap and evidence-only authority enum. |
| `rust-harness/src/lib.rs` | REUSE | `1c0141ad4b11ef13b9e8656f685444ce58ce8edc` | Native/WASM feature-gated exports and shared receipt surface. |
| `rust-harness/src/receipt.rs` | REUSE | `b528982e4d6b9b94249451f59f185144e72f562f` | Deterministic typed-JSON SHA-256, projection and negative tests; limitations documented below. |
| `rust-harness/src/wasm.rs` | REUSE | `99b194606559ab05bd78bfb2701452748a562aa4` | Transport-free WASM functions share native Rust receipt builder. |
| `tools/pybundle/watersheep_bundle.py` | REFACTOR | `492cf0e9f4edec804356097894c1cdef7069f73b` | Replace upstream root/module expectations, genericize smoke/launch and tighten test-only overrides. |

### Outside-PR inputs and licensing

- **Keep existing target `LICENSE` unchanged.** Its Git blob SHA-1 `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64` matches the source's Apache License 2.0 file.
- **Create a targeted standalone `NOTICE`.** Source `NOTICE` at commit `cdce968a7ed7c6a4f4f983c07438a49702157000` (Git blob `710b362e15f9abe2bb613c23fb47e8f2e297efc2`) identifies WaterSheep and `Copyright 2026 Samrat Dutta`, but also discusses base-model weights and numerous datasets that the harness must not bundle. Preserve applicable upstream notices and do not suggest the standalone code is solely original work. A human should review notice selection before public release.
- Add `PROVENANCE.md` identifying the upstream author/project, fork PR, pinned commit, copied/refactored file mapping, license, no original model assets, and any modifications; retain source and derivative history as file-level ledger, **not** a silent new provenance claim.
- **Exclude all `kol-watersheep/**` content.** Exclusion applies to implementation, configuration, tests, prompts, schemas, data and fixtures. The excluded *path metadata* above exists only to make the extraction auditable; no excluded file contents are in this report or artifacts.
- Exclude the rest of the original source monorepo (inference/training package `watersheep/**`, Hugging Face handlers, model weights/data, benchmark results/figures, unrelated scripts and tools). The standalone may communicate with the independent WaterSheep server but must not vendor its runtime.

## Missing or separate build requirements

| Area | Source dependency / state | Standalone requirement |
| --- | --- | --- |
| Rust native | Edition 2021; `serde`, `serde_json`, `sha2`, `hex`, `thiserror`; optional `clap`, `reqwest` + `rustls`, `tokio` | Rust stable, Cargo, rustfmt, clippy; compile default `native,typescript` features |
| WASM | Optional `wasm-bindgen = 0.2`; `wasm32-unknown-unknown`; no native HTTP | `rustup target add wasm32-unknown-unknown`; matching `wasm-bindgen-cli`; generate `.wasm` and JS package; browser/Node import + runtime parity tests |
| TypeScript | Optional `ts-rs = 12.0` with `serde-json-impl`; `ts(export)` | Explicit export destination and `tsc --noEmit` validation; check bindings generated from pinned version |
| Go supervisor | `go 1.22`, Go standard library only | Go >= 1.22; rename module/import and status field. No `go.sum` needed for current stdlib-only module |
| Python smoke | Python 3 stdlib, fake HTTP server; tests build Go + Rust | Python >= 3.10; synthetic fixtures; run both `--smoke` and `--smoke --dev` |
| Reproducibility | **No `Cargo.lock` in PR**, no checked-in golden response/receipt vector, no packaged JS/TS build output | Pin dependencies/tool versions; retain native golden fixtures and exact expected digests; verify lockfile policy |
| Inference | WaterSheep external API server at `/v1/systemone`; default upstream 127.0.0.1:8766 | Optional *external* runtime for live integration only; fake server must cover offline CI without weights/model downloads |

The source CI at [https://github.com/es-3581100/WaterSheep/actions/runs/42340061172](https://github.com/es-3581100/WaterSheep/actions/runs/42340061172) **passed** against the exact pinned head on 2026-11-07: Rust fmt/clippy/tests, Go fmt/vet/tests, fake-model end-to-end smoke in dev mode, and `cargo check` for wasm32. It does **not** run `wasm-bindgen` glue generation, a browser runtime import, TypeScript `tsc` validation, standalone layout, independent golden SHA-256 vectors, or a real external inference integration.

### Risks requiring explicit review before calling it verified

1. **Semantic vs wire digests:** serialized typed JSON may discard unknown input fields and materialize defaults, so two distinct raw payloads can share a receipt digest. Preserve current behavior initially for compatibility, but label hash semantics in `PROVENANCE.md`; add adversarial examples. Consider strict unknown-field rejection or separately computed wire-body hashes only under a deliberate contract-version change.
2. **Correlation gap:** the code compares answer-name sets, not an immutable request ID or nonce; crossed responses with identical question names can pass validation. No production evidence chain should claim perfect request/response binding without an external correlation proof or versioned envelope change.
3. **Raw output approval inconsistency:** the Go debug path requires `--dev` plus a fixed approval header, but the Rust CLI `ask --response-out FILE` writes raw model responses with no explicit per-call approval. Reconcile the intended policy before shipping. Static headers also do not prove human identity/consent and must not be represented as authentication.
4. **Go local trust assumptions:** `waitReady` accepts TCP reachability (a stale/unrelated process could be mistaken for healthy), configurable listeners could expose debug endpoints, and `WATERSHEEP_SMOKE=1` enables arbitrary child command overrides. Constrain the supervisor to trusted local development and test these failure modes.
5. **Authority boundary is a contract, not a sandbox:** `authority: evidence-only` and Go `observation-only` are metadata. A downstream consumer must separately refuse executable actions based on predictions or debug responses; no such consumer enforcement exists in the 27-file PR.
6. **Schema/runtime parity:** the JSON Schema disallows extra receipt properties; Rust deserialization does not explicitly use `deny_unknown_fields` on request/response objects. Add strict negative tests to establish intended rules, while preserving v1 compatibility where required.

## Proposed standalone filesystem layout

```text
watersheep-rust-wasm-harness/
├── LICENSE                       # retain existing target Apache-2.0 verbatim
├── NOTICE                        # applicable upstream notices, reviewed
├── README.md                     # standalone domain-neutral contract
├── PROVENANCE.md                 # pinned source + modifications ledger
├── .gitignore                    # generated artifacts, no secrets or model files
├── .github/workflows/verify.yml # adapted Rust/Go/Python/WASM/TS gates
├── rust-harness/
│   ├── Cargo.toml
│   ├── Cargo.lock                 # generated and retained for CLI/reproducibility
│   ├── src/{lib.rs,contracts.rs,receipt.rs,client.rs,wasm.rs}
│   ├── src/bin/watersheep-harness.rs
│   ├── schema/watersheep-harness-receipt-v1.schema.json
│   ├── examples/request.json
│   └── bindings/                 # controlled ts-rs output; generated
├── go-bridge/
│   ├── go.mod
│   ├── README.md
│   ├── cmd/watersheep-supervisor/main.go
│   └── internal/supervisor/{supervisor.go,supervisor_test.go}
├── fixtures/v1/
│   ├── request.json              # new domain-neutral deterministic input
│   ├── response.json             # new synthetic response, no live inference
│   ├── receipt.golden.json       # verified native canonical receipt
│   └── sha256.expected.json      # independent expected semantic hashes
├── tools/smoke.py                # adapted pybundle smoke, no inference dependency
├── tests/                        # contract, schema, WASM parity, TS, debug gates
└── reports/
    ├── extraction-report.md      # this report, after explicit placement
    ├── extraction-manifest.v1.json
    └── SHA256SUMS
```

Retain `rust-harness/` and `go-bridge/` paths on first pass to minimize behavioral changes. Avoid bundling WaterSheep's Python model, weights, training environment or integration subtree. A WaterSheep-specific endpoint and naming are acceptable; **application-domain-specific adapters, prompts and data are not**.

## Verification plan and acceptance criteria

**Phase A — provenance and boundary (all required).** Freeze the PR HEAD and blob IDs listed in the JSON manifest. Verify each candidate source Git blob against pin, license/NOTICE and derivative mapping. Enumerate all copied output files (explicit allowlist) and fail CI on unexpected files, forbidden domain references, assets, prompts, data, model weights, symlinks or dependencies. Scan runtime/docs/tests/fixtures; do not misinterpret the excluded-path *audit metadata* in `reports/` as copied code. Confirm source repo and PR unchanged; no merge, commit, push or publish.

**Phase B — native correctness (all required).** `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, `cargo test` with default features, `go test ./...`, `go vet ./...`, `gofmt -l`, plus schema validation for every golden receipt. Test `noul/choice/score/multi`, optional values, legends, truncation, in-band error, zero usage, invalid probabilities and thresholds, empty names/instructions, wrong answer-name set, and mutation of any hashed semantic input. Persist an independently obtained SHA-256 golden vector (do **not** invent digest constants in audit).

**Phase C — deterministic parity (all required).** Verify identical typed-JSON receipt and both SHA-256 digests under request/response object-key reordering, stable over repeated runs and across CLI `project`, native library, and actual WASM JavaScript invocation. Verify array reordering and semantic content changes change the relevant digest. Document and test unknown-field/default-number behavior. Check JSON Schema conformance and `tsc --noEmit` against generated TypeScript declarations. Pin the WASM glue generation version and exercise actual `wasm-bindgen --target web`, not only `cargo check`.

**Phase D — process and authority (all required).** Run fake-model Go supervisor smoke with and without `--dev`; assert normal proxy and observable status, direct debug denied without consent, no debug in production mode, no arbitrary external child command outside controlled tests, safe child shutdown, startup failure behavior and loopback binding. Reconcile Rust `--response-out` with approval policy. Test that downstream mock consumer **cannot transform either model receipt or raw debug output into an authorized action**. A receipt is observational evidence only.

**Phase E — release decision.** Extraction is acceptable only after all phases pass in the *standalone* checkout, with actual file hashes, tool versions, test logs and a canonical artifact SHA-256 recorded. Until then label `AUDIT_ONLY / NOT_EXTRACTED / NOT_STANDALONE_VERIFIED`. No changes to source PR/repository at any point.

## Audit evidence and limitations

- Directly inspected pinned source code, Rust contracts, hashing/projection, native/WASM layer, Cargo metadata, JSON Schema, TypeScript derives, Go supervisor/Go unit tests, Python smoke, CI workflow, source Apache license and source NOTICE via the GitHub connector. Excluded subtree contents were deliberately not copied.
- GitHub confirmed **27 PR files**, exact SHA-1 Git blob IDs and upstream CI success at the pinned head. Target remote `main` contained only the matching LICENSE at inspection time.
- Local source/target workspaces are **not mounted here**. Rust/Cargo is unavailable in this execution container. **No local Rust or Go source tests were executed**; upstream CI evidence is not independent standalone verification. The canonical audit and JSON manifest are produced in the conversation's downloadable working directory, **not in the target workspace**.
- The manifest's SHA-256 and this report's SHA-256 are computed over the exact UTF-8 bytes of the generated files and recorded in the accompanying `SHA256SUMS` file. These hashes attest to audit artifacts only, **not** the source tree or executable behavior.
