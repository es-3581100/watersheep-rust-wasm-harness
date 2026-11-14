#!/usr/bin/env python3
"""Find exactly one wasm-bindgen crate version in Cargo.lock (TOML, stdlib)."""
import sys
import tomllib
from pathlib import Path
p=Path(sys.argv[1])
if not p.exists():raise SystemExit('BLOCKED: Cargo.lock missing')
rows=[x['version'] for x in tomllib.loads(p.read_text())['package'] if x['name']=='wasm-bindgen']
if len(set(rows))!=1:raise SystemExit('BLOCKED: expected one wasm-bindgen crate version')
print(rows[0])
