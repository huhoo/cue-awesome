#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cue_connectivity_check.py —— 一条命令跑完「通道到底连没连上」这一层（零改动地复用 M332 那块面内命令的语义）。

它做三件事，全按 README 连通那一节的现值走，不在本件里另立第二套判据：
  1. 匿名 GET 目录（本件唯一的目录入口，默认 https://cuecue.cn/api/mcp-catalog，可用 --catalog-url 换）；
  2. 按 --domain 给的域 id 从返回里取该域 routing 里的 url 字段——取的是对象里那个可发请求的 url，不是整枚 routing 对象；
  3. 显式带 --post 时，才用本地凭据设施里那把 key 向那个 url 发一次 tools/list，把 HTTP 状态码与返回体里 result.tools 的枚数打出来。

缺省一个包都不发：不带 --post 时本件只走到「取到该域 routing 里的 url」为止，并印一行提示。
这么定的理由：「默认即发」会让「忘带开关」这个形状一直存在；把发与不发做成显式选择，漏手的人最多是少跑一步，不会多打一次出站。

判据在哪：通过与否的权威表述在该包 README 的连通那一节（同包英文面同义），本件只负责执行与把现场值打出来，
不在这里复述一遍数字条件——一处事实两处真值正是要防的。

退码（每条都响亮、零 Traceback）：
  0  取到该域 routing 里的 url；带 --post 时还把 HTTP 码与 result.tools 枚数打了出来
  0  --list 与缺省（不带 --post）两形同样退 0：一次 POST 都不发
  1  取不到：域 id 不在目录现值里／该域没有 routing／routing 在场却没有 url／本地凭据缺位／请求没发出去
  2  用法错：既没给 --domain 也没给 --list

零计费：目录那一次是匿名只读；tools/list 是 MCP 的清单方法，不取数据、不计消耗；本件缺省不发任何包。
本件不写死任何域名清单、工具名或 routing 值——域 id 与 url 一律从目录当场返回里取。
凭据只从环境变量读（CUE_API_KEY，或宿主凭据设施注入的等价变量），本件永不打印它的值。
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

CATALOG_DEFAULT = "https://cuecue.cn/api/mcp-catalog"
ACCEPT = "application/json, text/event-stream"


def die(msg: str, code: int = 1) -> int:
    """一句人话出口——绝不抛异常，让下一位照着 Traceback 查错方向。"""
    print(msg, file=sys.stderr)
    return code


def read_catalog(url: str, path: str, timeout: int):
    """目录来源：--catalog-file 给路径时读本地快照（离线靶用），否则匿名 GET。返回 (文档, 来源说明)。"""
    if path:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh), "本地快照 %s" % path
        except (OSError, ValueError) as err:
            raise SystemExit(die("读不到目录快照：%s（%s: %s）" % (path, type(err).__name__, str(err)[:80])))
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8")), "匿名 GET %s" % url


def rows_of(doc):
    """从返回里取域清单——形状不认识时也要一句人话，不许 KeyError。"""
    if not isinstance(doc, dict):
        raise SystemExit(die("目录返回不是对象（顶层类型＝%s）——换源或换 --catalog-file" % type(doc).__name__))
    data = doc.get("data")
    rows = data.get("domains") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise SystemExit(die("目录返回里没有 data.domains 数组（顶层键＝%s）——本件按那形读，换源请直说" % ", ".join(sorted(doc))))
    return [r for r in rows if isinstance(r, dict)]


def routing_url(row):
    """取该域 routing 里的 url 字段；routing 在场但缺 url 时返回 None，由调用方出一句人话。"""
    routing = row.get("routing")
    if not isinstance(routing, dict):
        return None
    url = routing.get("url")
    return url if isinstance(url, str) and url else None


def main() -> int:
    ap = argparse.ArgumentParser(
        description="一条命令跑完连通自检：从目录现取该域 routing 里的 url；要真发那一次 tools/list 请显式带 --post。",
        epilog="判据的权威表述在该包 README 连通那一节，本件只执行、不复述。零计费：目录匿名只读，tools/list 不取数据。")
    ap.add_argument("--domain", help="要连的域 id（取值请从 --list 的现场输出里挑，本件不写死域清单）")
    ap.add_argument("--list", action="store_true", help="只列在场域 id、external_status 与 routing 里的 url，不发 POST")
    ap.add_argument("--catalog-url", default=CATALOG_DEFAULT, help="目录入口（默认本件唯一那处；换源时传这里）")
    ap.add_argument("--catalog-file", help="离线：改读本地目录快照（受控靶用），不发网络")
    ap.add_argument("--post", action="store_true", help="显式发那一次 tools/list；不带这一项本件一个包都不发（缺省即零发包）")
    ap.add_argument("--timeout", type=int, default=20, help="单次请求超时秒数（默认 20）")
    args = ap.parse_args()

    try:
        doc, src = read_catalog(args.catalog_url, args.catalog_file, args.timeout)
    except (urllib.error.URLError, OSError, ValueError) as err:
        return die("目录取不回：%s（%s）" % (src, str(err)[:120]))

    rows = rows_of(doc)
    listed = []
    for r in rows:
        rid = str(r.get("id", ""))
        status = str(r.get("external_status", ""))
        url = routing_url(r)
        listed.append((rid, status, url))

    if args.list:
        print("目录来源＝%s｜在场域 %d 枚（id／external_status／routing 里的 url）" % (src, len(listed)))
        for rid, status, url in listed:
            print("  %-16s %-12s %s" % (rid or "(缺 id)", status or "(缺状态)", url or "(routing 里没有 url)"))
        print("下一步：python3 -B scripts/cue_connectivity_check.py --domain <上面那一列里的 id>；要真发那一次包，再显式加 --post")
        return 0

    if not args.domain:
        print("--domain 没给（也不带 --list）——本件不猜域。在场域如下，挑一个再跑：")
        for rid, status, url in listed:
            print("  %-16s %-12s %s" % (rid or "(缺 id)", status or "(缺状态)", url or "(routing 里没有 url)"))
        return 2

    hit = [x for x in listed if x[0] == args.domain]
    if not hit:
        return die("未取到：目录现值里没有 id＝%s 这一枚（在场 %d 枚，先跑 --list 看清单）" % (args.domain, len(listed)))
    rid, status, url = hit[0]
    if url is None:
        if status and status != "live":
            return die("未取到：域 %s 的 external_status＝%s，目录这一枚没给 routing 里的 url——非 live 域本件不装也不承诺" % (rid, status))
        return die("未取到：域 %s 的 routing 在场但没有 url 字段（键＝%s）——本件要的是其中那个可发请求的 url，不猜别的键" % (
            rid, ", ".join(sorted((next((r for r in rows if str(r.get("id", "")) == rid) or {}).get("routing") or {})) or "(routing 不是对象)")))

    if not args.post:
        print("域 %s｜external_status=%s｜取到 routing 里的 url=%s" % (rid, status, url))
        print("缺省零发包：本件到此为止，没有发 POST。要真跑连通那一步，请显式加 --post。")
        return 0

    key = os.environ.get("CUE_API_KEY", "").strip()
    if not key:
        return die("取到了 routing 里的 url，但本地凭据缺位：环境变量 CUE_API_KEY 没读到——本件不打印 key，也不替你写进任何文件")
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": "Bearer " + key, "Accept": ACCEPT, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            code, raw = resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        return die("POST 到 %s 实得 HTTP %s——连通未过（判据见该包 README 连通那一节）；错误体首行：%s" % (
            url, err.code, (err.read().decode("utf-8", "replace").splitlines() or ["(空)"])[0][:120]))
    except (urllib.error.URLError, OSError, ValueError) as err:
        return die("POST 发不出去（%s）：连接报错不等于域无数据——如实报，只重试错误标明可重试的部分" % str(err)[:120])

    payload = raw
    doc = None
    try:
        doc = json.loads(payload.strip())
    except ValueError:
        # MCP 的 streamable-http 常以 SSE 回：event: 行＋data: 行，取第一条能解析的 data: 载荷
        for line in raw.splitlines():
            if line.startswith("data:"):
                try:
                    doc = json.loads(line[5:].strip())
                    break
                except ValueError:
                    continue
    if doc is None:
        return die("POST 实得 HTTP %s，但返回体既不是单个 JSON、也没有可解析的 data: 行（首 60 字：%s）——按现场回字判，别按本件的解析判" % (code, raw[:60]))
    tools = (doc.get("result") or {}).get("tools") if isinstance(doc, dict) else None
    n = len(tools) if isinstance(tools, list) else 0
    print("域 %s｜external_status=%s｜routing 里的 url=%s" % (rid, status, url))
    print("POST tools/list 实得 HTTP %s｜返回体里 result.tools 枚数=%s（枚数只在此行，判据以该包 README 连通那一节为准）" % (code, n if isinstance(tools, list) else "(返回体里没有 tools 数组)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
