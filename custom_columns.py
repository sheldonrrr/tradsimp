# -*- coding: utf-8 -*-

"""Create and write the Script / 书写系统 custom column."""

__license__ = 'GPL 3'

from calibre_plugins.chinese_text_conversion.i18n import (
    detect_calibre_ui_language, translate)

ZH_SCRIPT_LABEL = 'zh_script'
ZH_SCRIPT_LOOKUP = '#' + ZH_SCRIPT_LABEL


def script_column_heading():
    """Heading follows Calibre GUI language: Script / 书写系统 / 書寫系統."""
    return translate(
        'Chinese script column name', detect_calibre_ui_language())


def _field_metadata(db):
    fm = getattr(db, 'field_metadata', None)
    if fm is not None:
        return fm
    api = getattr(db, 'new_api', None)
    return getattr(api, 'field_metadata', None) if api is not None else None


def zh_script_column_exists(db):
    """True if this library already has #zh_script."""
    if db is None:
        return False
    fm = _field_metadata(db)
    if fm is None:
        return False
    if ZH_SCRIPT_LOOKUP in fm:
        return True
    try:
        custom = fm.custom_field_metadata()
    except Exception:
        return False
    return ZH_SCRIPT_LOOKUP in custom


def _column_record(db):
    fm = _field_metadata(db)
    if fm is None:
        return None
    if ZH_SCRIPT_LOOKUP in fm:
        return fm[ZH_SCRIPT_LOOKUP]
    try:
        return fm.custom_field_metadata().get(ZH_SCRIPT_LOOKUP)
    except Exception:
        return None


def _apply_heading_in_memory(db, name):
    record = _column_record(db)
    if record is not None:
        record['name'] = name
    fm = _field_metadata(db)
    if fm is not None and ZH_SCRIPT_LOOKUP in fm:
        try:
            fm[ZH_SCRIPT_LOOKUP]['name'] = name
        except Exception:
            pass
    api = getattr(db, 'new_api', None)
    api_fm = getattr(api, 'field_metadata', None) if api is not None else None
    if api_fm is not None and ZH_SCRIPT_LOOKUP in api_fm:
        try:
            api_fm[ZH_SCRIPT_LOOKUP]['name'] = name
        except Exception:
            pass


def _rename_column(db, name, display):
    record = _column_record(db)
    if not record:
        return False
    current = (record.get('name') or '').strip()
    num = record.get('colnum')
    if current == name or num is None:
        return False
    try:
        api = getattr(db, 'new_api', None)
        if api is not None and hasattr(api, 'set_custom_column_metadata'):
            api.set_custom_column_metadata(num, name=name)
            setup = getattr(api, 'setup_fields', None)
            if callable(setup):
                setup()
        elif hasattr(db, 'set_custom_column_metadata'):
            try:
                db.set_custom_column_metadata(num, name=name, notify=True)
            except TypeError:
                db.set_custom_column_metadata(num, name=name)
        else:
            return False
    except Exception:
        return False
    _apply_heading_in_memory(db, name)
    after = _column_record(db)
    after_name = (after.get('name') if after else None)
    return after_name == name


def sync_script_column_heading(db):
    """Rename #zh_script to match the current Calibre interface language."""
    if db is None or not zh_script_column_exists(db):
        return False
    display = {
        'is_names': False,
        'description': translate(
            'Chinese script column description', detect_calibre_ui_language()),
    }
    return _rename_column(db, script_column_heading(), display)


def create_zh_script_column(db):
    """Create or refresh the tags-style #zh_script column. Do not create silently."""
    if db is None:
        raise RuntimeError('no library')
    display = {
        'is_names': False,
        'description': translate(
            'Chinese script column description', detect_calibre_ui_language()),
    }
    name = script_column_heading()
    if zh_script_column_exists(db):
        if _rename_column(db, name, display):
            return 'renamed'
        return 'exists'
    if hasattr(db, 'create_custom_column'):
        db.create_custom_column(
            ZH_SCRIPT_LABEL, name, 'text', True, display=display)
        return 'created'
    api = getattr(db, 'new_api', None)
    if api is not None and hasattr(api, 'create_custom_column'):
        api.create_custom_column(
            ZH_SCRIPT_LABEL, name, 'text', True, display=display)
        return 'created'
    raise RuntimeError('create_custom_column is not available')


def write_zh_script_tokens(db, book_id, tokens):
    """Write filter tokens onto the new book. False if the column is missing."""
    cleaned = [str(token).strip() for token in (tokens or []) if str(token).strip()]
    if db is None or not zh_script_column_exists(db):
        return not cleaned
    try:
        sync_script_column_heading(db)
    except Exception:
        pass
    api = getattr(db, 'new_api', None)
    if api is not None and hasattr(api, 'set_field'):
        try:
            api.set_field(ZH_SCRIPT_LOOKUP, {int(book_id): cleaned})
            return True
        except Exception:
            api.set_field(ZH_SCRIPT_LOOKUP, {int(book_id): ','.join(cleaned)})
            return True
    setter = getattr(db, 'set_custom', None)
    if setter is None:
        return False
    try:
        setter(int(book_id), ZH_SCRIPT_LABEL, cleaned, commit=True, notify=False)
    except TypeError:
        setter(int(book_id), ZH_SCRIPT_LABEL, cleaned)
    return True
