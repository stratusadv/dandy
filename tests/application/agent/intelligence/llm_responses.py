from dandy.infrastructure.http.intel import HttpResponseIntel


def tool_call_response(tool_name: str, arguments: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200,
        json_data={
            'choices': [
                {
                    'message': {
                        'content': None,
                        'tool_calls': [
                            {
                                'id': 'call_1',
                                'type': 'function',
                                'function': {'name': tool_name, 'arguments': arguments},
                            }
                        ],
                    }
                }
            ]
        },
    )


def content_response(content: str) -> HttpResponseIntel:
    return HttpResponseIntel(
        status_code=200, json_data={'choices': [{'message': {'content': content}}]}
    )
