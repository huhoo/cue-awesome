#!/usr/bin/env python3
"""offline stand-in for the Cue Omni Reader MCP Bridge (stdio JSON-RPC), for the regression tests only.
Serves parse / get_parse_status / read_result from a sanitized fixture with the real 1.8.x response shapes; no network, no key."""
import json, sys
fx = json.load(open(sys.argv[1], encoding='utf-8')); log = sys.argv[2] if len(sys.argv) > 2 else None
CHUNK = 15                                     # tiny chunks (characters, like the real Bridge never splits a UTF-8 char) to exercise next_cursor paging
def chunks(part):
    t = fx['parts'][part]; return [t[i:i + CHUNK] for i in range(0, len(t), CHUNK)] or ['']
def call(name, a):
    if log: open(log, 'a').write(json.dumps({'tool': name, 'args': a}) + '\n')
    if name == 'parse': return fx['parse_response']
    if name == 'get_parse_status': return fx['final_response']
    if name == 'read_result':
        part, i = a['cursor'].split(':')[1], int(a['cursor'].split(':')[2]); cs = chunks(part)
        if a.get('result_id') != fx['final_response']['result']['result_id'] or i >= len(cs):
            return {'status': 'failed', 'error': {'code': 'INVALID_RESULT_CURSOR', 'billed': False}}
        return {'status': 'completed', 'result': {'part': part, 'offset': i * CHUNK, 'text': cs[i],
                'next_cursor': f'cursor_fake:{part}:{i + 1}' if i + 1 < len(cs) else None}}
    return {'status': 'failed', 'error': {'code': 'UNKNOWN_TOOL'}}
for line in sys.stdin:
    m = json.loads(line)
    if 'id' not in m: continue
    if m['method'] == 'initialize': r = {'protocolVersion': '2025-06-18', 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'fake-omni', 'version': '0'}}
    else:
        sc = call(m['params']['name'], m['params'].get('arguments') or {}); r = {'content': [{'type': 'text', 'text': json.dumps(sc)}], 'structuredContent': sc}
    sys.stdout.write(json.dumps({'jsonrpc': '2.0', 'id': m['id'], 'result': r}) + '\n'); sys.stdout.flush()
