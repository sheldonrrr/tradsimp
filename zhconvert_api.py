# -*- coding: utf-8 -*-

__license__ = 'GPL 3'

import json
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from calibre_plugins.chinese_text_conversion import PLUGIN_VERSION


ZHCONVERT_URL = 'https://api.zhconvert.org/convert'
ZHCONVERT_SITE_URL = 'https://zhconvert.org'
ZHCONVERT_TIMEOUT_SECONDS = 30
ZHCONVERT_MAX_INPUT_BYTES = 64 * 1024

ZHCONVERT_CONVERTERS = (
    ('Traditional', 'ZhConvert mode Traditional'),
    ('Simplified', 'ZhConvert mode Simplified'),
    ('Taiwan', 'ZhConvert mode Taiwan'),
    ('Hongkong', 'ZhConvert mode Hong Kong'),
    ('China', 'ZhConvert mode Mainland'),
    ('WikiTraditional', 'ZhConvert mode Wiki Traditional'),
    ('WikiSimplified', 'ZhConvert mode Wiki Simplified'),
)
ZHCONVERT_CONVERTER_IDS = frozenset(item[0] for item in ZHCONVERT_CONVERTERS)

# Fixed glyph demos (not UI-translated) so regional wording stays visible.
ZHCONVERT_MODE_EXAMPLES = {
    'Traditional': '软件 → 軟件 · 内存 → 內存 · 计算机 → 計算機',
    'Simplified': '軟體 → 软体 · 記憶體 → 记忆体 · 計算機 → 计算机',
    'Taiwan': '软件 → 軟體 · 内存 → 記憶體 · 网络 → 網路',
    'Hongkong': '软件 → 軟件 · 什么 → 甚麼 · 网络 → 網絡',
    'China': '軟體 → 软件 · 記憶體 → 内存 · 網路 → 网络',
    'WikiTraditional': '服务器 → 伺服器 · 数据库 → 資料庫 · 计算机 → 電腦',
    'WikiSimplified': '伺服器 → 服务器 · 資料庫 → 数据库 · 電腦 → 计算机',
}


class ZhConvertError(Exception):
    """Structured error suitable for translation by the UI layer."""

    def __init__(self, kind, detail=''):
        self.kind = kind
        self.detail = str(detail or '')
        super().__init__(self.detail or kind)


def _decode_response(response):
    try:
        payload = response.read()
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8')
        result = json.loads(payload)
    except (UnicodeDecodeError, ValueError, TypeError) as err:
        raise ZhConvertError('invalid_response', err)

    if not isinstance(result, dict):
        raise ZhConvertError('invalid_response')
    if result.get('code') != 0:
        raise ZhConvertError('api_error', result.get('msg') or result.get('code'))

    data = result.get('data')
    if not isinstance(data, dict) or not isinstance(data.get('text'), str):
        raise ZhConvertError('invalid_response')
    revisions = result.get('revisions')
    if not isinstance(revisions, dict):
        revisions = {}
    used_modules = data.get('usedModules')
    if not isinstance(used_modules, list):
        used_modules = []
    return {
        'text': data['text'],
        'converter': str(data.get('converter') or ''),
        'used_modules': [str(item) for item in used_modules],
        'revision': str(revisions.get('build') or ''),
        'exec_time': result.get('execTime'),
    }


def convert_text(text, converter, timeout=ZHCONVERT_TIMEOUT_SECONDS,
                 urlopen_func=None):
    """Convert one short plain-text input through the public ZhConvert API."""
    if not isinstance(text, str) or not text.strip():
        raise ZhConvertError('empty_text')
    if converter not in ZHCONVERT_CONVERTER_IDS:
        raise ZhConvertError('unsupported_converter', converter)

    text_bytes = text.encode('utf-8')
    if len(text_bytes) > ZHCONVERT_MAX_INPUT_BYTES:
        raise ZhConvertError('text_too_long', len(text_bytes))

    body = json.dumps(
        {'text': text, 'converter': converter},
        ensure_ascii=False,
        separators=(',', ':'),
    ).encode('utf-8')
    request = Request(
        ZHCONVERT_URL,
        data=body,
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'User-Agent': 'Chinese-Conversion-Calibre/{}'.format(PLUGIN_VERSION),
        },
        method='POST',
    )
    opener = urlopen_func or urlopen
    try:
        response = opener(request, timeout=timeout)
        try:
            return _decode_response(response)
        finally:
            close = getattr(response, 'close', None)
            if close is not None:
                close()
    except ZhConvertError:
        raise
    except HTTPError as err:
        kind = 'rate_limited' if err.code == 429 else 'http_error'
        raise ZhConvertError(kind, err.code)
    except (socket.timeout, TimeoutError) as err:
        raise ZhConvertError('timeout', err)
    except URLError as err:
        reason = getattr(err, 'reason', err)
        if isinstance(reason, (socket.timeout, TimeoutError)):
            raise ZhConvertError('timeout', reason)
        raise ZhConvertError('network_error', reason)
    except OSError as err:
        raise ZhConvertError('network_error', err)
