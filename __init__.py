
__license__ = 'GPL 3'
__docformat__ = 'restructuredtext en'

from calibre.customize import InterfaceActionBase

PLUGIN_NAME = 'Chinese Conversion · 简繁转换'
PLUGIN_NAME_EN = 'Chinese Conversion'
PLUGIN_SAFE_NAME = 'chinese_text_conversion'
# Calibre catalog static parser: must be a plain string literal, not join()/computed.
PLUGIN_DESCRIPTION = 'Fully offline conversion between Simplified and Traditional Chinese. Community-maintained version powered by OpenCC.'
PLUGIN_VERSION_TUPLE = (3, 5, 3)
PLUGIN_VERSION = '3.5.3'
PLUGIN_MINIMUM_CALIBRE_VERSION = (6, 0, 0)
PLUGIN_RELEASED = '22 Jul, 2026'
PLUGIN_ABOUT_LAST_UPDATED = '2026-07-22'
PLUGIN_RELEASE_THREAD_URL = (
    'https://www.mobileread.com/forums/showthread.php?t=373788')
PLUGIN_AUTHOR = 'Sheldon (community fork of Hopkins1)'
PLUGIN_ACTUAL_PLUGIN = (
    'calibre_plugins.chinese_text_conversion.ui:ChineseTextAction')


class ChineseTextPlugin(InterfaceActionBase):

    name = PLUGIN_NAME
    description = PLUGIN_DESCRIPTION
    supported_platforms = ['windows', 'osx', 'linux']
    author = PLUGIN_AUTHOR
    version = PLUGIN_VERSION_TUPLE
    minimum_calibre_version = PLUGIN_MINIMUM_CALIBRE_VERSION

    #: Shown in Preferences → Plugins; also used for toolbar icon lookup
    icon = 'images/TradSimpIcon.png'

    actual_plugin = PLUGIN_ACTUAL_PLUGIN

    def is_customizable(self):
        return False

    def load_actual_plugin(self, gui):
        ac = getattr(self, 'actual_plugin_object', None)
        if ac is None:
            mod, cls = self.actual_plugin.split(':')
            from importlib import import_module
            ac = getattr(import_module(mod), cls)(gui, self.site_customization)
            self.actual_plugin_object = ac
        return ac

    def cli_main(self, argv):
        # calibre-debug --run-plugin "Chinese Conversion · 简繁转换" -- -h
        from calibre_plugins.chinese_text_conversion.main import main as plugin_main
        plugin_main(argv[1:], self.version, usage='%prog --run-plugin '+'\"'+self.name+'\"'+' --')
