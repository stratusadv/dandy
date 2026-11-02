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

try:
    # The proxy runs with the dandy tree on PYTHONPATH (see entrypoints/dandy.sh),
    # so the estimate uses the framework's own estimator. If the import fails
    # the proxy still logs real usage, just without the estimate.
    from dandy.domain.message.message import Message
except Exception:  # pragma: no cover
    Message = None

UPSTREAM = f'{os.environ["AI_API_HOST"]}:443'
API_KEY = os.environ['AI_API_KEY']
OUT_PATH = os.path.join(os.environ.get('PROXY_LOG_DIR', '/workdir'), 'usage.jsonl')


def _message_stats(messages: list[dict]) -> dict:
    """Component counts behind the estimator, for regressing real API counts.

    Mirrors the traversal in Message.estimated_token_count (dandy/domain/message/
    message.py) plus the character-class split of get_estimated_token_count_for_string
    (dandy/domain/tokens/estimate.py), so a linear regression of the API's
    prompt_tokens against these columns recovers the per-component token costs.
    """
    stats = {
        'est_messages': len(messages),
        'est_tool_calls': 0,
        'est_tool_call_ids': 0,
        'est_strings': 0,
        'est_alpha': 0,
        'est_digit': 0,
        'est_symbol': 0,
        'est_space': 0,
        'est_other': 0,
        'est_images': 0,
    }

    def count_string(text: str) -> None:
        if not text:
            return
        stats['est_strings'] += 1
        for character in text:
            if not character.isascii():
                stats['est_other'] += 1
            elif character.isalpha():
                stats['est_alpha'] += 1
            elif character.isdigit():
                stats['est_digit'] += 1
            elif character.isspace():
                stats['est_space'] += 1
            else:
                stats['est_symbol'] += 1

    for message in messages:
        if message.get('tool_call_id'):
            stats['est_tool_call_ids'] += 1
            count_string(message['tool_call_id'])

        tool_calls = message.get('tool_calls')
        if tool_calls:
            stats['est_tool_calls'] += len(tool_calls)
            for tool_call in tool_calls:
                count_string(tool_call.get('id') or '')
                function = tool_call.get('function') or {}
                count_string(function.get('name') or '')
                arguments = function.get('arguments')
                count_string(arguments if isinstance(arguments, str) else str(arguments or ''))
            continue

        content = message.get('content')
        if isinstance(content, str):
            count_string(content)
        elif isinstance(content, list):
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get('type') == 'text':
                    count_string(part.get('text') or '')
                elif part.get('type') == 'image_url':
                    stats['est_images'] += 1

    return stats


def estimated_prompt_tokens(body: bytes) -> dict | None:
    try:
        messages = json.loads(body).get('messages') or []
        stats = _message_stats(messages)
        stats['estimated_prompt_tokens'] = sum(
            Message.model_validate(message).estimated_token_count for message in messages
        )
        return stats
    except Exception:
        return None


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
            record = {'path': self.path, **usage}
            record.update(estimated_prompt_tokens(body) or {})
            with open(OUT_PATH, 'a') as f:
                f.write(json.dumps(record) + '\n')
        self.send_response(status)
        if content_type:
            self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8787), UsageProxyHandler).serve_forever()
