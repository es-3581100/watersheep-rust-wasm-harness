#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRATE="$ROOT/rust-harness"
command -v cargo >/dev/null || { echo 'Cargo required for TypeScript generation' >&2;exit 2; }
command -v tsc >/dev/null || { echo 'TypeScript tsc required' >&2;exit 2; }
# ts-rs generates declarations from Rust, not a separately edited TS schema.
rm -rf "$CRATE/bindings"
(cd "$CRATE" && cargo test --features typescript)
for type in QuestionType QuestionSpec SystemOneRequest Usage Answer SystemOneResponse Authority MatrixDecision HarnessReceipt; do
  test -s "$CRATE/bindings/$type.ts" || { echo "Missing Rust-generated $type.ts" >&2;exit 1; }
done
# Compile type declarations directly (all imports stay inside bindings/).
(cd "$CRATE" && tsc --noEmit --strict --skipLibCheck --target ES2020 --module ESNext --moduleResolution bundler bindings/*.ts)
A="$(mktemp -d)";trap 'rm -rf "$A"' EXIT
cp -a "$CRATE/bindings/." "$A/"
rm -rf "$CRATE/bindings"
(cd "$CRATE" && cargo test --features typescript)
diff -ru "$A" "$CRATE/bindings"
echo 'TYPESCRIPT_BINDINGS_GENERATION_AND_DRIFT_PASS'
