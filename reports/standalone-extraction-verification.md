# Standalone extraction verification

**Decision: `READY_FOR_PUBLIC_REVIEW`** — local verification passed; GitHub-hosted CI has not yet run on this branch. This is review readiness, not release approval.

## Git and archive

- Target origin: `https://github.com/es-3581100/watersheep-rust-wasm-harness.git`.
- Branch: `feature/standalone-evidence-harness`, created from clean `main` at `492b9c833f22feacd63f42a6c0e087b4e2fa5a57`. All integration changes are uncommitted; no push, merge, tag, or release.
- The original Apache-2.0 `LICENSE` was preserved unchanged: Git blob `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`, also matching the pinned source license. The archive license contains an extra initial newline and was not transferred.
- Download: `watersheep-rust-wasm-harness-staging.zip`; SHA-256 `1b557da22bcc0c36db4cc952db26744f8c946409fd384f61f9b950dc0d7aefa8`. The only downloaded ZIP containing the expected report was selected by its exact report digest.
- Original staged report SHA-256: `fefbec0efcd47bba8143881e73ea430ef8e63cf6755c8f4cfea33f589ce34794`. The staged sidecar and every entry in `reports/staging-SHA256SUMS.txt` were verified before integration. Those records describe the archived staging artifact, not the subsequently modified checkout.
- Staging manifest SHA-256: `f48bef3a122cdcd88fbc55d47d46c1b4712d3dd4f10bc85701f6783f331b42bf`. Staging audit SHA-256: `c170e8692f050cbf1468927c1e7bbe367cd0659b0a031551d351e1619104ebc9`. Manifest JSON passed duplicate-key and shape validation.
- All 50 ZIP entries were checked for absolute/traversal paths, duplicate paths, non-regular special files and symlinks; no unsafe entries were found. Extraction used a fresh directory under the requested staging cache. No source checkout files were modified.

## Provenance and boundaries

- Pinned source commit: `cdce968a7ed7c6a4f4f983c07438a49702157000`. All 27 source Git blob IDs match the manifest locally; all 17 admitted staging destination SHA-256 values matched before integration. Six unchanged source files match their Git blobs byte-for-byte; 11 refactored files were compared against the pinned originals. All 10 excluded source paths were absent.
- `PROVENANCE.md` and `reports/extraction-manifest.v1.json` document every source path, relocation, original blob, staging destination hash, classification, and refactoring rationale. Apache-2.0 attribution is retained in `NOTICE`. The manifest and original staging checksums are historical evidence and do not assert current hashes after integration edits.
- Integration edits: format the Rust CLI and golden tests; add `Cargo.lock`; pin the CI Rust version and select an isolated Python setup; require an explicit source path for the optional source-oracle tool; update standalone documentation and provenance; remove the staging-only installer and stale report generator; and extend the synthetic smoke with CLI raw-export approval tests.
- The entire extracted text was scanned for application-specific markers. Matches were limited to historical audit, manifest and original report entries naming excluded paths; no such implementation, dependency, or fixture was admitted. Runtime and CI paths use the standalone layout. Historical provenance URLs and audit metadata intentionally identify the source.
- Receipts retain `watersheep.harness.receipt/v1` and `authority: evidence-only`. Supervisor status and debug metadata are `observation-only`; supervisor starts and monitors an explicitly configured inference child, but neither receipt nor debug approval is an action-execution grant. Debug approval phrases are scoped intent signals, not authentication.

## Verification

| Check | Result |
|---|---|
| `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, `cargo test` | PASS; Rust 1.93.1, 14 library tests and 4 golden tests. Initial staging formatting failed and was corrected. |
| Resolved `rust-harness/Cargo.lock` | PASS; SHA-256 `bce360886d5da5de9699bb004f615b50b396547065ec7d0c2057634e7c69f4ff`; offline locked WASM build succeeded. |
| Pinned native source oracle | PASS; all source blob IDs checked and complete parsed source, standalone, and golden receipt JSON compared equal. The source was exported from Git into a temporary build directory. |
| WASM build and runtime | PASS; Rust 1.93.1 `wasm32-unknown-unknown`, `wasm-bindgen` 0.2.127, Node 22.22.1: actual module initialization, valid request validation, projection, repeated complete receipt equality with native and golden, both hash comparisons, and invalid-input rejection. Web and Node bindings generated. |
| TypeScript | PASS; `ts-rs` generated nine declarations; TypeScript 5.9.3 compiled them, and two independent generations matched. Generated declarations are ignored, so this checks repeat-generation drift rather than comparison with a committed baseline. |
| Go | PASS; `gofmt`, `go vet`, unit and race tests; tested Go 1.26.8 and CI-compatible 1.23.12. Both standard and dev fixture-smoke modes passed with actual Rust receipt generation and Go 1.23.12. |
| Approval and authority | PASS; Go tests and fixture smoke reject missing, wrong-operation and non-dev debug approval. Rust smoke rejects missing or partial raw-export flags before file writes and permits output only with both flags; resulting receipt remains evidence-only. |
| Static/schema | PASS; six Python tests, including schema authority rejection and domain boundary. |
| CI readiness | PASS locally: workflow parsed and `actionlint` 1.7.7 passed; complete `tools/verify_all.sh` passed in the standalone layout using Rust 1.93.1, Node 22, TypeScript 5.9.3 and installed JSON Schema validator. Workflow pins Rust 1.93.1, Go 1.23.x, Node 22, Python 3.12, TypeScript 5.9.3, JSON Schema 4.25.1, and resolves the bindgen CLI version from the lockfile. GitHub-hosted execution remains unobserved. |

The full verification script passed before the additional raw-export smoke assertions; both smoke modes were rerun successfully afterwards with those assertions. The standalone source-oracle tool was also rerun against the integrated checkout.

### Golden SHA-256 values

- Request: `9a408cdce23b45bc8e32f8cff4b673b9fae98559ed79d71a8bcc18f546d6e6e9`.
- Response: `89f796f1d12b472d935a23d2086198440c4424e44af79504c35ccf3c2cbd1f09`.

These are SHA-256 hashes of normalized typed JSON, not raw HTTP bytes or a request-response authentication mechanism. Equivalence is established for the supplied vector and tested invalid cases, not every possible input.

## Remaining review conditions

- GitHub-hosted CI has not executed; Python 3.12 and JSON Schema 4.25.1 are workflow pins, whereas the local full run used Python 3.14 and JSON Schema 4.19.2. Review the first hosted run before treating CI as independently confirmed.
- TCP-only readiness is weaker than the optional application probe. Debug approval headers are not authentication. The separate inference runtime is not included or tested against a real model.
- Source and target history are preserved; the feature branch has no new commit. Any commit or publication requires separate authorization.

## Report checksum

`reports/standalone-extraction-verification.md.sha256` contains the SHA-256 of this exact file. A file cannot contain its own stable SHA-256 without changing its bytes.
