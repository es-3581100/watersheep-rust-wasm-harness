import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'fixtures/v1'

class StandaloneStaticTests(unittest.TestCase):
    def test_manifest_complete_and_source_pinned(self):
        data=json.loads((ROOT/'reports/extraction-manifest.v1.json').read_text())
        self.assertEqual(len(data['files']),27)
        self.assertEqual(data['source']['head_sha'],'cdce968a7ed7c6a4f4f983c07438a49702157000')
        self.assertEqual(data['source']['base_sha'],'aa308f7778a06bad77c1adb3e3109e27bed03736')
        for item in data['files']:
            self.assertRegex(item['source_git_blob_sha1'],r'^[a-f0-9]{40}$')
            path=item['path']
            if item['classification']=='exclude':
                self.assertFalse((ROOT/path).exists(),f'prohibited transferred path {path}')

    def test_source_exact_bytes(self):
        m=json.loads((ROOT/'reports/extraction-manifest.v1.json').read_text())
        for e in m['files']:
            if e['classification'] != 'unchanged':continue
            path=ROOT/e['destination_path']
            self.assertTrue(path.is_file(),str(path))
            got=subprocess.check_output(['git','hash-object',str(path)],text=True).strip()
            self.assertEqual(got,e['source_git_blob_sha1'],str(path))

    def test_fixture_consistency_and_hash_format(self):
        req=json.loads((FIX/'request.json').read_text())
        resp=json.loads((FIX/'response.json').read_text())
        receipt=json.loads((FIX/'receipt.golden.json').read_text())
        self.assertEqual(set(req['questions']),set(resp['answers']))
        self.assertEqual({x['name'] for x in receipt['decisions']},set(req['questions']))
        self.assertEqual(receipt['authority'],'evidence-only')
        self.assertEqual(receipt['schema'],'watersheep.harness.receipt/v1')
        for k in ('request_sha256','response_sha256'):
            self.assertRegex(receipt[k],r'^[0-9a-f]{64}$')

    def test_schema_validation(self):
        import jsonschema
        schema=json.loads((ROOT/'rust-harness/schema/watersheep-harness-receipt-v1.schema.json').read_text())
        receipt=json.loads((FIX/'receipt.golden.json').read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(receipt,schema)
        receipt['authority']='execute'
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(receipt,schema)

    def test_no_executable_authority(self):
        # Only a passive observation consumer is permissible; nothing in a
        # receipt can authorize an operation or shell command.
        receipt=json.loads((FIX/'receipt.golden.json').read_text())
        self.assertFalse(any(x in receipt for x in ('command','execute','approved','action')))
        self.assertTrue(all(d['status'] in ('ok','error') for d in receipt['decisions']))
        self.assertNotEqual(receipt['authority'],'execute')

    def test_domain_boundary(self):
        subprocess.run(['python3',str(ROOT/'tools/check_boundary.py')],check=True,capture_output=True)

if __name__=='__main__':unittest.main()
