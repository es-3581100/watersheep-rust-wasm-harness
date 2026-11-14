#!/usr/bin/env python3
"""Fail closed on disallowed app integration files and named-domain tokens.

Audit-only reports are permitted to name excluded source paths; distributable
code, fixtures, and CI must not import application-domain implementation.
"""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
# Construct exclusion markers from ASCII hex so no domain-specific fixtures,
# labels or messages are bundled into runtime code as literal strings.
forbidden=[bytes.fromhex(x).decode().lower() for x in ('6b6f6c2d77617465727368656570','6b6f6c6d61666961','6b6f6c737461636b')]
issues=[]
for p in root.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ('.dev','target','pkg-web','pkg-node','.git','bindings','reports','__pycache__')):
        continue
    if p.suffix not in ('.py','.rs','.go','.sh','.yml','.yaml','.json','.js','.mjs','.md','.toml'):
        continue
    text=p.read_text(encoding='utf8').lower()
    if any(x in text for x in forbidden):issues.append(str(p.relative_to(root)))
if issues:
    print('DOMAIN_BOUNDARY_FAIL:',issues,file=sys.stderr)
    raise SystemExit(1)
print('DOMAIN_BOUNDARY_PASS (runtime/docs/fixtures/tool source; audit files excluded)')
