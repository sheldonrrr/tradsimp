
__license__ = 'GPL 3'
__docformat__ = 'restructuredtext en'

from calibre.customize import InterfaceActionBase

PLUGIN_NAME = "Chinese Text Conversion"
PLUGIN_SAFE_NAME = PLUGIN_NAME.strip().lower().replace(' ', '_')
PLUGIN_DESCRIPTION_EN = (
    'Convert traditional and simplified Chinese in your ebooks (offline OpenCC)')
PLUGIN_DESCRIPTION_ZH_CN = (
    '简繁中文转换：在电子书中转换简体与繁体中文（离线 OpenCC）')
PLUGIN_DESCRIPTION_ZH_TW = (
    '繁簡中文轉換：在電子書中轉換簡體與繁體中文（離線 OpenCC）')
# Calibre exposes a single description string for plugin list search/display.
PLUGIN_DESCRIPTION = ' — '.join((
    PLUGIN_DESCRIPTION_EN,
    PLUGIN_DESCRIPTION_ZH_CN,
    PLUGIN_DESCRIPTION_ZH_TW,
))
PLUGIN_VERSION_TUPLE = (3, 3, 0)
PLUGIN_VERSION = '.'.join([str(x) for x in PLUGIN_VERSION_TUPLE])
PLUGIN_ABOUT_LAST_UPDATED = '2026-06-04'
PLUGIN_RELEASE_THREAD_URL = (
    'https://www.mobileread.com/forums/showthread.php?t=373788')
PLUGIN_AUTHORS = 'Sheldon'


class ChineseTextPlugin(InterfaceActionBase):

    name = PLUGIN_NAME
    description = PLUGIN_DESCRIPTION
    supported_platforms = ['windows', 'osx', 'linux']
    author = PLUGIN_AUTHORS
    version = PLUGIN_VERSION_TUPLE
    minimum_calibre_version = (6, 0, 0)

    #: Shown in Preferences → Plugins; also used for toolbar icon lookup
    icon = 'images/TradSimpIcon.png'

    actual_plugin = 'calibre_plugins.chinese_text_conversion.ui:ChineseTextAction'

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
        # calibre-debug --run-plugin "Chinese Text Conversion" -- -h
        from calibre_plugins.chinese_text_conversion.main import main as plugin_main
        plugin_main(argv[1:], self.version, usage='%prog --run-plugin '+'\"'+self.name+'\"'+' --')
