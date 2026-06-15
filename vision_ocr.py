# -*- coding: utf-8 -*-

__license__ = 'GPL v3'

import html
import platform
import posixpath
import re
import subprocess
import tempfile
from html.parser import HTMLParser

from calibre_plugins.chinese_text_conversion.i18n import _


MIN_VISION_OCR_MACOS_MAJOR = 12
_SUPPORTED_LANGUAGES_CACHE = None

OCR_LANGUAGE_PROFILES = {
    0: (_('Simplified Chinese'), ['zh-Hans', 'zh-Hant', 'en-US']),
    1: (_('Traditional Chinese (Hong Kong)'), ['zh-Hant', 'zh-Hans', 'en-US']),
    2: (_('Traditional Chinese (Taiwan)'), ['zh-Hant', 'zh-Hans', 'en-US']),
    3: (_('Japan'), ['ja-JP', 'zh-Hans', 'zh-Hant', 'en-US']),
}


def is_vision_ocr_supported():
    if platform.system().lower() != 'darwin':
        return False
    ver = (platform.mac_ver()[0] or '').split('.')
    if not ver or not ver[0].isdigit():
        return False
    return int(ver[0]) >= MIN_VISION_OCR_MACOS_MAJOR


def get_preferred_ocr_languages(input_locale):
    _, preferred = OCR_LANGUAGE_PROFILES.get(input_locale, OCR_LANGUAGE_PROFILES[0])
    return list(preferred)


def get_ocr_language_display_name(input_locale):
    display, _preferred = OCR_LANGUAGE_PROFILES.get(input_locale, OCR_LANGUAGE_PROFILES[0])
    return display


def get_supported_vision_languages():
    global _SUPPORTED_LANGUAGES_CACHE
    if _SUPPORTED_LANGUAGES_CACHE is not None:
        return _SUPPORTED_LANGUAGES_CACHE
    if not is_vision_ocr_supported():
        _SUPPORTED_LANGUAGES_CACHE = []
        return _SUPPORTED_LANGUAGES_CACHE

    swift_code = r'''
import Vision

let request = VNRecognizeTextRequest()
do {
    let languages = try request.supportedRecognitionLanguages()
    print(languages.joined(separator: "\n"))
} catch {
    exit(2)
}
'''
    cmd = ['/usr/bin/xcrun', 'swift', '-e', swift_code]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20, check=False)
    except Exception:
        _SUPPORTED_LANGUAGES_CACHE = []
        return _SUPPORTED_LANGUAGES_CACHE
    if result.returncode != 0:
        _SUPPORTED_LANGUAGES_CACHE = []
        return _SUPPORTED_LANGUAGES_CACHE
    _SUPPORTED_LANGUAGES_CACHE = [line.strip() for line in (result.stdout or '').splitlines() if line.strip()]
    return _SUPPORTED_LANGUAGES_CACHE


def get_missing_ocr_language_notice(input_locale):
    preferred = get_preferred_ocr_languages(input_locale)
    supported_list = get_supported_vision_languages()
    if not supported_list:
        return None
    supported = set(supported_list)
    if not preferred:
        return None
    primary = preferred[0]
    if primary in supported:
        return None

    display = get_ocr_language_display_name(input_locale)
    problem = _('OCR language missing problem').format(display)
    suggestion = _('OCR language missing suggestion')
    action = _('OCR language missing action')
    return {'problem': problem, 'suggestion': suggestion, 'action': action}


def format_ocr_language_notice_message(notice):
    if not notice:
        return ''
    return '\n'.join([
        _('OCR notice problem line').format(notice.get('problem', '')),
        _('OCR notice suggestion line').format(notice.get('suggestion', '')),
        _('OCR notice action line').format(notice.get('action', '')),
    ])


def run_vision_ocr(image_bytes, preferred_languages=None):
    if not image_bytes or not is_vision_ocr_supported():
        return ''

    image_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix='tradsimp_ocr_', suffix='.img', delete=False) as tmp:
            tmp.write(image_bytes)
            image_path = tmp.name
        return _run_vision_ocr_from_file(image_path, preferred_languages=preferred_languages)
    except Exception:
        return ''
    finally:
        if image_path:
            try:
                import os
                os.remove(image_path)
            except Exception:
                pass


def enrich_images_with_ocr(container, html_name, html_data, converter, ocr_cache=None, preferred_languages=None):
    if not html_data or not is_vision_ocr_supported():
        return html_data, False, []

    cache = ocr_cache if ocr_cache is not None else {}
    parser = _ImageAltEnricher(
        container,
        html_name,
        converter,
        cache,
        preferred_languages=preferred_languages,
    )
    parser.feed(html_data)
    parser.close()
    output = parser.render()
    return output, parser.changed, parser.preview_samples


def _run_vision_ocr_from_file(image_path, preferred_languages=None):
    preferred_arg = ','.join(preferred_languages or [])
    swift_code = r'''
import Foundation
import Vision

let args = CommandLine.arguments
guard args.count >= 2 else {
    exit(1)
}

let imageURL = URL(fileURLWithPath: args[1])
let preferredLanguages = args.count >= 3
    ? args[2].split(separator: ",").map { String($0) }.filter { !$0.isEmpty }
    : []
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
let supported = (try? request.supportedRecognitionLanguages()) ?? []
let preferredAvailable = preferredLanguages.filter { supported.contains($0) }
if !preferredAvailable.isEmpty {
    request.recognitionLanguages = preferredAvailable
}
if #available(macOS 13.0, *) {
    request.automaticallyDetectsLanguage = preferredAvailable.isEmpty
}

do {
    let handler = try VNImageRequestHandler(url: imageURL, options: [:])
    try handler.perform([request])
    let observations = request.results ?? []
    let lines = observations.compactMap { obs -> String? in
        return obs.topCandidates(1).first?.string
    }.filter { !$0.isEmpty }
    print(lines.joined(separator: "\n"))
} catch {
    exit(2)
}
'''
    cmd = ['/usr/bin/xcrun', 'swift', '-e', swift_code, image_path, preferred_arg]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25, check=False)
    except Exception:
        return ''
    if result.returncode != 0:
        return ''
    return (result.stdout or '').strip()


class _FigureFrame:
    def __init__(self):
        self.has_figcaption = False
        self.parts = []


class _ImageAltEnricher(HTMLParser):
    def __init__(self, container, html_name, converter, ocr_cache, preferred_languages=None):
        super().__init__(convert_charrefs=False)
        self.container = container
        self.html_name = html_name
        self.converter = converter
        self.ocr_cache = ocr_cache
        self.preferred_languages = preferred_languages or []
        self.result = []
        self.figure_stack = []
        self.changed = False
        self.preview_samples = []

    def render(self):
        return ''.join(self.result)

    def handle_starttag(self, tag, attrs):
        tag_text = self.get_starttag_text()
        lower_tag = tag.lower()
        if lower_tag == 'figure':
            frame = _FigureFrame()
            frame.parts.append(tag_text)
            self.figure_stack.append(frame)
            return
        if lower_tag == 'figcaption' and self.figure_stack:
            self.figure_stack[-1].has_figcaption = True
        if lower_tag == 'img':
            self._append_img_part(tag_text, attrs, self._inside_captionless_figure())
            return
        self._append_text(tag_text)

    def handle_startendtag(self, tag, attrs):
        tag_text = self.get_starttag_text()
        lower_tag = tag.lower()
        if lower_tag == 'img':
            self._append_img_part(tag_text, attrs, self._inside_captionless_figure())
            return
        self._append_text(tag_text)

    def handle_endtag(self, tag):
        lower_tag = tag.lower()
        end_tag = '</' + tag + '>'
        if lower_tag == 'figure' and self.figure_stack:
            frame = self.figure_stack.pop()
            frame.parts.append(end_tag)
            rendered = self._render_frame(frame)
            self._append_text(rendered)
            return
        self._append_text(end_tag)

    def handle_data(self, data):
        self._append_text(data)

    def handle_comment(self, data):
        self._append_text('<!--' + data + '-->')

    def handle_entityref(self, name):
        self._append_text('&' + name + ';')

    def handle_charref(self, name):
        self._append_text('&#' + name + ';')

    def handle_pi(self, data):
        self._append_text('<?' + data + '>')

    def handle_decl(self, decl):
        self._append_text('<!' + decl + '>')

    def unknown_decl(self, data):
        self._append_text('<!' + data + '>')

    def _append_text(self, text):
        if self.figure_stack:
            self.figure_stack[-1].parts.append(text)
        else:
            self.result.append(text)

    def _append_img_part(self, tag_text, attrs, inside_captionless_figure):
        part = ('img', tag_text, attrs, inside_captionless_figure)
        if self.figure_stack:
            self.figure_stack[-1].parts.append(part)
        else:
            self.result.append(self._render_img(part, has_figcaption=False))

    def _inside_captionless_figure(self):
        return bool(self.figure_stack)

    def _render_frame(self, frame):
        out = []
        for part in frame.parts:
            if isinstance(part, tuple) and part and part[0] == 'img':
                out.append(self._render_img(part, has_figcaption=frame.has_figcaption))
            else:
                out.append(part)
        return ''.join(out)

    def _render_img(self, part, has_figcaption):
        _, tag_text, attrs, _inside_captionless_figure = part
        if has_figcaption:
            return tag_text
        alt_found = False
        alt_value = ''
        src_value = None
        for name, value in attrs:
            n = (name or '').lower()
            if n == 'alt':
                alt_found = True
                alt_value = value or ''
            elif n == 'src':
                src_value = value or ''
        if alt_found and alt_value.strip():
            return tag_text
        if not src_value:
            return tag_text

        image_name = _resolve_image_name(self.container, self.html_name, src_value)
        if not image_name:
            return tag_text

        recognized = self.ocr_cache.get(image_name)
        if recognized is None:
            recognized = _ocr_from_container(
                self.container, image_name, preferred_languages=self.preferred_languages)
            self.ocr_cache[image_name] = recognized
        if not recognized:
            return tag_text

        recognized = _clean_ocr_text(recognized)
        converted = self.converter.convert(recognized) if self.converter else recognized
        converted = _clean_ocr_text(converted)
        if not converted:
            return tag_text
        if len(self.preview_samples) < 3:
            self.preview_samples.append({
                'image': image_name,
                'recognized': recognized,
                'converted': converted,
            })

        updated_tag = _inject_alt(tag_text, converted)
        if updated_tag != tag_text:
            self.changed = True
        return updated_tag


def _clean_ocr_text(text):
    text = (text or '').strip()
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text)


def _ocr_from_container(container, image_name, preferred_languages=None):
    mime = container.mime_map.get(image_name, '')
    if not mime.startswith('image/'):
        return ''
    try:
        image_bytes = container.raw_data(image_name, decode=False)
    except TypeError:
        image_bytes = container.raw_data(image_name)
    except Exception:
        return ''
    if isinstance(image_bytes, str):
        try:
            image_bytes = image_bytes.encode('utf-8')
        except Exception:
            return ''
    return run_vision_ocr(image_bytes, preferred_languages=preferred_languages)


def _resolve_image_name(container, html_name, src):
    src = (src or '').strip()
    if not src or src.startswith('data:'):
        return None
    src = src.split('#', 1)[0].split('?', 1)[0]
    if not src:
        return None

    resolver = getattr(container, 'href_to_name', None)
    if callable(resolver):
        try:
            resolved = resolver(src, html_name)
            if resolved in container.mime_map:
                return resolved
        except Exception:
            pass

    src_norm = posixpath.normpath(posixpath.join(posixpath.dirname(html_name), src))
    if src_norm in container.mime_map:
        return src_norm

    return src if src in container.mime_map else None


def _inject_alt(tag_text, alt_text):
    escaped = html.escape(alt_text, quote=True)
    if re.search(r'\balt\s*=', tag_text, flags=re.IGNORECASE):
        return re.sub(
            r'(\balt\s*=\s*)(["\']).*?\2',
            r'\1"' + escaped + '"',
            tag_text,
            count=1,
            flags=re.IGNORECASE | re.DOTALL,
        )
    if tag_text.endswith('/>'):
        return tag_text[:-2] + ' alt="' + escaped + '"/>'
    if tag_text.endswith('>'):
        return tag_text[:-1] + ' alt="' + escaped + '">'
    return tag_text
