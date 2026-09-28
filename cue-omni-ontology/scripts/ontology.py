#!/usr/bin/env python3
"""Offline knowledge packaging. Semantic extraction is performed by the host agent.

Only Python's standard library is required. No network requests or telemetry.
Hashes and range checks establish internal integrity, not source truth or IAM.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import ipaddress
import json
import math
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

VERSION = "0.2.0"
SCHEMA_VERSION = "0.1.0"
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,119}$")
HASH = re.compile(r"^[0-9a-f]{64}$")
TYPES = {"Organization", "Product", "BusinessSegment", "Topic"}
VALUE_TYPES = {"number", "string", "boolean", "entity", "set"}
OMNI = "omni_native_source_pdf_page"


class Invalid(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Invalid(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value).encode()).hexdigest()


def read_json(path):
    return decode_json(Path(path).read_text(encoding="utf-8"))


def decode_json(content):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, f"duplicate JSON key: {key}")
            out[key] = value
        return out
    return json.loads(content, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(Invalid(f"nonfinite number: {x}")))


def text(value, label):
    need(isinstance(value, str) and bool(value.strip()), f"{label}: nonempty text required")
    return value


def ident(value, label):
    need(isinstance(value, str) and ID.fullmatch(value), f"{label}: invalid ID")
    return value


def iso_date(value, label, nullable=False):
    if value is None and nullable:
        return
    need(isinstance(value, str), f"{label}: date required")
    try:
        need(date.fromisoformat(value).isoformat() == value, f"{label}: YYYY-MM-DD required")
    except (ValueError, TypeError):
        raise Invalid(f"{label}: YYYY-MM-DD required")


def public_url(value):
    text(value, "source.url")
    need(not any(c.isspace() or c in '<>"`' for c in value), "source.url: unsafe characters")
    try:
        p = urlsplit(value)
        need(p.scheme in {"http", "https"} and bool(p.hostname), "source.url: HTTP(S) required")
        need(not p.username and not p.password, "source.url: userinfo forbidden")
        host = p.hostname.lower().rstrip(".")
        need(host != "localhost" and not host.endswith((".localhost", ".local", ".internal")),
             "source.url: public host required")
        try:
            need(ipaddress.ip_address(host).is_global, "source.url: non-public IP")
        except ValueError as exc:
            if isinstance(exc, Invalid):
                raise
            need("." in host, "source.url: public hostname required")
        sensitive = {"token", "access_token", "api_key", "key", "signature", "sig", "x-amz-signature"}
        need(not any(k.lower() in sensitive for k, _ in parse_qsl(p.query)), "source.url: credential-like query")
    except ValueError as exc:
        raise Invalid(str(exc))


def local_file(root, rel):
    text(rel, "content_file")
    p = Path(rel)
    need(not p.is_absolute() and ".." not in p.parts, "content_file: relative path without traversal required")
    target = (root / p).resolve()
    need(target.is_relative_to(root.resolve()) and target.is_file(), "content_file: unavailable or outside input directory")
    need(target.stat().st_size <= 32 * 1024 * 1024, "content_file: exceeds 32 MiB")
    return target


def indexed(items, label):
    need(isinstance(items, list), f"{label}: list required")
    out = {}
    for item in items:
        need(isinstance(item, dict), f"{label}: object required")
        key = ident(item.get("id"), label)
        need(key not in out, f"{label}: duplicate ID {key}")
        out[key] = copy.deepcopy(item)
    return out


def key_of(a):
    return {k: a[k] for k in ("entity_id", "concept_id", "unit", "period", "basis", "qualifiers", "valid_from", "valid_to")}


def fact_id(a):
    return "fact:" + digest(key_of(a))[:24]


def assertion_id(a):
    # Value and exact supporting ranges belong to the source assertion, not the logical fact key.
    return "assert:" + digest({k: a[k] for k in ("fact_id", "value", "evidence")})[:24]


def value_key(value):
    # Compare numeric spelling without rounding large integers or changing stored identities.
    return ("number", Decimal(str(value))) if type(value) in {int, float} else ("other", canonical(value))


def check_knowledge(k, root, normalized=True):
    need(isinstance(k, dict) and k.get("schema_version") == SCHEMA_VERSION, "unsupported schema_version")
    scope = k.get("scope", {})
    need(isinstance(scope, dict), "scope: object required")
    text(scope.get("title"), "scope.title")
    iso_date(scope.get("as_of"), "scope.as_of")
    entities = indexed(k.get("entities"), "entities")
    for e in entities.values():
        need(e.get("type") in TYPES, "unsupported entity type")
        text(e.get("name"), "entity.name")
    defs = indexed(k.get("definitions"), "definitions")
    for d in defs.values():
        need(d.get("kind") in {"metric", "relation", "attribute"}, "invalid definition kind")
        need(d.get("value_type") in VALUE_TYPES, "invalid definition value_type")
        if d["kind"] == "relation":
            need(d["value_type"] == "entity", "relation must have entity value_type")
        text(d.get("name"), "definition.name")
        text(d.get("description"), "definition.description")
        need(d.get("status", "candidate") == "candidate", "public-beta definitions remain candidates; no schema approval engine")
    sources = indexed(k.get("sources"), "sources")
    source_bytes = {}
    for s in sources.values():
        public_url(s.get("url"))
        text(s.get("title"), "source.title")
        iso_date(s.get("published_at"), "source.published_at", True)
        iso_date(s.get("accessed_at"), "source.accessed_at")
        need(s.get("public_status") in {"user_confirmed", "retrieved_public", "synthetic"}, "source public_status required")
        need(s.get("parse_origin") in {"omni_live", "omni_replay", "synthetic", "other"}, "source parse_origin required")
        raw = local_file(root, s.get("content_file")).read_bytes()
        raw.decode("utf-8")
        need(isinstance(s.get("sha256"), str) and HASH.fullmatch(s["sha256"]) and digest(raw) == s["sha256"],
             f"source hash mismatch: {s['id']}")
        source_bytes[s["id"]] = raw
        spans = s.get("page_spans", [])
        need(isinstance(spans, list), "source.page_spans: list required")
        previous = 0
        pages = set()
        for span in spans:
            need(isinstance(span, dict), "page span must be object")
            page, start, end = span.get("page"), span.get("start_utf8"), span.get("end_utf8")
            need(type(page) is int and page > 0 and page not in pages, "page must be unique positive integer")
            need(type(start) is int and type(end) is int and previous <= start < end <= len(raw), "invalid page span")
            raw[:start].decode("utf-8"); raw[start:end].decode("utf-8")
            need(span.get("basis") in {OMNI, "synthetic_page", "manual_page"}, "invalid page basis")
            need(span["basis"] != OMNI or s["parse_origin"] in {"omni_live", "omni_replay"}, "native page requires Omni provenance")
            previous = end; pages.add(page)
    assertions = k.get("assertions")
    need(isinstance(assertions, list), "assertions: list required")
    seen = set()
    for a in assertions:
        need(isinstance(a, dict), "assertion must be object")
        need(a.get("entity_id") in entities, "unknown assertion entity")
        need(a.get("concept_id") in defs, "unknown assertion concept")
        for field in ("unit", "period", "basis"):
            text(a.get(field), f"assertion.{field}; use explicit not_applicable when appropriate")
        q = a.get("qualifiers")
        need(isinstance(q, dict) and all(isinstance(x, str) and isinstance(v, (str, bool, int, float))
                                       and (not isinstance(v, float) or math.isfinite(v)) for x, v in q.items()),
             "qualifiers: flat object of finite scalars required")
        for field in ("valid_from", "valid_to"):
            iso_date(a.get(field), field, True)
        need(not (a.get("valid_from") and a.get("valid_to")) or a["valid_from"] <= a["valid_to"], "reversed validity interval")
        vt = defs[a["concept_id"]]["value_type"]
        value = a.get("value")
        valid = {"number": type(value) is int or (type(value) is float and math.isfinite(value)),
                 "boolean": type(value) is bool, "string": isinstance(value, str) and bool(value.strip()),
                 "entity": isinstance(value, str) and value in entities,
                 "set": isinstance(value, list) and all(isinstance(x, str) and x for x in value)}[vt]
        need(valid, f"invalid value for {vt}")
        if vt == "set":
            need(value == sorted(set(value)), "set value must be sorted and unique")
        need(a.get("claim_kind") == "reported", "assertion.claim_kind must be 'reported' or omitted; packages store directly reported claims only, keep derived answers separate")
        need(a.get("status") in {"candidate", "accepted", "rejected"}, "invalid assertion status")
        evidence = a.get("evidence")
        need(isinstance(evidence, list) and evidence, "assertion needs evidence")
        for ev in evidence:
            need(isinstance(ev, dict) and ev.get("source_id") in sources, "unknown evidence source")
            raw = source_bytes[ev["source_id"]]
            start, end = ev.get("start_utf8"), ev.get("end_utf8")
            need(type(start) is int and type(end) is int and 0 <= start < end <= len(raw), "invalid evidence range")
            raw[:start].decode("utf-8"); raw[start:end].decode("utf-8")
            need(ev.get("span_sha256") == digest(raw[start:end]), "evidence span hash mismatch")
            text(ev.get("role"), "evidence.role")
            page = ev.get("page")
            if page is not None:
                need(type(page) is int and page > 0, "invalid evidence page")
                matches = [s for s in sources[ev["source_id"]].get("page_spans", []) if
                           s["page"] == page and s["start_utf8"] <= start < end <= s["end_utf8"]
                           and s["basis"] == ev.get("locator_basis")]
                need(bool(matches), "page claim has no matching source span")
            else:
                need(ev.get("locator_basis") == "text_range", "page-less evidence must use text_range")
        if normalized:
            need(a.get("fact_id") == fact_id(a), "fact ID mismatch")
            need(a.get("id") == assertion_id(a), "assertion ID mismatch")
            need(a["id"] not in seen, "duplicate assertion ID")
            seen.add(a["id"])
        reviews = a.get("reviews", [])
        need(isinstance(reviews, list), "reviews must be list")
        for review in reviews:
            need(isinstance(review, dict) and review.get("decision") in {"accepted", "rejected"}, "invalid review")
            text(review.get("reviewer"), "review.reviewer")
            text(review.get("note"), "review.note")
            text(review.get("at"), "review.at")
        need(a["status"] == (reviews[-1]["decision"] if reviews else "candidate"), "status does not match review log")
    return {"sources": len(sources), "entities": len(entities), "definitions": len(defs),
            "assertions": len(assertions), "facts": len({fact_id(a) for a in assertions})}


def prepare_input(path):
    root = Path(path).resolve().parent
    k = read_json(path)
    need(isinstance(k, dict), "input must be object")
    need(isinstance(k.get("assertions"), list), "assertions: list required")
    for a in k.get("assertions", []):
        need(isinstance(a, dict), "assertion must be object")
        need(a.get("status", "candidate") == "candidate" and not a.get("reviews"), "input cannot inject review decisions")
        a["status"] = "candidate"; a["reviews"] = []
        a.setdefault("valid_from", None); a.setdefault("valid_to", None)
        a.setdefault("claim_kind", "reported")
        a["fact_id"] = fact_id(a)
        a["evidence"] = sorted(a["evidence"], key=canonical)
        a["id"] = assertion_id(a)
    # Identical input rows are idempotent; inconsistent declared identities are never guessed.
    k["assertions"] = list({a["id"]: a for a in k.get("assertions", [])}.values())
    check_knowledge(k, root)
    return k, root


def load_package(path):
    root = Path(path).resolve()
    k = read_json(root / "knowledge.json")
    run = read_json(root / "run.json")
    changes = read_json(root / "changes.json")
    need(run.get("knowledge_sha256") == digest(k), "knowledge integrity mismatch")
    need(run.get("changes_sha256") == digest(changes), "changes integrity mismatch")
    need(changes.get("current_sha256") == digest(k), "changes current version mismatch")
    counts = check_knowledge(k, root)
    need(run.get("counts") == counts, "run counts mismatch")
    expected = "".join(canonical(s) + "\n" for s in k["sources"])
    need((root / "sources.jsonl").read_text(encoding="utf-8") == expected, "source manifest mismatch")
    return k, run


def active_groups(k):
    groups = defaultdict(list)
    for a in k["assertions"]:
        if a["status"] != "rejected":
            groups[a["fact_id"]].append(a)
    return groups


def conflict_ids(k):
    return sorted(fid for fid, rows in active_groups(k).items() if len({value_key(a["value"]) for a in rows}) > 1)


def merge(base, incoming):
    need(base["scope"]["title"] == incoming["scope"]["title"], "scope.title differs; create separate knowledge package")
    need(incoming["scope"]["as_of"] >= base["scope"]["as_of"], "scope.as_of moves backwards")
    merged = copy.deepcopy(base)
    merged["scope"] = copy.deepcopy(incoming["scope"])
    additions = {}
    for name in ("entities", "definitions", "sources"):
        old = indexed(base[name], name)
        additions[name] = []
        for item in incoming[name]:
            previous = old.get(item["id"])
            if previous is not None:
                # Packaging may relocate the same source snapshot.
                omit = {"content_file"} if name == "sources" else set()
                need({k: v for k, v in previous.items() if k not in omit} ==
                     {k: v for k, v in item.items() if k not in omit},
                     f"{name} ID reused with changed definition/content: {item['id']}; preserve old ID and add a candidate")
            else:
                merged[name].append(copy.deepcopy(item)); additions[name].append(item["id"])
    prior = {a["id"] for a in base["assertions"]}
    prior_facts = {a["fact_id"] for a in base["assertions"]}
    new = [a for a in incoming["assertions"] if a["id"] not in prior]
    merged["assertions"].extend(copy.deepcopy(new))
    changes = {"new_definitions": additions["definitions"], "new_entities": additions["entities"],
               "new_sources": additions["sources"], "new_facts": sorted({a["fact_id"] for a in new} - prior_facts),
               "additional_support": [a["id"] for a in new if a["fact_id"] in prior_facts and any(
                   b["fact_id"] == a["fact_id"] and value_key(b["value"]) == value_key(a["value"]) for b in base["assertions"])],
               "new_assertions": [a["id"] for a in new], "duplicate_assertions": len(incoming["assertions"]) - len(new),
               "not_in_incoming": sorted(prior - {a["id"] for a in incoming["assertions"]}),
               "note": "Missing from this batch does not mean deleted, discontinued or withdrawn. New means new to this package."}
    return merged, changes


def cell(value):
    s = str(value) if isinstance(value, str) else canonical(value)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ").replace("\r", " ")
    return re.sub(r"([\\`*_{}\[\]()|!])", r"\\\1", s)


def render(k, changes):
    entities = {e["id"]: e for e in k["entities"]}
    definitions = {d["id"]: d for d in k["definitions"]}
    sources = {s["id"]: s for s in k["sources"]}
    conflicts = set(conflict_ids(k))
    lines = [f"# {cell(k['scope']['title'])}", "", f"As of: {k['scope']['as_of']} | Schema {SCHEMA_VERSION}", "",
             "Machine-organized source claims. Candidate definitions; no automatic business decision. / 机器整理的来源断言，定义待审。", "",
             "## Changes / 变化", "", f"- New facts / 新事实: {len(changes.get('new_facts', []))}",
             f"- Additional support / 新增支持: {len(changes.get('additional_support', []))}",
             f"- Conflicting fact groups / 冲突组: {len(changes['conflicts'])}",
             "- Absence is not deletion. / 未发现不代表废止。", "",
             "## Claims / 事实审阅", "", "| Fact ID | Subject | Concept | Value | Unit | Period | Basis / qualifiers | Validity | Status | Evidence |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for a in k["assertions"]:
        refs = []
        for ev in a["evidence"]:
            src = sources[ev["source_id"]]
            page = f" p.{ev['page']}" if ev.get("page") else ""
            refs.append(f"[{cell(src['id'])}{page}](<{src['url']}>) bytes {ev['start_utf8']}:{ev['end_utf8']}")
        status = a["status"] + (" / conflict" if a["status"] != "rejected" and a["fact_id"] in conflicts else "")
        validity = f"{a.get('valid_from') or 'unspecified'} → {a.get('valid_to') or 'unspecified'}"
        vals = [a["fact_id"], entities[a["entity_id"]]["name"], definitions[a["concept_id"]]["name"], a["value"],
                a["unit"], a["period"], a["basis"] + " " + canonical(a["qualifiers"]), validity, status]
        lines.append("| " + " | ".join(cell(x) for x in vals) + " | " + "; ".join(refs) + " |")
    lines += ["", "## Boundaries / 边界", "", "Hash/range validation checks integrity and declared alignment, not semantic entailment or source authenticity.",
              "See knowledge.json for full IDs and review history. This is not an approval or access-control service.", "",
              "## Optional feedback / 自愿反馈", "", "Found an error, want this for routine work, or need internal deployment? Generate a local feedback draft and review it before sharing.",
              "Public issues: https://github.com/huhoo/cue-awesome/issues/new . Do not post internal documents or contact details there.", ""]
    return "\n".join(lines)


def write_package(k, roots, out, changes, parent=None, operation="build"):
    dest = Path(out).resolve()
    need(not dest.exists(), "output already exists; choose a new version directory")
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".ontology-", dir=dest.parent))
    try:
        result = copy.deepcopy(k)
        (stage / "evidence").mkdir()
        for s in result["sources"]:
            src = roots[s["id"]]
            raw = src.read_bytes()
            need(digest(raw) == s["sha256"], "source changed during packaging")
            rel = "evidence/" + digest(s["id"])[:24] + ".txt"
            (stage / rel).write_bytes(raw)
            s["content_file"] = rel
        counts = check_knowledge(result, stage)
        h = digest(result)
        changes = dict(changes, baseline_sha256=parent, current_sha256=h, conflicts=conflict_ids(result))
        run = {"skill_version": VERSION, "schema_version": SCHEMA_VERSION, "operation": operation,
               "created_at": datetime.now(timezone.utc).isoformat(), "knowledge_sha256": h,
               "changes_sha256": digest(changes), "parent_sha256": parent, "counts": counts,
               "semantic_verification": "not_established_by_scripts", "billing": "not_observed_by_offline_packager"}
        for name, data in (("knowledge.json", result), ("changes.json", changes), ("run.json", run)):
            (stage / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (stage / "sources.jsonl").write_text("".join(canonical(s) + "\n" for s in result["sources"]), encoding="utf-8")
        (stage / "report.md").write_text(render(result, changes), encoding="utf-8")
        load_package(stage)
        stage.rename(dest)
        return run
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def roots_for(k, root):
    return {s["id"]: local_file(root, s["content_file"]) for s in k["sources"]}


def query(k, args):
    for field in ("valid_from", "valid_to"):
        if getattr(args, field, None) is not None:
            iso_date(getattr(args, field), field)
    matches = [a for a in k["assertions"] if a["status"] != "rejected" and all(
        getattr(args, arg, None) is None or a[field] == getattr(args, arg)
        for arg, field in (("entity", "entity_id"), ("concept", "concept_id"), ("period", "period"), ("basis", "basis"),
                           ("unit", "unit"), ("valid_from", "valid_from"), ("valid_to", "valid_to"), ("fact", "fact_id")))]
    if args.qualifiers is not None:
        q = decode_json(args.qualifiers)
        need(isinstance(q, dict), "query qualifiers must be JSON object")
        matches = [a for a in matches if canonical(a["qualifiers"]) == canonical(q)]
    ids = {a["fact_id"] for a in matches}
    state = "not_found" if not matches else "needs_scope" if len(ids) > 1 else (
        "conflict" if len({value_key(a["value"]) for a in matches}) > 1 else "found")
    source_ids = {ev["source_id"] for a in matches for ev in a["evidence"]}
    scopes = {a["fact_id"]: dict(fact_id=a["fact_id"], **key_of(a)) for a in matches}
    return {"status": state, "scopes": [scopes[fid] for fid in sorted(scopes)],
            "assertions": matches, "sources": [s for s in k["sources"] if s["id"] in source_ids],
            "note": "found means a structurally matching source claim, not independently verified truth"}


def export_okf(k, out):
    dest = Path(out)
    need(not dest.exists(), "OKF destination exists; choose a new directory")
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".okf-", dir=dest.parent))
    try:
        links = []
        for d in k["definitions"]:
            name = "concept-" + digest(d["id"])[:20] + ".md"
            # JSON-quoted scalars are valid YAML; no YAML dependency or arbitrary frontmatter injection.
            body = ["---", "type: " + json.dumps(d["kind"]), "title: " + json.dumps(d["name"], ensure_ascii=False),
                    "status: draft", "---", "", "# " + cell(d["name"]), "", cell(d["description"]), "",
                    "Definition is a candidate. No human verification is asserted.", "",
                    "Structured identity: `" + d["id"] + "`", ""]
            selected = dict(k, assertions=[a for a in k["assertions"] if a["concept_id"] == d["id"]])
            body.append(render(selected, {"conflicts": conflict_ids(selected)}))
            (stage / name).write_text("\n".join(body), encoding="utf-8")
            links.append(f"- [{cell(d['name'])}]({name})")
        (stage / "index.md").write_text("# Knowledge concepts\n\n" + "\n".join(links) + "\n", encoding="utf-8")
        stage.rename(dest)
    finally:
        if stage.exists(): shutil.rmtree(stage)
    return {"status": "exported", "concept_files": len(links), "okf_target": "0.2 core Markdown/YAML subset",
            "consumer_import_verified": False, "note": "No runtime actions, permissions or private evidence files exported."}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("build", "update"):
        q = sub.add_parser(name, help="Package host-extracted input into a new immutable directory")
        q.add_argument("input")
        if name == "update": q.add_argument("--base", required=True)
        q.add_argument("--out", required=True)
    for name in ("validate", "query", "export-okf", "feedback", "review"):
        q = sub.add_parser(name)
        q.add_argument("package")
        if name == "query":
            for field in ("entity", "concept", "period", "basis", "qualifiers", "unit", "valid-from", "valid-to", "fact"):
                q.add_argument("--" + field)
            q.add_argument("--with-evidence", action="store_true", help="Include bounded exact source excerpts")
        if name in {"export-okf", "feedback", "review"}: q.add_argument("--out", required=True)
        if name == "review":
            q.add_argument("--assertion", required=True)
            q.add_argument("--decision", required=True, choices=["accepted", "rejected"])
            q.add_argument("--reviewer", required=True)
            q.add_argument("--note", required=True)
    q = sub.add_parser("prepare", help="Resolve exact quotes into validated byte evidence; no model or parser call")
    q.add_argument("draft"); q.add_argument("--out", required=True)
    q = sub.add_parser("brief", help="Create a local searchable HTML/Markdown brief with evidence previews")
    q.add_argument("package"); q.add_argument("--base"); q.add_argument("--out", required=True)
    q = sub.add_parser("demo", help="Run the complete synthetic build/update/brief example without an API key")
    q.add_argument("--out", required=True)
    args = p.parse_args(argv)
    try:
        if args.command in {"prepare", "brief", "demo"}:
            import experience
            if args.command == "prepare": result = experience.prepare(args.draft, args.out)
            elif args.command == "brief": result = experience.brief(args.package, args.out, args.base)
            else: result = experience.demo(args.out)
        elif args.command in {"build", "update"}:
            k, root = prepare_input(args.input)
            roots = roots_for(k, root)
            if args.command == "build":
                changes = {"new_facts": sorted({a["fact_id"] for a in k["assertions"]}),
                           "new_assertions": [a["id"] for a in k["assertions"]], "new_definitions": [d["id"] for d in k["definitions"]]}
                result = write_package(k, roots, args.out, changes)
            else:
                base, run = load_package(args.base)
                combined, changes = merge(base, k)
                roots = dict(roots_for(base, Path(args.base)), **roots)
                result = write_package(combined, roots, args.out, changes, run["knowledge_sha256"], "update")
        else:
            k, run = load_package(args.package)
            if args.command == "validate":
                result = {"status": "valid", "counts": run["counts"], "semantic_verification": "not_established_by_scripts"}
            elif args.command == "query":
                result = query(k, args)
                if args.with_evidence:
                    import experience
                    result["evidence_previews"] = experience.previews(k, Path(args.package), result["assertions"])
            elif args.command == "export-okf": result = export_okf(k, args.out)
            elif args.command == "feedback":
                out = Path(args.out); need(not out.exists(), "feedback output exists")
                data = {"skill_version": VERSION, "counts": run["counts"], "intent": "",
                        "task_description_without_private_details": "", "failure_stage": "", "repeat_use": None,
                        "repeat_update_completed": None, "review_minutes_self_reported": None, "next_workflow": "",
                        "notice": "Local draft only. Review and explicitly choose whether to share. No source URLs, raw claims, contacts or telemetry included."}
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                result = {"status": "local_draft_created", "sent": False}
            elif args.command == "review":
                rows = [a for a in k["assertions"] if a["id"] == args.assertion]
                need(len(rows) == 1, "unknown assertion ID")
                a = rows[0]
                a["reviews"].append({"decision": args.decision, "reviewer": text(args.reviewer, "reviewer"),
                                     "note": text(args.note, "note"), "at": datetime.now(timezone.utc).isoformat()})
                a["status"] = args.decision
                result = write_package(k, roots_for(k, Path(args.package)), args.out, {"reviewed_assertions": [a["id"]]},
                                       run["knowledge_sha256"], "review")
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (Invalid, OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
