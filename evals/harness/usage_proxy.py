"""Local usage-logging proxy for the dandy agent.

dandy does not surface the API's `usage` field, so the dandy entrypoint
points its LLM config at this proxy (127.0.0.1:8787) instead of stratus
directly. The proxy forwards requests verbatim and appends each response's
`usage` object to /workdir/usage.jsonl for the harness to sum.
"""

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = f"{os.environ['AI_API_HOST']}:443"
API_KEY = os.environ['AI_API_KEY']
OUT_PATH = os.path.join(os.environ.get('PROXY_LOG_DIR', '/workdir'), 'usage.jsonl')


class UsageProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        upstream_request = urllib.request.Request(
            f'{UPSTREAM}{self.path}',
            data=body,
            method='POST',
            headers={
                'Content-Type': self.headers.get('Content-Type', 'application/json'),
                'Authorization': f'Bearer {API_KEY}',
            },
        )
        with urllib.request.urlopen(upstream_request, timeout=600) as upstream_response:
            payload = upstream_response.read()
            status = upstream_response.status
            content_type = upstream_response.headers.get('Content-Type')
        try:
            usage = json.loads(payload).get('usage')
        except (ValueError, AttributeError):
            usage = None
        if usage:
            with open(OUT_PATH, 'a') as f:
                f.write(json.dumps({'path': self.path, **usage}) + '\n')
        self.send_response(status)
        if content_type:
            self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8787), UsageProxyHandler).serve_forever()
