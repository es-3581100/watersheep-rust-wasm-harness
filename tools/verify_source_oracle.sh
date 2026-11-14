#!/usr/bin/env bash
# Read-only upstream build: NEVER checkout, fetch or mutate source repository.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="${1:?Usage: verify_source_oracle.sh /path/to/source-checkout}"
PIN='cdce968a7ed7c6a4f4f983c07438a49702157000'
[[ -d "$SOURCE/.git" ]] || { echo "BLOCKED: no local source .git at $SOURCE" >&2; exit 2; }
[[ "$(git -C "$SOURCE" rev-parse --verify "${PIN}^{commit}")" == "$PIN" ]] || { echo "BLOCKED: pinned commit absent" >&2; exit 2; }
python3 - "$ROOT/reports/extraction-manifest.v1.json" "$SOURCE" "$PIN" <<'PY'
import json, subprocess, sys
manifest=json.load(open(sys.argv[1]))
for ent in manifest['files']:
    path=ent['path']
    got=subprocess.check_output(['git','-C',sys.argv[2],'rev-parse',f'{sys.argv[3]}:{path}'],text=True).strip()
    want=ent['source_git_blob_sha1']
    if got != want:raise SystemExit(f'BLOB MISMATCH: {path} got {got} expected {want}')
print(f'PINNED_GIT_BLOBS_OK: {len(manifest["files"])}')
PY
command -v cargo >/dev/null || { echo 'BLOCKED: Cargo unavailable' >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# Archive selected source subtree into disposable temp directory, not source working tree.
git -C "$SOURCE" archive "$PIN" rust-harness | tar -x -C "$TMP"
export CARGO_TARGET_DIR="$TMP/target"
REQ="$ROOT/fixtures/v1/request.json"
RESP="$ROOT/fixtures/v1/response.json"
ENDPOINT='offline://watersheep/v1/systemone'
cargo run --quiet --manifest-path "$TMP/rust-harness/Cargo.toml" -- project --request "$REQ" --response "$RESP" --endpoint "$ENDPOINT" --out "$TMP/source-receipt.json"
cargo run --quiet --manifest-path "$ROOT/rust-harness/Cargo.toml" -- project --request "$REQ" --response "$RESP" --endpoint "$ENDPOINT" --out "$TMP/standalone-receipt.json"
python3 - "$TMP/source-receipt.json" "$TMP/standalone-receipt.json" "$ROOT/fixtures/v1/receipt.golden.json" <<'PY'
import json, pathlib, sys
source,standalone,golden=[json.loads(pathlib.Path(x).read_text()) for x in sys.argv[1:]]
assert source==standalone, 'Native source / standalone receipt mismatch'
assert source==golden, 'Native source / checked-in golden mismatch'
assert source['authority']=='evidence-only'
assert source['schema']=='watersheep.harness.receipt/v1'
print('SOURCE_ORACLE_PASS source == standalone == checked-in expected; both hashes equal')
print('request_sha256',source['request_sha256'])
print('response_sha256',source['response_sha256'])
PY
