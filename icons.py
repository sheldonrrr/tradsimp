# -*- coding: utf-8 -*-

__license__ = 'GPL 3'

ICON_PATH = 'images/TradSimpIcon.png'


def load_plugin_icon(plugin_name):
    '''Load toolbar icon from the plugin zip (get_icons injected by Calibre).'''
    icon = get_icons(ICON_PATH, plugin_name)  # noqa: F821
    if icon is not None and not icon.isNull():
        return icon
    return None


def apply_action_icon(action, plugin_name):
    icon = load_plugin_icon(plugin_name)
    if icon is not None:
        action.setIcon(icon)
