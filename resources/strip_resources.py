# -*- coding: utf-8 -*-
"""Strip embedded fonts / images from a polish Container for lighter books."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os

from calibre.ebooks.oeb.polish.container import OEB_DOCS, OEB_STYLES

# Keep in sync with main.py criteria indices (avoid importing main here).
_INPUT_SOURCE = 0
_REMOVE_EMBEDDED_FONTS = 19
_REMOVE_IMAGE_FILES = 20

_FONT_EXTENSIONS = frozenset({
    '.ttf', '.otf', '.woff', '.woff2', '.ttc', '.eot',
})


def _flag(criteria, index):
    return bool(criteria is not None and len(criteria) > index and criteria[index])


def _mark_changed(changed_files, name):
    if name and name not in changed_files:
        changed_files.append(name)


def _font_mimes():
    try:
        from calibre.ebooks.oeb.polish.utils import OEB_FONTS
        return OEB_FONTS
    except Exception:
        return frozenset({
            'font/otf', 'font/woff', 'font/woff2', 'font/ttf',
            'application/x-font-ttf', 'application/x-font-otf',
            'application/font-sfnt', 'application/vnd.ms-opentype',
            'application/x-font-truetype',
        })


def _is_font_item(name, mime_type):
    mt = (mime_type or '').lower()
    if mt in _font_mimes():
        return True
    if mt.startswith('font/') or 'opentype' in mt or 'truetype' in mt:
        return True
    ext = os.path.splitext(name or '')[1].lower()
    return ext in _FONT_EXTENSIONS


def _is_image_item(_name, mime_type):
    return (mime_type or '').startswith('image/')


def _collect_names(container, predicate):
    return [
        name for name, mt in list(container.mime_map.items())
        if predicate(name, mt)
    ]


def _strip_font_face_from_sheet(sheet):
    removals = []
    for rule in sheet:
        rule_type = getattr(rule, 'type', None)
        font_face_type = getattr(rule, 'FONT_FACE_RULE', None)
        if font_face_type is not None and rule_type == font_face_type:
            removals.append(rule)
    if not removals:
        return False
    for rule in reversed(removals):
        try:
            sheet.cssRules.remove(rule)
        except Exception:
            try:
                sheet.remove(rule)
            except Exception:
                pass
    return True


def _strip_font_face_rules(container, changed_files):
    changed = False
    for name, mt in list(container.mime_map.items()):
        if mt not in OEB_STYLES:
            continue
        try:
            sheet = container.parsed(name)
        except Exception:
            continue
        if not _strip_font_face_from_sheet(sheet):
            continue
        container.dirty(name)
        _mark_changed(changed_files, name)
        changed = True

    # Inline <style> blocks in HTML may also declare @font-face.
    for name, mt in list(container.mime_map.items()):
        if mt not in OEB_DOCS:
            continue
        try:
            root = container.parsed(name)
        except Exception:
            continue
        doc_changed = False
        for style_tag in root.xpath('//*[local-name()="style"]'):
            text = style_tag.text or ''
            if '@font-face' not in text.lower():
                continue
            try:
                sheet = container.parse_css(text)
            except Exception:
                continue
            if not _strip_font_face_from_sheet(sheet):
                continue
            try:
                from calibre.ebooks.oeb.base import css_text as _css_text
            except Exception:
                _css_text = str
            style_tag.text = _css_text(sheet)
            doc_changed = True
        if doc_changed:
            container.dirty(name)
            _mark_changed(changed_files, name)
            changed = True
    return changed


def _remove_package_items(container, names, changed_files):
    removed_any = False
    for name in list(names):
        if not container.has_name(name):
            continue
        try:
            container.remove_item(name)
        except Exception:
            continue
        _mark_changed(changed_files, name)
        removed_any = True
    return removed_any


def _scrub_links_to_names(container, target_names, changed_files):
    if not target_names:
        return False
    targets = set(target_names)

    def predicate(hname, _href, _fragment=None):
        return hname in targets

    try:
        from calibre.ebooks.oeb.polish.replace import remove_links_to
    except Exception:
        return False

    changed_names = remove_links_to(container, predicate) or set()
    for name in changed_names:
        try:
            container.dirty(name)
        except Exception:
            pass
        _mark_changed(changed_files, name)
    return bool(changed_names)


def _remove_unused_images_fallback(container, changed_files):
    try:
        from calibre.ebooks.oeb.polish.images import remove_unused_images
    except Exception:
        try:
            from calibre.ebooks.oeb.polish.cover import remove_unused_images
        except Exception:
            return False
    before = set(container.mime_map.keys())
    try:
        remove_unused_images(container)
    except Exception:
        return False
    after = set(container.mime_map.keys())
    removed = before - after
    for name in removed:
        _mark_changed(changed_files, name)
    return bool(removed)


def apply_resource_stripping(container, criteria, changed_files):
    """
    Remove embedded fonts and/or images from an entire-book container.
    Returns True if the package changed.
    """
    if criteria is None or len(criteria) <= _INPUT_SOURCE:
        return False
    if criteria[_INPUT_SOURCE] != 0:
        return False

    remove_fonts = _flag(criteria, _REMOVE_EMBEDDED_FONTS)
    remove_images = _flag(criteria, _REMOVE_IMAGE_FILES)
    if not remove_fonts and not remove_images:
        return False

    changed = False

    if remove_fonts:
        font_names = _collect_names(container, _is_font_item)
        if _strip_font_face_rules(container, changed_files):
            changed = True
        if font_names and _scrub_links_to_names(container, font_names, changed_files):
            changed = True
        if font_names and _remove_package_items(container, font_names, changed_files):
            changed = True

    if remove_images:
        image_names = _collect_names(container, _is_image_item)
        if image_names and _scrub_links_to_names(container, image_names, changed_files):
            changed = True
        if image_names and _remove_package_items(container, image_names, changed_files):
            changed = True
        if _remove_unused_images_fallback(container, changed_files):
            changed = True

    return changed
