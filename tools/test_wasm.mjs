// Run after wasm-bindgen --target nodejs (no external runtime or network).
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';

const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const require=createRequire(import.meta.url);
const wasm=require(join(root,'rust-harness/pkg-node/watersheep_harness.js'));
const request=readFileSync(join(root,'fixtures/v1/request.json'),'utf8');
const response=readFileSync(join(root,'fixtures/v1/response.json'),'utf8');
const expected=JSON.parse(readFileSync(join(root,'fixtures/v1/receipt.golden.json'),'utf8'));
const endpoint='offline://watersheep/v1/systemone';
assert.equal(wasm.validate_request_json(request),'ok:5');
const one=JSON.parse(wasm.project_receipt(request,response,endpoint));
const two=JSON.parse(wasm.project_receipt(request,response,endpoint));
assert.deepEqual(one,two);
assert.deepEqual(one,expected,'WASM disagrees with pinned golden receipt');
assert.equal(one.request_sha256, expected.request_sha256);
assert.equal(one.response_sha256,expected.response_sha256);
assert.throws(()=>wasm.validate_request_json('{"questions":{}}'));
assert.throws(()=>wasm.project_receipt(request,'{"answers":{},"model":"wrong"}',endpoint));
// Native binary execution is mandatory: golden agreement alone is insufficient.
const native=spawnSync('cargo',['run','--quiet','--manifest-path',join(root,'rust-harness/Cargo.toml'),
  '--','project','--request',join(root,'fixtures/v1/request.json'),'--response',join(root,'fixtures/v1/response.json'),
  '--endpoint',endpoint],{encoding:'utf8'});
if(native.status!==0)throw new Error('Native project failed: '+native.stderr);
const parsed=JSON.parse(native.stdout);
assert.deepEqual(parsed,one,'WASM/native complete receipt mismatch');
assert.equal(parsed.request_sha256,one.request_sha256);
assert.equal(parsed.response_sha256,one.response_sha256);
console.log('WASM_NATIVE_EQUIVALENCE_PASS (complete receipt, both SHA-256, invalid input)');
