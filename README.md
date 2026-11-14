# WaterSheep Rust/WASM Evidence Harness (standalone)

A **domain-neutral, separately buildable, evidence-only** adapter for the
WaterSheep-compatible `POST /v1/systemone` JSON interface. This is an
**independently maintained derivative** of Rust and Go code in
[WaterSheep PR #2](https://github.com/es-3581100/WaterSheep/pull/2), pinned at
`cdce968a7ed7c6a4f4f983c07438a49702157000`. It is **not an official
WaterSheep release** and is **not endorsed** by the upstream maintainers.

The harness is **not** an inference runtime: install/run WaterSheep separately
for online inference. Offline tests use a synthetic HTTP backend; no model
weights, downloads, credentials or external services are required.

## Architecture and authority

```text
separate inference process  <-- Go supervisor (optional, loopback only)
   POST /v1/systemone         | status, bounded logs, child lifecycle
             ^                | debugging (dev-mode + operation-specific approval)
             | HTTP           v
   Rust CLI/HTTP client --> Rust typed contracts + validation + evidence receipts
                                        |                 |
                                        v                 v
                                  TypeScript            WASM projector
                                  declarations          (NO network/I/O)
                                        \                /
                                     read-only consumers
                               (NEVER execution authorization)
```

The unchanged Rust receipt core emits `watersheep.harness.receipt/v1`,
`producer=watersheep-rust-harness`, `authority=evidence-only`, ordered decisions,
usage, and canonical typed-JSON request/response SHA-256. All four question
kinds (`noul`, `choice`, `score`, `multi`) are supported. Confidence, score
legends, truncation and error flags survive projection. Response answer names
must match request question names.

**Important semantics:** these SHA-256 digests are computed after deserializing
into Rust structs and serializing canonical key-sorted JSON. They are **not
raw-wire HTTP checksums**, nor an RFC-8785 guarantee. Unknown input JSON fields
may be omitted and default fields materialized. Equal question-name sets do not
prove a response belongs to a particular request; request correlation belongs
to the caller. Evidence metadata is not a sandbox or policy enforcement engine.

## Native Rust

Requires Rust 1.93.1 or newer (edition 2021), Cargo, and the dependencies in
`rust-harness/Cargo.toml`. The standalone Rust binary lives under
`rust-harness/`, maintaining the original crate identity.

```bash
cargo test --manifest-path rust-harness/Cargo.toml
cargo run --manifest-path rust-harness/Cargo.toml -- \
  validate --request fixtures/v1/request.json
cargo run --manifest-path rust-harness/Cargo.toml -- \
  project --request fixtures/v1/request.json --response fixtures/v1/response.json \
  --endpoint offline://watersheep/v1/systemone
```

For online use, start a separately installed WaterSheep server (default
`http://127.0.0.1:8766`) and run:

```bash
cargo run --manifest-path rust-harness/Cargo.toml -- \
  ask --base-url http://127.0.0.1:8766 --request rust-harness/examples/request.json
```

Normal inference does not need debug approval. A raw response file via
`ask --response-out ...` requires **both** `--dev` and
`--approve-readonly-response-out` on that call; it is observation only.
Neither approval nor any receipt grants permission to execute actions.

## WASM & JavaScript

Requires `rustup target add wasm32-unknown-unknown` and a
`wasm-bindgen-cli` version **identical to the `wasm-bindgen` crate resolved in
Cargo.lock** (see `tools/resolve_bindgen_version.py`). Build without native
transport:

```bash
cargo build --manifest-path rust-harness/Cargo.toml --release \
  --target wasm32-unknown-unknown --no-default-features --features wasm
wasm-bindgen --target web --out-dir rust-harness/pkg-web \
  rust-harness/target/wasm32-unknown-unknown/release/watersheep_harness.wasm
wasm-bindgen --target nodejs --out-dir rust-harness/pkg-node \
  rust-harness/target/wasm32-unknown-unknown/release/watersheep_harness.wasm
node tools/test_wasm.mjs
```

Browser ES module import and asynchronous initialization:

```js
import init, { validate_request_json, project_receipt } from './pkg-web/watersheep_harness.js';
await init();
const valid = validate_request_json(JSON.stringify(request));
const receiptJSON = project_receipt(JSON.stringify(request), JSON.stringify(response),
  'offline://watersheep/v1/systemone');
```

WASM has **no HTTP client** or execution authority; the host supplies captured
JSON. `tools/test_wasm.mjs` verifies actual Node runtime loading, validation,
invalid-input rejection, and complete receipt + both digest equivalence against
native Rust and checked-in fixture. The browser package is generated, not
committed. Use a static server with the correct WASM MIME type to run in browsers.

## TypeScript contracts (Rust-owned)

The nine exported Rust contract types use `ts-rs` derivation under the
`typescript` feature. Run `bash tools/check_ts.sh`: it regenerates
`rust-harness/bindings/*.ts` via `cargo test`, confirms each expected type,
compiles all declarations with `tsc --noEmit` and repeats generation to detect
drift. Generated bindings are **not committed**; build them during development
or packaging, never maintain separate hand-edited declarations. Requires `tsc`
(TypeScript 5.9.3 is pinned in CI).

## Optional Go supervisor

Go >=1.22; standard library only. The supervisor launches a separately
installed WaterSheep Python service by default; `--upstream` controls the
compatible upstream URL. It forwards normal inference unchanged and reports
observation-only lifecycle status through `GET /v1/status`.

```bash
cd go-bridge
go test ./... && go test -race ./...
go run ./cmd/watersheep-supervisor serve
```

The listener rejects non-loopback addresses, including `0.0.0.0`; there is
**no network authentication**. Do not put the local port behind a proxy or
forward it to untrusted clients. Dev mode is off by default.
Debug direct outputs require `--dev` **and**
`debug-ask --approve-readonly-direct-output`; debug logs require `--dev` **and**
`debug-logs --approve-readonly-logs`. Both operations carry different approval
header phrases. These phrases are scoped **intent flags**, **not identity
proof** or authorization tokens. Raw model content may contain untrusted text.
Status and debug outputs are observation only, never instructions to execute.

Startup defaults to TCP reachability only; this does **not** prove that the
listening process is the correct runtime. Optional `--readiness-request FILE`
probes `/v1/systemone` with the supplied JSON and checks the response shape,
but **may consume inference**. The offline smoke enables this probe. A malicious
local process can still spoof readiness; isolate the service in a trusted
execution environment where needed.

## Offline verification

```bash
python3 tools/smoke.py --smoke      # Go child, normal inference, deny debug
python3 tools/smoke.py --smoke --dev # explicitly scoped read-only debug test
bash tools/verify_all.sh           # full Rust + Go + WASM + Node + TS suite
```

Both smoke modes require Go, Python >=3.10, and Cargo for **full** acceptance.
`--skip-rust` is diagnostic-only and cannot establish standalone readiness.
The upstream pinned-version oracle must be checked **separately**, once during
extraction, using `bash tools/verify_source_oracle.sh /path/to/WaterSheep`.
That script builds code exported from the exact Git commit into a temporary
directory and does **not modify the source working tree**. It verifies all
27 source Git blobs and matches source and standalone receipts to the golden.

## Packaging & provenance

See [PROVENANCE.md](PROVENANCE.md),
[NOTICE](NOTICE), and [reports/extraction-manifest.v1.json](reports/extraction-manifest.v1.json).
Apache-2.0 license. See the verification report for extraction and local
integration evidence.

**Review status:** See `reports/standalone-extraction-verification.md` for
verified checks and remaining review conditions.
