#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 tools/check_boundary.py
command -v cargo >/dev/null || { echo 'BLOCKED: Rust/Cargo missing; cannot grant release acceptance' >&2;exit 2; }
command -v rustup >/dev/null || { echo 'BLOCKED: rustup missing' >&2;exit 2; }
command -v wasm-bindgen >/dev/null || { echo 'BLOCKED: wasm-bindgen-cli missing' >&2;exit 2; }
command -v node >/dev/null || { echo 'BLOCKED: Node missing' >&2;exit 2; }
(cd rust-harness && cargo fmt --check && cargo clippy --all-targets -- -D warnings && cargo test)
(cd go-bridge && test -z "$(gofmt -l .)" && go vet ./... && go test ./... && go test -race ./...)
python3 tools/smoke.py --smoke
python3 tools/smoke.py --smoke --dev
(cd rust-harness && cargo build --release --target wasm32-unknown-unknown --no-default-features --features wasm)
mkdir -p rust-harness/pkg-node rust-harness/pkg-web
wasm-bindgen --target nodejs --out-dir rust-harness/pkg-node rust-harness/target/wasm32-unknown-unknown/release/watersheep_harness.wasm
wasm-bindgen --target web --out-dir rust-harness/pkg-web rust-harness/target/wasm32-unknown-unknown/release/watersheep_harness.wasm
node tools/test_wasm.mjs
bash tools/check_ts.sh
python3 -m unittest discover -s tests -v
echo 'STANDALONE_CHECKS_PASS; source-oracle comparison is a SEPARATE mandatory gate'
