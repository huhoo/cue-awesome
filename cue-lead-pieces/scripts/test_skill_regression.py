#!/usr/bin/env python3
"""cue-lead-pieces skill regression — stdlib only, offline (synthetic filings, no network, no model)."""
from __future__ import annotations
import io, json, os, re, shutil, subprocess, sys, tempfile, unittest, contextlib
from pathlib import Path
_HERE = Path(__file__).resolve().parent; _SKILL = _HERE.parent; CUE = _HERE / 'cue.py'
sys.path.insert(0, str(_HERE)); import cue  # noqa: E402
P1 = "Liquidity\nAs a result of the upcoming maturity of the Credit Facility, there is substantial doubt about our ability to continue as a going concern.\nNet loss | 1,234 | 987\n"
P2 = "Other matters\nThe lenders have the right to accelerate the loans for noncompliance with the net leverage ratio covenant.\n"
def make_dir(d):
    os.makedirs(f'{d}/pages'); src = [{'sid': '10-K_FY2025', 'kind': 'annual', 'date': '2026-03-01', 'title': '10-K test', 'n_pages': 2}]
    json.dump({'company': 'TestCo', 'id': 'TEST', 'market': 'US', 'sources': src}, open(f'{d}/sources.json', 'w'))
    with open(f'{d}/pages/10-K_FY2025.jsonl', 'w') as f:
        for i, t in enumerate((P1, P2), 1): f.write(json.dumps({'page': i, 'text': t}) + '\n')
class CueLeadPiecesRegression(unittest.TestCase):
    def setUp(self): self.d = tempfile.mkdtemp(); make_dir(self.d); self.S = cue.load(self.d)[1]
    def tearDown(self): shutil.rmtree(self.d, ignore_errors=True)
    def test_frontmatter(self):
        md = (_SKILL / 'SKILL.md').read_text(encoding='utf-8'); fm = re.match(r'^---\n(.*?)\n---\n', md, re.S).group(1)
        self.assertRegex(fm, re.compile(r'^name:\s*cue-lead-pieces$', re.M)); self.assertIn('version: "0.3.0"', fm); self.assertEqual(cue.__version__, '0.3.0')
    def test_verify_levels(self):
        c = lambda q, p: cue.check(q, '10-K_FY2025', p, self.S)
        self.assertEqual(c('there is substantial doubt about our ability to continue as a going concern', 1)['status'], 'verbatim')
        self.assertEqual(c('The lenders have the right to accelerate the loans', 9)['status'], 'verbatim_elsewhere')
        r = c('there is substantial doubt about our ability to continue as going concern', 1); self.assertEqual((r['status'], r.get('kind')), ('not_found', 'edited'))
        r = c('The company has ample liquidity and no refinancing needs at all', 1); self.assertEqual(r['status'], 'not_found'); self.assertIn(r['kind'], ('absent', 'numbers_differ'))
    def test_fix_rewrites_answer(self):
        a = os.path.join(self.d, 'answer.json')
        json.dump({'signals': [{'rank': 1, 'title': 't', 'explanation': 'e', 'evidence': [
            {'source': '10-K_FY2025', 'page': 1, 'quote': 'there is substantial doubt about our ability to continue as going concern'},
            {'source': '10-K_FY2025', 'page': 9, 'quote': 'The lenders have the right to accelerate the loans'},
            {'source': '10-K_FY2025', 'page': 1, 'quote': 'The company has ample liquidity and no refinancing needs at all'}]}]}, open(a, 'w'))
        out = subprocess.run([sys.executable, str(CUE), 'verify', self.d, '--json', a, '--fix'], capture_output=True, text=True, check=True).stdout
        self.assertTrue(os.path.exists(os.path.join(self.d, 'answer.before_fix.json')))
        ev = json.load(open(a))['signals'][0]['evidence']; self.assertEqual(len(ev), 2)
        for e in ev: self.assertEqual(cue.check(e['quote'], e['source'], e['page'], cue.load(self.d)[1])['status'], 'verbatim')
        self.assertIn('"after": {"verbatim": 2, "total": 2}', out)
    def test_page_and_brief_offline(self):
        self.assertEqual(cue.pagespec('1,3-4'), [1, 3, 4])
        out = subprocess.run([sys.executable, str(CUE), 'page', self.d, '10-K_FY2025', '1-2'], capture_output=True, text=True, check=True).stdout
        self.assertIn('[10-K_FY2025 p2]', out)
        env = {k: v for k, v in os.environ.items() if not k.startswith('CUE_LLM_')}
        out = subprocess.run([sys.executable, str(CUE), 'brief', self.d], capture_output=True, text=True, check=True, env=env).stdout
        self.assertIn('10-K_FY2025', out); self.assertEqual(json.load(open(f'{self.d}/leads.json'))['aligner'], 'fallback')
if __name__ == '__main__': unittest.main(verbosity=2)
