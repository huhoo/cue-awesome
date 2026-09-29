#!/usr/bin/env python3
"""Boundary tests for the offline package contract; no live parser or LLM evaluation."""
import argparse
import copy
import contextlib
import io
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

SPEC = importlib.util.spec_from_file_location("ontology", Path(__file__).with_name("ontology.py"))
o = importlib.util.module_from_spec(SPEC)
sys.modules['ontology'] = o
SPEC.loader.exec_module(o)
import experience as e
DEMO = Path(__file__).resolve().parent.parent / "assets" / "demo"


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.inputs = self.root / "inputs"
        shutil.copytree(DEMO, self.inputs)
        self.a, _ = o.prepare_input(self.inputs / "r1.json")
        self.b, _ = o.prepare_input(self.inputs / "r2.json")

    def tearDown(self): self.temp.cleanup()

    def build(self):
        dest = self.root / "v1"
        o.write_package(self.a, o.roots_for(self.a, self.inputs), dest, {})
        return dest

    def merged(self):
        dest = self.build()
        base, run = o.load_package(dest)
        k, changes = o.merge(base, self.b)
        out = self.root / "v2"
        roots = dict(o.roots_for(base, dest), **o.roots_for(self.b, self.inputs))
        o.write_package(k, roots, out, changes, run["knowledge_sha256"], "update")
        return out

    def test_replay_no_duplicate_or_lost_history(self):
        out = self.merged(); k, _ = o.load_package(out)
        again, changes = o.merge(k, self.b)
        self.assertEqual(len(again["assertions"]), 5)
        self.assertEqual(changes["duplicate_assertions"], 3)
        self.assertEqual(len([a for a in again["assertions"] if a["concept_id"] == "relation:offers"]), 1)

    def test_restated_same_period_preserves_conflict(self):
        k, _ = o.load_package(self.merged())
        r = o.query(k, SimpleNamespace(entity=None, concept="metric:revenue", period="2025Q4", basis="IFRS", qualifiers=None))
        self.assertEqual(r["status"], "conflict")
        self.assertEqual({a["value"] for a in r["assertions"]}, {100, 105})

    def test_unspecified_basis_requires_scope(self):
        k, _ = o.load_package(self.merged())
        r = o.query(k, SimpleNamespace(entity=None, concept="metric:revenue", period="2026Q1", basis=None, qualifiers=None))
        self.assertEqual(r["status"], "needs_scope")

    def test_explicit_basis_selects_with_evidence(self):
        k, _ = o.load_package(self.merged())
        r = o.query(k, SimpleNamespace(entity=None, concept="metric:revenue", period="2026Q1", basis="IFRS", qualifiers="{}"))
        self.assertEqual(r["status"], "found")
        self.assertEqual(r["assertions"][0]["value"], 120)
        self.assertTrue(r["sources"])

    def test_changed_definition_reusing_id_rejected(self):
        self.b["definitions"][0]["description"] = "A silently different meaning"
        with self.assertRaises(o.Invalid): o.merge(self.a, self.b)

    def test_changed_source_reusing_id_rejected(self):
        other = copy.deepcopy(self.a); other["sources"][0]["sha256"] = "0" * 64
        with self.assertRaises(o.Invalid): o.merge(self.a, other)

    def test_retrieval_date_cannot_move_scope_backwards(self):
        self.b["scope"]["as_of"] = "2025-01-01"
        with self.assertRaises(o.Invalid): o.merge(self.a, self.b)

    def test_source_bytes_tampering_rejected(self):
        out = self.build(); k, _ = o.load_package(out)
        (out / k["sources"][0]["content_file"]).write_text("changed")
        with self.assertRaises(o.Invalid): o.load_package(out)

    def test_knowledge_tampering_rejected(self):
        out = self.build(); k = o.read_json(out / "knowledge.json")
        k["assertions"][0]["value"] = 999
        (out / "knowledge.json").write_text(json.dumps(k))
        with self.assertRaises(o.Invalid): o.load_package(out)

    def test_changes_tampering_rejected(self):
        out = self.build(); (out / "changes.json").write_text('{}')
        with self.assertRaises(o.Invalid): o.load_package(out)

    def test_bad_page_is_not_native_evidence(self):
        self.a["assertions"][0]["evidence"][0]["page"] = 2
        with self.assertRaises(o.Invalid): o.check_knowledge(self.a, self.inputs)

    def test_fake_native_provenance_rejected(self):
        self.a["sources"][0]["page_spans"][0]["basis"] = o.OMNI
        with self.assertRaises(o.Invalid): o.check_knowledge(self.a, self.inputs)

    def test_range_hash_mismatch_rejected(self):
        self.a["assertions"][0]["evidence"][0]["span_sha256"] = "0" * 64
        with self.assertRaises(o.Invalid): o.check_knowledge(self.a, self.inputs)

    def test_unicode_mid_character_range_rejected(self):
        s = self.a["sources"][0]; raw = '企业'.encode(); (self.inputs / s["content_file"]).write_bytes(raw)
        s["sha256"] = o.digest(raw); s["page_spans"][0]["end_utf8"] = len(raw)
        ev = self.a["assertions"][0]["evidence"][0]
        ev.update(start_utf8=1, end_utf8=3, span_sha256=o.digest(raw[1:3]))
        with self.assertRaises(UnicodeError): o.check_knowledge(self.a, self.inputs)

    def test_unknown_entity_relation_rejected(self):
        self.a["assertions"][1]["value"] = "org:unknown"
        with self.assertRaises(o.Invalid): o.check_knowledge(self.a, self.inputs)

    def test_unit_required(self):
        self.a["assertions"][0]["unit"] = ""
        with self.assertRaises(o.Invalid): o.check_knowledge(self.a, self.inputs)

    def test_injected_acceptance_rejected(self):
        j = o.read_json(self.inputs / "r1.json"); j["assertions"][0]["status"] = "accepted"
        p = self.inputs / "injected.json"; p.write_text(json.dumps(j))
        with self.assertRaises(o.Invalid): o.prepare_input(p)

    def test_claim_kind_defaults_to_reported(self):
        j = o.read_json(self.inputs / "r1.json")
        for a in j["assertions"]: a.pop("claim_kind", None)
        p = self.inputs / "noclaim.json"; p.write_text(json.dumps(j))
        k, _ = o.prepare_input(p)
        self.assertTrue(all(a["claim_kind"] == "reported" for a in k["assertions"]))

    def test_derived_value_cannot_masquerade_as_reported(self):
        self.a["assertions"][0]["claim_kind"] = "derived"
        with self.assertRaises(o.Invalid): o.check_knowledge(self.a, self.inputs)

    def test_traversal_rejected(self):
        with self.assertRaises(o.Invalid): o.local_file(self.inputs, "../outside.txt")

    def test_symlink_escape_rejected(self):
        external = self.root / "outside.txt"; external.write_text("private")
        (self.inputs / "link.txt").symlink_to(external)
        if not (self.inputs / "link.txt").is_symlink():
            # On Windows without symlink privilege, symlink_to silently copies the
            # target instead of creating a link, so no escape exists to reject.
            self.skipTest("platform cannot create file symlinks (silently copied)")
        with self.assertRaises(o.Invalid): o.local_file(self.inputs, "link.txt")

    def test_private_and_credential_urls_rejected(self):
        for url in ("http://127.0.0.1/a", "http://localhost/a", "http://service.internal/a", "https://u:p@example.org/a", "https://example.org/a?token=abc"):
            with self.subTest(url=url), self.assertRaises(o.Invalid): o.public_url(url)

    def test_existing_output_never_overwritten(self):
        out = self.build()
        with self.assertRaises(o.Invalid): o.write_package(self.a, o.roots_for(self.a, self.inputs), out, {})

    def test_missing_query_is_not_zero(self):
        r = o.query(self.a, SimpleNamespace(entity=None, concept="metric:none", period=None, basis=None, qualifiers=None))
        self.assertEqual(r["status"], "not_found"); self.assertEqual(r["assertions"], [])

    def test_duplicate_json_keys_rejected(self):
        p = self.root / "duplicate.json"; p.write_text('{"value":1,"value":2}')
        with self.assertRaises(o.Invalid): o.read_json(p)

    def test_okf_never_claims_human_verification(self):
        out = self.root / "okf"; o.export_okf(self.a, out)
        files = list(out.glob('concept-*.md')); self.assertEqual(len(files), 2)
        for f in files:
            s = f.read_text(); self.assertIn('status: draft', s); self.assertNotIn('\nverified:', s)

    def test_review_persists_across_duplicate_update(self):
        base = self.build(); k, _ = o.load_package(base)
        reviewed = self.root / 'reviewed'
        with contextlib.redirect_stdout(io.StringIO()):
            code = o.main(['review', str(base), '--assertion', k['assertions'][0]['id'], '--decision', 'rejected',
                           '--reviewer', 'synthetic-test-actor', '--note', 'Synthetic regression decision', '--out', str(reviewed)])
        self.assertEqual(code, 0)
        r, _ = o.load_package(reviewed); merged, changes = o.merge(r, self.a)
        self.assertEqual(merged['assertions'][0]['status'], 'rejected')
        self.assertEqual(changes['duplicate_assertions'], 2)
        self.assertEqual(len(merged['assertions'][0]['reviews']), 1)
        original, _ = o.load_package(base)
        self.assertEqual(original['assertions'][0]['status'], 'candidate')

    def test_feedback_excludes_source_and_claim_content(self):
        base = self.build(); out = self.root / 'feedback.json'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(o.main(['feedback', str(base), '--out', str(out)]), 0)
        s = out.read_text()
        for value in ['example.org', 'Northstar', '100', 'demo-r1']:
            self.assertNotIn(value, s)

    def test_url_markup_characters_rejected(self):
        for value in ['https://example.org/a>bad', 'https://example.org/a\nnext', 'https://example.org/a space']:
            with self.subTest(value=value), self.assertRaises(o.Invalid): o.public_url(value)

    def test_numeric_spelling_is_support_not_conflict(self):
        incoming = copy.deepcopy(self.a)
        row = incoming['assertions'][0]
        original_id = row['id']
        row['value'] = float(row['value']); row['id'] = o.assertion_id(row)
        merged, changes = o.merge(self.a, incoming)
        self.assertEqual(o.conflict_ids(merged), [])
        self.assertEqual(changes['additional_support'], [row['id']])
        self.assertEqual(merged['assertions'][0]['id'], original_id)
        result = o.query(merged, SimpleNamespace(concept='metric:revenue', qualifiers=None))
        self.assertEqual(result['status'], 'found')
        self.assertEqual(len(result['assertions']), 2)

    def test_large_integer_differences_are_not_rounded_away(self):
        a = 10 ** 40
        self.assertNotEqual(o.value_key(a), o.value_key(a + 1))

    def test_unit_and_validity_scope_can_be_selected(self):
        a = self.a['assertions'][0]
        b = copy.deepcopy(a); b.update(unit='CNY', valid_from='2026-01-01', valid_to='2026-03-31')
        b['fact_id'] = o.fact_id(b); b['id'] = o.assertion_id(b)
        self.a['assertions'].append(b)
        broad = o.query(self.a, SimpleNamespace(concept='metric:revenue', qualifiers=None))
        self.assertEqual(broad['status'], 'needs_scope')
        self.assertEqual(len(broad['scopes']), 2)
        selected = o.query(self.a, SimpleNamespace(concept='metric:revenue', qualifiers=None,
                          unit='CNY', valid_from='2026-01-01', valid_to='2026-03-31'))
        self.assertEqual(selected['status'], 'found')
        self.assertEqual(selected['assertions'], [b])

    def test_fact_cli_selects_from_old_schema_package(self):
        base = self.build(); k, run = o.load_package(base)
        self.assertEqual(run['schema_version'], '0.1.0')
        self.assertEqual(run['skill_version'], o.VERSION)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = o.main(['query', str(base), '--fact', k['assertions'][0]['fact_id']])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())['status'], 'found')

    def test_boolean_qualifier_does_not_match_number(self):
        a = self.a['assertions'][0]; a['qualifiers'] = {'flag': True}
        a['fact_id'] = o.fact_id(a); a['id'] = o.assertion_id(a)
        result = o.query(self.a, SimpleNamespace(concept='metric:revenue', qualifiers='{"flag":1}'))
        self.assertEqual(result['status'], 'not_found')

    def test_query_rejects_ambiguous_json_and_invalid_dates(self):
        for value in ('{"flag":1,"flag":2}', '{"flag":NaN}'):
            with self.subTest(value=value), self.assertRaises(o.Invalid):
                o.query(self.a, SimpleNamespace(qualifiers=value))
        with self.assertRaises(o.Invalid):
            o.query(self.a, SimpleNamespace(qualifiers=None, valid_from='2026-99-01'))

    def test_malformed_assertions_return_structured_error(self):
        for bad in (None, {}, ['text'], [None]):
            k = o.read_json(self.inputs / 'r1.json'); k['assertions'] = bad
            p = self.inputs / 'malformed.json'; p.write_text(json.dumps(k))
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                code = o.main(['build', str(p), '--out', str(self.root / 'invalid')])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(stderr.getvalue())['status'], 'invalid')
            self.assertFalse((self.root / 'invalid').exists())

    def test_report_identifies_conflict_scope_and_escapes_source_text(self):
        k, changes = o.merge(self.a, self.b)
        changes['conflicts'] = o.conflict_ids(k)
        k['entities'][0]['name'] = '[external](https://example.org)'
        rendered = o.render(k, changes)
        self.assertIn('candidate / conflict', rendered)
        self.assertIn(changes['conflicts'][0], rendered)
        self.assertIn('| Validity |', rendered)
        self.assertNotIn('[external](https://example.org)', rendered)

    def test_quote_preparation_preserves_exact_evidence(self):
        target = self.root / 'prepared'
        e.prepare(self.inputs / 'quote-draft.json', target)
        k, _ = o.prepare_input(target / 'input.json')
        self.assertEqual(k['assertions'], self.a['assertions'])
        self.assertEqual(k['sources'][0]['sha256'], self.a['sources'][0]['sha256'])

    def quote_input(self, text, quote, occurrence=None):
        d = o.read_json(self.inputs / 'quote-draft.json')
        d['assertions'] = d['assertions'][:1]
        d['sources'][0]['page_spans'] = []
        (self.inputs/d['sources'][0]['content_file']).write_text(text, encoding='utf-8')
        d['assertions'][0]['evidence'] = [dict(source_id=d['sources'][0]['id'],role='value',quote=quote)]
        if occurrence is not None: d['assertions'][0]['evidence'][0]['occurrence'] = occurrence
        p=self.inputs/'draft.json';p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8')
        return p

    def test_ambiguous_quote_fails_without_output(self):
        p=self.quote_input('收入 100。收入 100。','收入 100。')
        with self.assertRaises(o.Invalid): e.prepare(p,self.root/'prepared')
        self.assertFalse((self.root/'prepared').exists())

    def test_quote_occurrence_uses_utf8_byte_positions(self):
        p=self.quote_input('收入 100。收入 100。','收入 100。',2)
        e.prepare(p,self.root/'prepared')
        k,_=o.prepare_input(self.root/'prepared'/'input.json')
        self.assertEqual(k['assertions'][0]['evidence'][0]['start_utf8'],len('收入 100。'.encode()))

    def test_changed_quote_and_wrong_hash_are_rejected(self):
        p=self.quote_input('actual text','invented text')
        with self.assertRaises(o.Invalid): e.prepare(p,self.root/'bad')
        d=o.read_json(p);d['assertions'][0]['evidence'][0]['quote']='actual text';d['sources'][0]['sha256']='0'*64
        p.write_text(json.dumps(d))
        with self.assertRaises(o.Invalid): e.prepare(p,self.root/'bad')

    def test_quote_locator_cannot_override_derived_page(self):
        p=self.inputs/'quote-draft.json';d=o.read_json(p)
        d['assertions'][0]['evidence'][0]['page']=999;p.write_text(json.dumps(d))
        with self.assertRaises(o.Invalid): e.prepare(p,self.root/'bad')

    def test_brief_requires_preserved_baseline(self):
        current,_=o.merge(self.a,self.b)
        delta=e.changes_between(self.a,current)
        self.assertEqual(len(delta['new_conflict_ids']),1)
        self.assertEqual(delta['baseline_assertions_preserved'],2)
        current['assertions'].pop(0)
        with self.assertRaises(o.Invalid): e.changes_between(self.a,current)

    def test_evidence_previews_are_bounded_and_not_rewritten(self):
        previews=e.previews(self.a,self.inputs,limit=10)
        self.assertTrue(previews[0]['truncated'])
        ev=self.a['assertions'][0]['evidence'][0]
        raw=(self.inputs/self.a['sources'][0]['content_file']).read_bytes()
        self.assertEqual(previews[0]['excerpt'],raw[ev['start_utf8']:ev['end_utf8']].decode()[:10])

    def test_brief_html_keeps_hostile_content_as_data(self):
        k=copy.deepcopy(self.a);k['scope']['title']='</script><img src=x onerror=alert(1)>'
        d=e.payload(k,self.inputs)
        document=e.html_report(d)
        self.assertNotIn('</script><img',document)
        self.assertIn('\\u003c/script',document)
        self.assertNotIn('innerHTML',document)

    def test_one_command_demo_is_complete_and_offline(self):
        out=self.root/'demo';result=e.demo(out)
        self.assertEqual(result['api_calls'],0)
        self.assertTrue((out/'brief'/'brief.html').is_file())
        k,_=o.load_package(out/'v2');self.assertEqual(len(k['assertions']),5)
        with self.assertRaises(o.Invalid): e.demo(out)

    def test_query_evidence_cli_returns_source_excerpts(self):
        base=self.build();stdout=io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(o.main(['query',str(base),'--concept','metric:revenue','--with-evidence']),0)
        result=json.loads(stdout.getvalue())
        self.assertTrue(result['evidence_previews'][0]['excerpt'])
        self.assertIn('url',result['evidence_previews'][0])


class VersionConsistency(unittest.TestCase):
    """M158 案①一致性锁:脚本 VERSION 常量必须==两份 SKILL frontmatter version(防漂)。

    M158 追加(4.1 发现,lead 转):本包中英两份 SKILL 各带 version 字段,单读一份
    测不到两文漂移——遍历 SKILL.md+SKILL.en.md,三者(脚本+两份)同号才放行。"""

    def test_script_version_equals_both_skill_frontmatter(self):
        root = Path(__file__).resolve().parent.parent
        for name in ("SKILL.md", "SKILL.en.md"):
            with self.subTest(skill=name):
                text = (root / name).read_text(encoding="utf-8")
                fm = re.search(r"^---\s*\n(.*?)\n---\n", text, re.DOTALL)
                self.assertIsNotNone(fm, f"{name} 缺 frontmatter 块")
                mv = re.search(r'^version:\s*"?([0-9][^"\n]*)"?\s*$', fm.group(1), re.MULTILINE)
                self.assertIsNotNone(mv, f"{name} frontmatter 缺 version 字段")
                self.assertEqual(o.VERSION, mv.group(1),
                                 f"ontology.py VERSION={o.VERSION} 与 {name} frontmatter {mv.group(1)} 漂号(M156 第6项/M158 追加)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    unittest.main(argv=[__file__], verbosity=2)
