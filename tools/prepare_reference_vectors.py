#!/usr/bin/env python3
"""INDEPENDENT PROVISIONAL vector reference, not a Rust golden oracle.

Makes vectors deterministic for review; final release requires comparison against
pinned upstream native Rust using tools/verify_source_oracle.sh.
"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
folder = root / 'fixtures/v1'
request = json.loads((folder/'request.json').read_text())
response = json.loads((folder/'response.json').read_text())

# Mirror deserializing through the exact upstream typed structs; this is an
# independent reimplementation only for carefully chosen ASCII fixture types.
def normalize_request(inp):
    out = {'state':inp.get('state'), 'questions':{}}
    for k, q in sorted(inp['questions'].items()):
        item = {'type':q['type'], 'instructions':q['instructions']}
        for key in ('criteria', 'threshold'):
            if q.get(key) is not None:
                item[key] = q[key]
        out['questions'][k] = item
    return out

def normalize_response(inp):
    out = {'model':inp['model'], 'answers':{},
           'usage':{'input_tokens':inp.get('usage',{}).get('input_tokens',0),
                    'output_tokens':inp.get('usage',{}).get('output_tokens',0)}}
    for k,a in sorted(inp['answers'].items()):
        item={'type':a['type']}
        for key in ('noul','choice','score','confidence','truncated','error'):
            if key in a and a[key] is not None:
                item[key]=a[key]
        for key in ('choices','probabilities','legend'):
            if key in a and a[key]:
                item[key]=a[key]
        out['answers'][k]=item
    return out

def hash_typed(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

req=normalize_request(request)
resp=normalize_response(response)
decisions=[]
for name,a in sorted(resp['answers'].items()):
    kind=a['type']; err=a.get('error')
    probs=dict(a.get('probabilities',{}))
    selected=[];scalar=None;confidence=a.get('confidence')
    if not err:
        if kind=='noul':
            p=a['noul'];probs.update(yes=p,no=1-p)
            selected=['yes' if p>=0.5 else 'no'];scalar=p;confidence=max(p,1-p)
        if kind=='choice':selected=[a['choice']]
        if kind=='score':scalar=a['score']
        if kind=='multi':selected=a.get('choices',[])
    decision={'name':name,'decision_type':kind,'status':'error' if err else 'ok'}
    if selected:decision['selected']=selected
    if scalar is not None:decision['scalar']=scalar
    if confidence is not None:decision['confidence']=confidence
    if probs:decision['probabilities']=dict(sorted(probs.items()))
    if a.get('legend'):decision['legend']=dict(sorted(a['legend'].items()))
    if a.get('truncated') is not None:decision['truncated']=a['truncated']
    if err is not None:decision['error']=err
    decisions.append(decision)

receipt={'schema':'watersheep.harness.receipt/v1','producer':'watersheep-rust-harness',
         'authority':'evidence-only','endpoint':'offline://watersheep/v1/systemone',
         'request_sha256':hash_typed(req),'response_sha256':hash_typed(resp),
         'model':resp['model'],'usage':resp['usage'],'decisions':decisions}
(folder/'receipt.golden.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
(folder/'sha256.expected.json').write_text(json.dumps({'status':'PROVISIONAL_PYTHON_REFERENCE_NOT_UPSTREAM_RUST_VERIFIED',
    'request_sha256':receipt['request_sha256'], 'response_sha256':receipt['response_sha256']},indent=2)+'\n')
print('request_sha256:',receipt['request_sha256'])
print('response_sha256:',receipt['response_sha256'])
print('status: PROVISIONAL; upstream Rust oracle required')
