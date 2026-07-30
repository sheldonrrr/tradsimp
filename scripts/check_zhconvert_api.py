#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Offline checks for the ZhConvert API client. No network request is made."""

import importlib.util
import io
import json
import os
import socket
import sys
import types
from urllib.error import HTTPError, URLError


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def load_client():
    package = types.ModuleType('calibre_plugins.chinese_text_conversion')
    package.PLUGIN_VERSION = 'test'
    sys.modules.setdefault('calibre_plugins', types.ModuleType('calibre_plugins'))
    sys.modules['calibre_plugins.chinese_text_conversion'] = package
    path = os.path.join(REPO_ROOT, 'zhconvert_api.py')
    spec = importlib.util.spec_from_file_location('zhconvert_api_under_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.closed = False

    def read(self):
        return self.payload

    def close(self):
        self.closed = True


def response_opener(payload, captured=None):
    encoded = json.dumps(payload, ensure_ascii=False).encode('utf-8')

    def open_request(request, timeout):
        if captured is not None:
            captured['request'] = request
            captured['timeout'] = timeout
        return FakeResponse(encoded)

    return open_request


def assert_error(client, kind, opener, text='测试'):
    try:
        client.convert_text(text, 'Traditional', urlopen_func=opener)
    except client.ZhConvertError as err:
        assert err.kind == kind, (err.kind, kind)
    else:
        raise AssertionError('Expected ZhConvertError: ' + kind)


def main():
    client = load_client()
    captured = {}
    result = client.convert_text(
        '内存不足',
        'Taiwan',
        urlopen_func=response_opener({
            'code': 0,
            'data': {
                'converter': 'Taiwan',
                'text': '記憶體不足',
                'usedModules': ['Unit', 'Typo'],
            },
            'revisions': {'build': 'dict-test'},
            'execTime': 0.01,
        }, captured),
    )
    assert result == {
        'text': '記憶體不足',
        'converter': 'Taiwan',
        'used_modules': ['Unit', 'Typo'],
        'revision': 'dict-test',
        'exec_time': 0.01,
    }
    request_payload = json.loads(captured['request'].data.decode('utf-8'))
    assert request_payload == {'text': '内存不足', 'converter': 'Taiwan'}
    assert captured['request'].full_url == client.ZHCONVERT_URL
    assert captured['timeout'] == client.ZHCONVERT_TIMEOUT_SECONDS

    assert_error(
        client, 'api_error',
        response_opener({'code': 12, 'msg': 'conversion failed'}))
    assert_error(
        client, 'invalid_response',
        lambda _request, timeout: FakeResponse(b'not-json'))

    def rate_limited(request, timeout):
        raise HTTPError(request.full_url, 429, 'Too Many Requests', {}, io.BytesIO())

    assert_error(client, 'rate_limited', rate_limited)

    def timed_out(_request, timeout):
        raise URLError(socket.timeout('timed out'))

    assert_error(client, 'timeout', timed_out)

    oversized = '汉' * (client.ZHCONVERT_MAX_INPUT_BYTES + 1)
    assert_error(
        client, 'text_too_long',
        lambda _request, timeout: None,
        text=oversized,
    )
    print('ZhConvert API checks passed (offline)')


if __name__ == '__main__':
    main()
