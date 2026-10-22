#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m393_key_send_probe.py —— 凭据外发两关的反证尺：证明「没发」，不是听件自己说「没发」。

一条命令重跑：python3 -B scripts/m393_key_send_probe.py
  射程＝盘上现扫的每枚带 scripts/cue_connectivity_check.py 的包（枚数由名册现算，不写死）。
  每枚跑五格，缺一格即那枚不过：
    T1 真 socket 靶：把 http://127.0.0.1:PORT/mcp 写进目录快照的 routing.url，带 --post 且环境里备一把哨兵 key
       ⇒ 件必须拒发（退 6），而**靶自己数到的请求数＝0、数到的 Authorization 头数＝0**。
          「没发」由靶的计数说话，不由件里那句 print 说话。
    T2 观察力自证：探针自己向同一枚靶发一次 GET ⇒ 靶计数必须 +1。
       这一格不测件，测靶——防「靶聋了所以什么都测不到」那种假绿；T1 的那个 0 全靠它有牙。
    T3 https 但非授权 host（传输层打桩）⇒ 退 6 且 urlopen 调用次数＝0（key 连被读的机会都没有）。
    T4 目录入口本身是 http（--catalog-url）⇒ 退 7 且调用次数＝0（换源这一路同样要过 https 关）。
    T5 正控：https＋授权 host，打桩返回 200 且 result.tools 非空 ⇒ 退 0 且调用次数＝1
       （证今天那条行为没被这关改坏；也给 T1／T3／T4 的「0」上牙——不是尺子根本发不出去）。
  授权后缀的缺省值不硬编进本尺：由被检件头 CATALOG_DEFAULT 的 host 现推，尺只按「非该后缀即拒、是则照旧」判形。
  退码：0 全过；1 有不合（逐枚逐格点名）；3 取值域故障（一枚都不在场——不读成「零违例」）。
零网络：所有靶都在 127.0.0.1 或打桩层；本尺不向任何外部主机发一个包；哨兵 key 的值不打印、不落盘。
"""
from __future__ import annotations

import argparse
import contextlib
import http.server
import importlib.util
import io
import json
import os
import socketserver
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SENTINEL = "skh-SENTINEL-DO-NOT-PRINT"
WORK = Path(os.environ.get("M393_TMP", "/data/sdc1/work/tmp/awesome-skill/m393/run"))


class RecordingHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.hits.append(("GET", self.headers.get("Authorization")))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def do_POST(self):
        self.server.hits.append(("POST", self.headers.get("Authorization")))
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "t"}]}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass


def start_target():
    srv = Server(("127.0.0.1", 0), RecordingHandler)
    srv.hits = []
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def write_catalog(path, url):
    Path(path).write_text(json.dumps({"data": {"domains": [
        {"id": "demo", "external_status": "live", "routing": {"url": url}}]}}, ensure_ascii=False), encoding="utf-8")


def load_module(script):
    spec = importlib.util.spec_from_file_location("ccc_" + script.parent.parent.name.replace("-", "_"), script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeResp:
    def __init__(self, payload, status=200):
        self._p, self.status = payload.encode("utf-8"), status

    def read(self):
        return self._p

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def authorize_suffix(host):
    parts = [x for x in (host or "").split(".") if x]
    return ".".join(parts[-2:]) if len(parts) >= 2 else (parts[-1] if parts else "")


def mocked_run(mod, script, argv, tmp):
    """在这一格里把传输层打桩，返回 (退码, 被调用的 Request 清单, 输出)。打桩＝零网络，也照样数得出发没发。"""
    calls = []

    def fake_urlopen(req, timeout=None, **kw):
        calls.append(req)
        if isinstance(req, str):
            return FakeResp(json.dumps({"data": {"domains": []}}))
        return FakeResp(json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "t"}]}}))

    real = urllib.request.urlopen
    urllib.request.urlopen = fake_urlopen
    old_argv, old_key = sys.argv, os.environ.get("CUE_API_KEY")
    os.environ["CUE_API_KEY"] = SENTINEL
    sys.argv = [str(script)] + argv
    buf = io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            code = mod.main()
    except SystemExit as err:
        code = err.code if isinstance(err.code, int) else 1
    except Exception as err:
        code = None
        buf.write("（打桩里抛了异常，形制＝%s：这一格不算合，也不算绿）" % type(err).__name__)
    finally:
        sys.argv = old_argv
        urllib.request.urlopen = real
        if old_key is None:
            os.environ.pop("CUE_API_KEY", None)
        else:
            os.environ["CUE_API_KEY"] = old_key
    out = buf.getvalue().replace(SENTINEL, "（哨兵值，已掩）")
    return code, calls, out


def header_count(calls):
    n = 0
    for req in calls:
        names = req.header_names() if hasattr(req, "header_names") else list(getattr(req, "headers", {}) or {})
        n += sum(1 for h in names if str(h).lower() == "authorization")
    return n


def run_case(pkg, script):
    res = []
    srv, port = start_target()
    tmp = Path(tempfile.mkdtemp(prefix="%s-" % pkg, dir=str(WORK)))
    try:
        # T1 真 socket 靶：http 目的地 ⇒ 拒发，且靶一个请求都数不到
        cat = tmp / "catalog-http.json"
        write_catalog(cat, "http://127.0.0.1:%d/mcp" % port)
        env = dict(os.environ, CUE_API_KEY=SENTINEL, TMPDIR=str(tmp))
        try:
            p = subprocess.run([sys.executable, "-B", str(script), "--catalog-file", str(cat),
                                "--domain", "demo", "--post"], capture_output=True, text=True, env=env, timeout=60)
            rc = p.returncode
            out = (p.stdout + p.stderr).replace(SENTINEL, "（哨兵值，已掩）")
        except (subprocess.SubprocessError, OSError) as err:
            rc, out = None, "子进程没跑起来（%s）" % type(err).__name__
        hits, auths = len(srv.hits), sum(1 for _, a in srv.hits if a)
        res.append(("T1 真靶 http 拒发", rc == 6 and hits == 0 and auths == 0,
                    "rc=%s（期望 6）｜靶数到请求=%d（期望 0）｜靶数到 Authorization 头=%d（期望 0）｜件回字首行=%s"
                    % (rc, hits, auths, (out.splitlines() or ["(无输出)"])[0][:70])))
        # T2 靶观察力自证
        before = len(srv.hits)
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/probe" % port, timeout=10) as resp:
                resp.read()
        except (urllib.error.URLError, OSError):
            pass
        gained = len(srv.hits) - before
        res.append(("T2 靶没聋", gained == 1, "探针自发的 GET 被靶数到 +%d（期望 +1）" % gained))

        mod = load_module(script)
        suffix = authorize_suffix(urllib.parse.urlsplit(mod.CATALOG_DEFAULT).hostname or "")
        good = "https://mcp.%s/mcp" % suffix if suffix else "https://mcp.invalid/mcp"

        # T3 https 非授权 host
        cat3 = tmp / "catalog-t3.json"
        write_catalog(cat3, "https://evil-not-authorized.example.net/mcp")
        code3, calls3, out3 = mocked_run(mod, script, ["--catalog-file", str(cat3), "--domain", "demo", "--post"], tmp)
        res.append(("T3 https 非授权 host", code3 == 6 and not calls3,
                    "rc=%s（期望 6）｜urlopen 调用=%d（期望 0）｜其中带 Authorization=%d" % (code3, len(calls3), header_count(calls3))))
        # T4 目录入口非 https
        code4, calls4, out4 = mocked_run(mod, script,
                                         ["--catalog-url", "http://%s/api/mcp-catalog" % (suffix or "x.invalid"),
                                          "--domain", "demo"], tmp)
        res.append(("T4 目录入口非 https", code4 == 7 and not calls4,
                    "rc=%s（期望 7）｜urlopen 调用=%d（期望 0）" % (code4, len(calls4))))
        # T5 正控：授权 https host 照旧通
        cat5 = tmp / "catalog-t5.json"
        write_catalog(cat5, good)
        code5, calls5, out5 = mocked_run(mod, script, ["--catalog-file", str(cat5), "--domain", "demo", "--post"], tmp)
        res.append(("T5 正控授权 host 照旧通", code5 == 0 and len(calls5) == 1,
                    "rc=%s（期望 0）｜urlopen 调用=%d（期望 1；这一格给上面三格的「0」上牙）" % (code5, len(calls5))))
    finally:
        srv.shutdown()
        srv.server_close()
        for f in sorted(tmp.glob("*")):
            try:
                f.unlink()
            except OSError:
                pass
        try:
            tmp.rmdir()
        except OSError:
            pass
    return res


def main():
    ap = argparse.ArgumentParser(description="凭据外发两关的反证尺（零网络；靶在 127.0.0.1 或打桩层）")
    ap.add_argument("--root", default=str(REPO), help="仓根（默认本仓；反证可指副本）")
    ap.add_argument("--only", help="只跑某一枚（调试用；末行的名册仍按被扫的那一组报）")
    a = ap.parse_args()
    root = Path(a.root)
    if not root.is_dir():
        print("3 取值域故障：--root 取不到目录 %s（不读成「零违例」）" % root)
        return 3
    WORK.mkdir(parents=True, exist_ok=True)
    pkgs = packages = sorted(p.parent.parent.name for p in root.glob("*/scripts/cue_connectivity_check.py"))
    if not pkgs:
        print("3 取值域故障：%s 名下扫不到任何 cue_connectivity_check.py（名册为空，不读成「全过」）" % root)
        return 3
    if a.only:
        pkgs = [p for p in pkgs if p == a.only]
        if not pkgs:
            print("3 取值域故障：--only 那枚不在名册里（名册=%s）" % "、".join(sorted(packages)))
            return 3
    rows, passed = [], 0
    for pkg in pkgs:
        script = root / pkg / "scripts" / "cue_connectivity_check.py"
        if not script.is_file():
            rows.append((pkg, [("整枚不可判", False, "脚本不在场")]))
            continue
        try:
            res = run_case(pkg, script)
        except Exception as err:
            res = [("整枚不可判", False, "打桩环境起不来：%s" % type(err).__name__)]
        rows.append((pkg, res))
        if res and all(ok for _, ok, _ in res):
            passed += 1
    for pkg, res in rows:
        bad = [n for n, ok, _ in res if not ok]
        print("%-22s 格=%d｜合=%d｜不合=%s" % (pkg, len(res), sum(1 for _, ok, _ in res if ok), "、".join(bad) or "无"))
        for name, ok, note in res:
            if not ok:
                print("     不合 %-24s %s" % (name, note))
    total = len(rows)
    print("----")
    print("件数=%d（由盘上现算）｜过靶=%d｜不过=%d｜每枚格数=%d" % (
        total, passed, total - passed, len(rows[0][1]) if rows else 0))
    return 0 if total and passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
