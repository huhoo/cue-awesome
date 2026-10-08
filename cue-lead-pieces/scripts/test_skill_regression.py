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
        self.assertRegex(fm, re.compile(r'^name:\s*cue-lead-pieces$', re.M)); self.assertIn('version: "0.4.0"', fm); self.assertEqual(cue.__version__, '0.4.0')
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
    def test_unknown_code_one_line_error(self):
        """0.3.1: an unknown A-share code / US ticker / CIK exits 2 with one stderr line, not a StopIteration traceback (offline: `get` is faked)"""
        import urllib.error
        def fake_get(url, headers=None, data=None, tries=4):
            if 'cninfo' in url: return json.dumps({'stockList': [{'code': '600606', 'orgId': 'x', 'zwjc': 'X'}]}).encode()
            if 'company_tickers' in url: return json.dumps({'0': {'cik_str': 1, 'ticker': 'LESL', 'title': 'X'}}).encode()
            raise urllib.error.HTTPError(url, 404, 'Not Found', None, None)
        real = cue.get; cue.get = fake_get
        try:
            for args, want in ((['--cn', '999999'], "unknown A-share code '999999'"), (['--us', 'ZZZZQX'], "unknown US ticker 'ZZZZQX'"),
                               (['--us', '9999999999'], "unknown CIK '9999999999'")):
                err = io.StringIO(); d = os.path.join(self.d, 'fetch-' + args[1])
                with contextlib.redirect_stderr(err): rc = cue.main(['fetch', d] + args)
                self.assertEqual(rc, 2); lines = err.getvalue().strip().splitlines()
                self.assertEqual(len(lines), 1, err.getvalue()); self.assertTrue(lines[0].startswith('cue.py: error: ' + want), lines[0])
                self.assertNotIn('Traceback', err.getvalue())
        finally: cue.get = real
    def _bundle(self):
        """synthetic omni.result_bundle.v1 (grounded) in the public shape: Markdown text + segments with UTF-8 byte ranges and source PDF page anchors"""
        parts = [("# 年度报告\n公司存在逾期债务，金额为 1,234 万元。\n", 1), ("| 项目 | 期末 |\n|---|---|\n| 短期借款 | 5,678 |\n", 2), ("会计师对持续经营能力出具了强调事项段。\n", 4)]
        text, segs, pos = '', [], 0
        for i, (t, p) in enumerate(parts, 1):
            b = len(t.encode('utf-8')); text += t
            segs.append({'segment_id': f'segment_{i:06d}', 'content_range_utf8': {'start': pos, 'end': pos + b},
                         'grounding': {'availability': 'available', 'anchors': [{'kind': 'page', 'basis': 'source_pdf_page_1_based', 'reliability': 'reliable', 'value': p}]}}); pos += b
        return {'protocol_version': 'omni.result_bundle.v1', 'detail': 'grounded', 'content': {'media_type': 'text/markdown; charset=utf-8', 'text': text},
                'grounding': {'media_type': 'application/vnd.cue.omni-grounding+json; version=1', 'value': {'schema_version': 'omni.grounding.v1', 'detail': 'grounded',
                              'document': {'format': 'pdf', 'partial': True, 'incomplete': [{'basis': 'source_pdf_page_1_based', 'kind': 'page', 'reason': 'processing_timeout', 'values': [3]}]},
                              'segments': segs}}}
    def test_ingest_omni_grounded_bundle(self):
        """0.4.0: an Omni grounded bundle becomes per-PDF-page text; verify then checks quotes against those pages"""
        d = os.path.join(self.d, 'cn'); od = os.path.join(d, 'omni'); os.makedirs(od)
        json.dump({'structuredContent': {'result': self._bundle()}}, open(os.path.join(od, 'AR2025.json'), 'w'), ensure_ascii=False)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cue.main(['ingest', d, '--omni', os.path.join(od, 'AR2025.json'), '--sid', 'AR2025', '--kind', 'annual', '--date', '2026-04-20',
                           '--title', '2025年年度报告', '--company', 'TestCN', '--market', 'CN'])
        self.assertEqual(rc, 0); self.assertIn('parser=omni-grounded, page_basis=pdf_page', out.getvalue()); self.assertIn('incomplete page [3]', out.getvalue())
        meta, S = cue.load(d); s = S['AR2025']
        self.assertEqual((s['n_pages'], s['parser'], s['page_basis']), (4, 'omni-grounded', 'pdf_page')); self.assertEqual(s['text'][3], '')
        self.assertEqual(cue.check('公司存在逾期债务，金额为1,234万元', 'AR2025', 1, S)['status'], 'verbatim')
        self.assertEqual(cue.check('会计师对持续经营能力出具了强调事项段', 'AR2025', 4, S)['status'], 'verbatim')
        self.assertEqual(cue.check('会计师对持续经营能力出具了强调事项段', 'AR2025', 1, S)['status'], 'verbatim_elsewhere')
        self.assertIn('短期借款', s['text'][2])
    def test_ingest_text_only_and_markers(self):
        self.assertEqual(cue.text_pages('a\fb')[1], 'form_feed')
        p, basis = cue.text_pages('<!-- page 1 -->\nfirst\n<!-- page 3 -->\nthird\n'); self.assertEqual((basis, len(p), p[2].strip()), ('marker', 3, 'third'))
        p, basis = cue.text_pages(('x' * 100 + '\n') * 80); self.assertEqual(basis, 'block'); self.assertGreater(len(p), 1)
    def test_list_register_and_local_fallback(self):
        """fetch --list registers filings as pending (e.g. from Cue data-MCP); local is the labeled fallback parser (`get` faked, offline)"""
        d = os.path.join(self.d, 'us'); lst = os.path.join(self.d, 'list.json')
        json.dump([{'sid': '8-K_2026-05-01', 'kind': 'event', 'date': '2026-05-01', 'title': '8-K', 'source_url': 'https://example.com/a.htm'}], open(lst, 'w'))
        html = ('<p>' + 'Lenders agreed to a forbearance period under the credit agreement. ' * 3 + '</p><div style="page-break-after: always"></div>') * 3
        real = cue.get; cue.get = lambda url, headers=None, data=None, tries=4: html.encode()
        try:
            with contextlib.redirect_stdout(io.StringIO()) as o1: self.assertEqual(cue.main(['fetch', d, '--list', lst, '--company', 'T', '--market', 'US']), 0)
            self.assertIn('not parsed yet', o1.getvalue()); self.assertEqual(cue.load(d)[1]['8-K_2026-05-01']['parser'], 'pending')
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(cue.main(['local', d]), 0)
        finally: cue.get = real
        s = cue.load(d)[1]['8-K_2026-05-01']; self.assertEqual((s['parser'], s['page_basis'], s['n_pages']), ('local', 'html_page_break', 3))
    def test_cn_fetch_lists_without_download(self):
        """default fetch only lists filings (no download, no parse) so the agent can hand the URLs to Cue Omni Reader"""
        ann = {'announcementId': 1, 'announcementTitle': '2025年年度报告', 'adjunctUrl': 'finalpage/2026-04-20/1.PDF', 'announcementTime': 1776650000000}
        def fake_get(url, headers=None, data=None, tries=4):
            if 'szse_stock' in url: return json.dumps({'stockList': [{'code': '600606', 'orgId': 'x', 'zwjc': 'X'}]}).encode()
            if 'hisAnnouncement' in url: return json.dumps({'announcements': [ann] if b'category_ndbg' in (data or b'') else [], 'hasMore': False}).encode()
            raise AssertionError('download attempted: ' + url)
        real = cue.get; cue.get = fake_get; d = os.path.join(self.d, 'cnlist')
        try:
            with contextlib.redirect_stdout(io.StringIO()) as o: self.assertEqual(cue.main(['fetch', d, '--cn', '600606']), 0)
        finally: cue.get = real
        m = json.load(open(os.path.join(d, 'sources.json'))); self.assertEqual([(x['sid'], x['parser']) for x in m['sources']], [('AR2025', 'pending')])
        self.assertTrue(m['sources'][0]['source_url'].endswith('.PDF')); self.assertIn('Cue Omni Reader', o.getvalue())
    def test_page_and_brief_offline(self):
        self.assertEqual(cue.pagespec('1,3-4'), [1, 3, 4])
        out = subprocess.run([sys.executable, str(CUE), 'page', self.d, '10-K_FY2025', '1-2'], capture_output=True, text=True, check=True).stdout
        self.assertIn('[10-K_FY2025 p2]', out)
        env = {k: v for k, v in os.environ.items() if not k.startswith('CUE_LLM_')}
        out = subprocess.run([sys.executable, str(CUE), 'brief', self.d], capture_output=True, text=True, check=True, env=env).stdout
        self.assertIn('10-K_FY2025', out); self.assertEqual(json.load(open(f'{self.d}/leads.json'))['aligner'], 'fallback')
if __name__ == '__main__': unittest.main(verbosity=2)
