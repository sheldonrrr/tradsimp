# -*- coding: utf-8 -*-

"""Compatibility layer for optional Vision OCR module.

This keeps plugin startup resilient when `vision_ocr.py` is not shipped in a
debug/test package yet. All fallback implementations are safe no-ops.
"""

try:
    from calibre_plugins.chinese_text_conversion.vision_ocr import (
        is_vision_ocr_supported,
        get_preferred_ocr_languages,
        get_missing_ocr_language_notice,
        format_ocr_language_notice_message,
        enrich_images_with_ocr,
    )
except ModuleNotFoundError:
    def is_vision_ocr_supported():
        return False

    def get_preferred_ocr_languages(input_locale):
        return []

    def get_missing_ocr_language_notice(input_locale):
        return []

    def format_ocr_language_notice_message(notice):
        return ''

    def enrich_images_with_ocr(
        container, html_name, html_data, converter,
        ocr_cache=None, preferred_languages=None, progress_callback=None,
    ):
        return html_data, False, [], {
            'images_recognized': 0,
            'recognized_images': [],
            'text_results': 0,
            'sample_results': [],
        }
