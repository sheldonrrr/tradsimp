# -*- coding: utf-8 -*-

__license__   = 'GPL v3'

import os, re

try:
    from qt.core import (Qt, QUrl, QVBoxLayout, QLabel, QComboBox, QApplication, QSizePolicy,
                  QGroupBox, QButtonGroup, QRadioButton, QDialogButtonBox, QHBoxLayout,
                  QProgressDialog, QSize, QDialog, QCheckBox, QSpinBox, QScrollArea, QWidget,
                  QPushButton, QPlainTextEdit)
except ImportError:
    from PyQt5.Qt import (Qt, QVBoxLayout, QLabel, QComboBox, QApplication, QSizePolicy,
                          QGroupBox, QButtonGroup, QRadioButton, QDialogButtonBox, QHBoxLayout,
                          QProgressDialog, QSize, QDialog, QCheckBox, QSpinBox, QScrollArea, QWidget,
                          QPushButton, QPlainTextEdit)
    from PyQt5.QtCore import QUrl

from calibre.utils.config import config_dir

from calibre.gui2 import open_url
from calibre.gui2.tweak_book.widgets import Dialog

from calibre_plugins.chinese_text_conversion import (
    PLUGIN_VERSION, PLUGIN_ABOUT_LAST_UPDATED, PLUGIN_RELEASE_THREAD_URL)
from calibre_plugins.chinese_text_conversion.i18n import (
    _, apply_ui_language_from_prefs, detect_calibre_ui_language,
    normalize_ui_language, ui_language_combo_items,
    UI_LANG_EN, UI_LANG_ZH_CN, UI_LANG_ZH_TW, UI_LANG_ZH_HK, TRADITIONAL_UI_LANGS,
)
from calibre_plugins.chinese_text_conversion.ui_style import (
    apply_dialog_stylesheet, configure_form_label, configure_layout,
    build_radio_group, build_section_group,
    help_text_row, make_section_divider, polish_scroll_area, style_help_label,
    style_subheading_label,
)

'''
ConversionDialog
The conversion dialog asks/displays the following:
    -Which direction of conversion is desired (i.e. Traditional->Simplified, Simplified->Traditional, or Traditional->Traditional)
    -If converting from Traditional, what country style is the source of the text (Hong Kong, Mainland, or Taiwan)
    -If converting to Traditional, what country style is desired (Hong Kong, Mainland, or Taiwan)
    -What text should be converted (the currently entire book, current file or selected text)

The chosen settings are saved between program starts.

Note: This code is based on the Calibre plugin Diap's Editing Toolbag
'''


# Default size when no saved geometry (library conversion wizard)
LIBRARY_CONVERSION_DIALOG_SIZE = QSize(760, 760)
LIBRARY_STATUS_DIALOG_SIZE = QSize(720, 560)
ABOUT_DIALOG_SIZE = QSize(560, 520)


class PluginAboutDialog(QDialog):
    '''User-facing introduction: features, offline conversion, quick start.'''

    def __init__(self, parent, prefs, first_run=False):
        super().__init__(parent)
        self.prefs = prefs
        self.first_run = first_run
        self._build_ui()
        apply_ui_language_from_prefs(self.prefs)
        self.apply_translations()

    def _build_ui(self):
        self.setMinimumSize(ABOUT_DIALOG_SIZE)
        layout = QVBoxLayout(self)
        configure_layout(layout, 'dialog')

        scroll = QScrollArea(self)
        polish_scroll_area(scroll)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        configure_layout(content_layout, 'sections')

        self.title_label = QLabel()
        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(title_font.pointSize() + 2)
        self.title_label.setFont(title_font)
        content_layout.addWidget(self.title_label)

        self.version_label = QLabel()
        content_layout.addWidget(self.version_label)

        self.last_updated_label = QLabel()
        content_layout.addWidget(self.last_updated_label)

        self.welcome_label = QLabel()
        self.welcome_label.setWordWrap(True)
        content_layout.addWidget(self.welcome_label)

        self.offline_label = QLabel()
        self.offline_label.setWordWrap(True)
        offline_font = self.offline_label.font()
        offline_font.setBold(True)
        self.offline_label.setFont(offline_font)
        content_layout.addWidget(self.offline_label)

        self.features_heading = QLabel()
        feat_font = self.features_heading.font()
        feat_font.setBold(True)
        self.features_heading.setFont(feat_font)
        self.features_heading.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.features_heading)

        self.features_label = QLabel()
        self.features_label.setWordWrap(True)
        content_layout.addWidget(self.features_label)

        self.usage_heading = QLabel()
        self.usage_heading.setFont(feat_font)
        content_layout.addWidget(self.usage_heading)

        self.usage_label = QLabel()
        self.usage_label.setWordWrap(True)
        content_layout.addWidget(self.usage_label)

        self.lineage_label = QLabel()
        self.lineage_label.setWordWrap(True)
        content_layout.addWidget(self.lineage_label)

        self.release_heading = QLabel()
        self.release_heading.setFont(feat_font)
        content_layout.addWidget(self.release_heading)

        self.release_label = QLabel()
        self.release_label.setWordWrap(True)
        content_layout.addWidget(self.release_label)

        self.maintainer_heading = QLabel()
        self.maintainer_heading.setFont(feat_font)
        content_layout.addWidget(self.maintainer_heading)

        self.maintainer_label = QLabel()
        self.maintainer_label.setWordWrap(True)
        content_layout.addWidget(self.maintainer_label)

        self.goals_heading = QLabel()
        self.goals_heading.setFont(feat_font)
        content_layout.addWidget(self.goals_heading)

        self.goals_label = QLabel()
        self.goals_label.setWordWrap(True)
        content_layout.addWidget(self.goals_label)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        layout.addWidget(make_section_divider(self))
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        layout.addWidget(self.button_box)
        apply_dialog_stylesheet(self)

    def apply_translations(self):
        self.setWindowTitle(_('About Chinese Conversion · 简繁转换'))
        self.title_label.setText(_('About Chinese Conversion · 简繁转换'))
        self.version_label.setText(_('Version {}').format(PLUGIN_VERSION))
        self.last_updated_label.setText(
            _('About last updated').format(PLUGIN_ABOUT_LAST_UPDATED))
        if self.first_run:
            self.welcome_label.setText(_('About welcome first run'))
            self.welcome_label.show()
        else:
            self.welcome_label.hide()
        self.offline_label.setText(_('About offline highlight'))
        self.features_heading.setText(_('About features'))
        self.features_label.setText(_('About features list'))
        self.usage_heading.setText(_('About quick start'))
        self.usage_label.setText(_('About quick start steps'))
        self.lineage_label.setText(_('About lineage'))
        self.release_heading.setText(_('About release'))
        self.release_label.setText(_('About release body'))
        self.maintainer_heading.setText(_('About maintainer'))
        self.maintainer_label.setText(_('About maintainer body'))
        self.goals_heading.setText(_('About maintenance goals'))
        self.goals_label.setText(_('About maintenance goals list'))
        ok_btn = self.button_box.button(QDialogButtonBox.Ok)
        if ok_btn is not None:
            ok_btn.setText(_('Got it'))

    def mark_first_run_complete(self):
        if self.first_run:
            self.prefs['about_shown'] = True
            self.prefs.commit()


class ConversionDialog(Dialog):
    # Preference behavior contract:
    # 1) Before any successful run is saved (has_user_preferences=False),
    #    UI language changes apply localized recommended defaults.
    # 2) After at least one successful run (has_user_preferences=True),
    #    switching to a different UI language shows that language's
    #    recommended defaults (temporary preview behavior).
    # 3) When switching back to the saved preference language
    #    (prefs['ui_language']), the full saved preference profile is restored.
    # 4) The saved preference profile is updated only when the user confirms
    #    processing (savePrefs), so casual UI language browsing does not
    #    overwrite user defaults.
    def __init__(self, parent, prefs, punc_dict, default_omitted_puncuation, force_entire_book=False):
        self.prefs = prefs
        self.parent = parent
        self.force_entire_book = force_entire_book
        Dialog.__init__(self, _('Chinese Conversion'), 'chinese_conversion_dialog', parent)
        self.punctuation_dialog = PuncuationDialog(self.parent, self.prefs, punc_dict, default_omitted_puncuation)
        if self.force_entire_book:
            self.setMinimumSize(LIBRARY_CONVERSION_DIALOG_SIZE)

    def sizeHint(self):
        if self.force_entire_book:
            return LIBRARY_CONVERSION_DIALOG_SIZE
        return QSize(640, 620)

    def _init_quote_strings(self):
        self.quote_for_trad_target = _('Update quotes: “ ”,‘ ’ -> 「 」,『 』')
        self.quote_for_simp_target = _('Update quotes: 「 」,『 』 -> “ ”,‘ ’')

    def setup_ui(self):

##        print('Dialog preferences')
##        print(self.prefs['input_source'])           # 0=whole book, 1=current file, 2=selected text
##
##        print(self.prefs['conversion_type'])        # 0=No change, 1=trad->simp, 2=simp->trad, 3=trad->trad
##        print(self.prefs['input_locale'])           # 0=Mainland, 1=Hong Kong, 2=Taiwan 3=Japan
##        print(self.prefs['output_locale'])          # 0=Mainland, 1=Hong Kong, 2=Taiwan 3=Japan
##        print(self.prefs['use_target_phrases'])     # True/False
##
##        print(self.prefs['quotation_type'])         # 0=No change, 1=Western, 2=East Asian
##
##        print(self.prefs['output_orientation'])     # 0=No change, 1=Horizontal, 2=Vertical
##
##        print(self.prefs['punc_omits'])             # Horizontal mark string in horizontal/vertical
##                                                    # dictionary pairs that is NOT to be used. No
##                                                    # space between marks in string.

        apply_ui_language_from_prefs(self.prefs)
        self._init_quote_strings()
        self.input_locale_user_set = bool(self.prefs.get('input_locale_user_set', False))
        self.output_locale_user_set = bool(self.prefs.get('output_locale_user_set', False))
        self.output_orientation_user_set = bool(self.prefs.get('output_orientation_user_set', False))
        self.symbol_profile_user_set = bool(self.prefs.get('symbol_profile_user_set', False))

        # Create layout for entire dialog
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        configure_layout(layout, 'dialog')

        lang_layout = QHBoxLayout()
        configure_layout(lang_layout, 'form')
        layout.addLayout(lang_layout)
        self.ui_lang_label = QLabel(_('Interface Language:'))
        configure_form_label(self.ui_lang_label)
        lang_layout.addWidget(self.ui_lang_label)
        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.addItems(ui_language_combo_items())
        self.ui_lang_combo.setCurrentIndex(
            normalize_ui_language(self.prefs.get(
                'ui_language', detect_calibre_ui_language())))
        self.ui_lang_combo.currentIndexChanged.connect(self.on_ui_language_changed)
        lang_layout.addWidget(self.ui_lang_combo, 1)

        self.scrollArea = QScrollArea(self)
        polish_scroll_area(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)

        self.scrollContentWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollContentWidget)
        widgetLayout = QVBoxLayout(self.scrollContentWidget)
        configure_layout(widgetLayout, 'sections')
        widgetLayout.setAlignment(
            Qt.AlignmentFlag.AlignTop if hasattr(Qt, 'AlignmentFlag') else Qt.AlignTop)

        layout.addWidget(self.scrollArea, stretch=1)

        # Section order: primary (direction + characters) → secondary (scope) → advanced (quotes/punctuation)
        self.text_direction_group_box, text_direction_group_box_layout = build_section_group(
            self, _('Text Direction:'))
        text_direction_policy = self.text_direction_group_box.sizePolicy()
        text_direction_policy.setVerticalPolicy(QSizePolicy.Maximum)
        self.text_direction_group_box.setSizePolicy(text_direction_policy)
        widgetLayout.addWidget(self.text_direction_group_box)
        self.text_direction_group, text_direction_radio_layout, text_direction_buttons = (
            build_radio_group(
                self,
                [_('No Change'), _('Horizontal'), _('Vertical')],
                ids=[0, 1, 2],
            )
        )
        text_direction_group_box_layout.addLayout(text_direction_radio_layout)
        (self.text_dir_no_change_button,
         self.text_dir_horizontal_button,
         self.text_dir_vertical_button) = text_direction_buttons
        tip = _('Select the desired text orientation')
        self.text_direction_group_box.setToolTip(tip)
        for btn in text_direction_buttons:
            btn.setToolTip(tip)
        self.text_direction_group.buttonClicked.connect(self._on_text_direction_clicked)

        self.operation_group_box, operation_group_box_layout = build_section_group(
            self, _('Conversion Direction'))
        operation_policy = self.operation_group_box.sizePolicy()
        operation_policy.setVerticalPolicy(QSizePolicy.Maximum)
        self.operation_group_box.setSizePolicy(operation_policy)
        widgetLayout.addWidget(self.operation_group_box)
        self.operation_group, operation_radio_layout, operation_buttons = build_radio_group(
            self,
            [
                _('No Conversion'),
                _('Traditional to Simplified'),
                _('Simplified to Traditional'),
                _('Traditional to Traditional'),
            ],
        )
        (self.no_conversion_button,
         self.trad_to_simp_button,
         self.simp_to_trad_button,
         self.trad_to_trad_button) = operation_buttons
        operation_group_box_layout.addLayout(operation_radio_layout)

        self.trad_to_trad_help = QLabel()
        self.trad_to_trad_help.setWordWrap(True)
        self.trad_to_trad_help.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        style_help_label(self.trad_to_trad_help)
        self.trad_to_trad_help.setStyleSheet(
            self.trad_to_trad_help.styleSheet() + ' padding-top: 0px; padding-bottom: 0px;')
        self.trad_to_trad_help_row = help_text_row(self, self.trad_to_trad_help)
        self.trad_to_trad_help_row.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        operation_group_box_layout.addWidget(self.trad_to_trad_help_row)
        self._update_trad_to_trad_help_text()
        self.operation_group.buttonClicked.connect(self.on_op_button_clicked)

        self.style_group_box = QGroupBox(_('Language Styles'))
        style_group_policy = self.style_group_box.sizePolicy()
        style_group_policy.setVerticalPolicy(QSizePolicy.Maximum)
        self.style_group_box.setSizePolicy(style_group_policy)
        widgetLayout.addWidget(self.style_group_box)
        style_group_box_layout = QVBoxLayout()
        configure_layout(style_group_box_layout, 'section')
        self.style_group_box.setLayout(style_group_box_layout)

        input_layout = QHBoxLayout()
        configure_layout(input_layout, 'form')
        style_group_box_layout.addLayout(input_layout)
        self.input_region_label = QLabel(_('Input:'))
        configure_form_label(self.input_region_label)
        input_layout.addWidget(self.input_region_label)
        self.input_combo = QComboBox()
        input_layout.addWidget(self.input_combo, 1)
        self.input_combo.addItems([_('Mainland'), _('Hong Kong'), _('Taiwan'), _('Japan')])
        self.input_combo.setToolTip(_('Select the origin region of the input'))
        self.input_combo.currentIndexChanged.connect(self._on_locale_changed)
        self.input_combo.activated.connect(self._mark_input_locale_user_set)

        output_layout = QHBoxLayout()
        configure_layout(output_layout, 'form')
        style_group_box_layout.addLayout(output_layout)
        self.output_region_label = QLabel(_('Output:'))
        configure_form_label(self.output_region_label)
        output_layout.addWidget(self.output_region_label)
        self.output_combo = QComboBox()
        output_layout.addWidget(self.output_combo, 1)
        self.output_combo.addItems([_('Mainland'), _('Hong Kong'), _('Taiwan'), _('Japan')])
        self.output_combo.setToolTip(_('Select the desired region of the output'))
        self.output_combo.currentIndexChanged.connect(self._on_locale_changed)
        self.output_combo.activated.connect(self._mark_output_locale_user_set)

        self.use_target_phrases = QCheckBox(_('Use output target phrases if possible'))
        style_group_box_layout.addWidget(self.use_target_phrases)
        self.use_target_phrases_help = QLabel()
        self.use_target_phrases_help.setWordWrap(True)
        self.use_target_phrases_help.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        style_help_label(self.use_target_phrases_help)
        self.use_target_phrases_help_row = help_text_row(self, self.use_target_phrases_help)
        self.use_target_phrases_help_row.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        style_group_box_layout.addWidget(self.use_target_phrases_help_row)
        self._update_target_phrases_help_text()
        self.use_target_phrases.stateChanged.connect(self._on_use_target_phrases_changed)

        source_group=QButtonGroup(self)
        self.book_source_button = QRadioButton(_('Entire eBook'))
        self.file_source_button = QRadioButton(_('Current File'))
        self.seltext_source_button = QRadioButton(_('Tagged Text in Current File'))
        self.seltext_source_button.setToolTip(_('“Tagged Text” is bracketed by <!--PI_SELTEXT_START--> and <!--PI_SELTEXT_END-->'))
        source_group.addButton(self.book_source_button)
        source_group.addButton(self.file_source_button)
        source_group.addButton(self.seltext_source_button)
        self.source_group_box = QGroupBox(_('Source'))
        if not self.force_entire_book:
            source_group_policy = self.source_group_box.sizePolicy()
            source_group_policy.setVerticalPolicy(QSizePolicy.Maximum)
            self.source_group_box.setSizePolicy(source_group_policy)
            widgetLayout.addWidget(self.source_group_box)
            source_group_box_layout = QVBoxLayout()
            configure_layout(source_group_box_layout, 'radio')
            self.source_group_box.setLayout(source_group_box_layout)
            source_group_box_layout.addWidget(self.book_source_button)
            source_group_box_layout.addWidget(self.file_source_button)
            source_group_box_layout.addWidget(self.seltext_source_button)

        self.advanced_group_box = QGroupBox(_('Advanced options'))
        advanced_group_policy = self.advanced_group_box.sizePolicy()
        advanced_group_policy.setVerticalPolicy(QSizePolicy.Maximum)
        self.advanced_group_box.setSizePolicy(advanced_group_policy)
        widgetLayout.addWidget(self.advanced_group_box)
        advanced_group_box_layout = QVBoxLayout()
        configure_layout(advanced_group_box_layout, 'section')
        self.advanced_group_box.setLayout(advanced_group_box_layout)

        self.quotation_heading = QLabel(_('Quotation Marks'))
        style_subheading_label(self.quotation_heading)
        self.quotation_heading.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        advanced_group_box_layout.addWidget(self.quotation_heading)

        quotation_group = QButtonGroup(self)
        self.quotation_no_change_button = QRadioButton(_('No Change'))
        quotation_group.addButton(self.quotation_no_change_button)
        self.quotation_trad_to_simp_button = QRadioButton(self.quote_for_simp_target)
        quotation_group.addButton(self.quotation_trad_to_simp_button)
        self.quotation_simp_to_trad_button = QRadioButton(self.quote_for_trad_target)
        quotation_group.addButton(self.quotation_simp_to_trad_button)
        advanced_group_box_layout.addWidget(self.quotation_no_change_button)
        advanced_group_box_layout.addWidget(self.quotation_simp_to_trad_button)
        advanced_group_box_layout.addWidget(self.quotation_trad_to_simp_button)
        self.quotation_no_change_button.toggled.connect(self.update_gui)
        self.quotation_trad_to_simp_button.toggled.connect(self.update_gui)
        self.quotation_simp_to_trad_button.toggled.connect(self.update_gui)
        self.quotation_no_change_button.clicked.connect(self._mark_symbol_profile_user_set)
        self.quotation_trad_to_simp_button.clicked.connect(self._mark_symbol_profile_user_set)
        self.quotation_simp_to_trad_button.clicked.connect(self._mark_symbol_profile_user_set)

        punctuation_layout = QHBoxLayout()
        configure_layout(punctuation_layout, 'form')
        advanced_group_box_layout.addLayout(punctuation_layout)
        self.update_punctuation = QCheckBox(_('Update punctuation'))
        punctuation_layout.addWidget(self.update_punctuation)
        self.update_punctuation.stateChanged.connect(self.update_gui)
        self.update_punctuation.clicked.connect(self._mark_symbol_profile_user_set)
        self.punc_settings_btn = QPushButton()
        self.punc_settings_btn.setText(_('Settings...'))
        punctuation_layout.addStretch(1)
        punctuation_layout.addWidget(self.punc_settings_btn)
        self.punc_settings_btn.clicked.connect(self.punc_settings_btn_clicked)
        self.punctuation_dialog = None

        self.book_source_button.toggled.connect(self.on_button_toggled)

        layout.addWidget(make_section_divider(self))
        footer_layout = QHBoxLayout()
        configure_layout(footer_layout, 'footer')
        self.about_btn = QPushButton()
        self.about_btn.clicked.connect(self._show_about_dialog)
        footer_layout.addWidget(self.about_btn)
        self.check_updates_btn = QPushButton()
        self.check_updates_btn.clicked.connect(self._open_release_thread)
        footer_layout.addWidget(self.check_updates_btn)
        footer_layout.addStretch(1)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._ok_clicked)
        self.button_box.rejected.connect(self._reject_clicked)
        footer_layout.addWidget(self.button_box)
        layout.addLayout(footer_layout)

        self.set_to_preferences()
        self.apply_translations()
        self.update_gui()
        ui_lang = normalize_ui_language(self.ui_lang_combo.currentIndex())
        if not self.prefs.get('has_user_preferences', False):
            self._apply_conversion_direction_for_ui_language(ui_lang)
            self._apply_locale_defaults_for_selected_direction(ui_lang)
            self._apply_output_orientation_default_for_ui_language(ui_lang, force=True)
            self._apply_symbol_profile_default(force=True)
        else:
            self._apply_symbol_profile_default()
        self.about_btn.setText(_('About'))
        self.check_updates_btn.setText(_('Check for updates'))
        if not self.prefs.get('about_shown', True):
            self._show_about_dialog(first_run=True)
        apply_dialog_stylesheet(self)

    def _show_about_dialog(self, first_run=False):
        dlg = PluginAboutDialog(self.parent, self.prefs, first_run=first_run)
        dlg.exec_()
        dlg.mark_first_run_complete()

    def _open_release_thread(self):
        open_url(QUrl(PLUGIN_RELEASE_THREAD_URL))

    def _update_target_phrases_help_text(self):
        help_text = _('Use target region phrases help')
        self.use_target_phrases_help.setText(help_text)
        self.use_target_phrases.setToolTip(help_text)

    def _update_trad_to_trad_help_text(self):
        self.trad_to_trad_help.setText(_('Traditional to Traditional help'))

    def _apply_conversion_direction_for_ui_language(self, lang_index):
        '''简体界面 → 繁体到简体；繁体界面 → 简体到繁体（与常见转换习惯一致）。'''
        if lang_index == UI_LANG_ZH_CN:
            direction_button = self.trad_to_simp_button
        elif lang_index in TRADITIONAL_UI_LANGS:
            direction_button = self.simp_to_trad_button
        else:
            return
        self.block_signals(True)
        direction_button.setChecked(True)
        self.block_signals(False)
        self.update_gui()

    def _ui_output_locale(self, lang_index):
        if lang_index == UI_LANG_ZH_CN:
            return 0  # Mainland
        if lang_index == UI_LANG_ZH_TW:
            return 2  # Taiwan
        if lang_index == UI_LANG_ZH_HK:
            return 1  # Hong Kong
        return None

    def _preferred_traditional_locale(self, lang_index):
        # Traditional UI keeps output aligned with UI locale;
        # Simplified UI defaults to Taiwan for traditional output/input.
        if lang_index == UI_LANG_ZH_HK:
            return 1
        if lang_index in TRADITIONAL_UI_LANGS:
            return 2
        return 2

    def _alternate_traditional_locale(self, locale_idx):
        # Keep traditional locale choices mutually exclusive between HK and TW.
        if locale_idx == 1:
            return 2
        if locale_idx == 2:
            return 1
        return 2

    def _apply_locale_defaults_for_selected_direction(self, lang_index):
        changed = False
        pref_trad = self._preferred_traditional_locale(lang_index)
        alt_trad = self._alternate_traditional_locale(pref_trad)
        input_idx = self.input_combo.currentIndex()
        output_idx = self.output_combo.currentIndex()

        if self.trad_to_simp_button.isChecked():
            target_input, target_output = pref_trad, 0
        elif self.simp_to_trad_button.isChecked():
            target_input, target_output = 0, pref_trad
        elif self.trad_to_trad_button.isChecked():
            # trad->trad always keeps both sides traditional and mutually exclusive.
            target_input, target_output = pref_trad, alt_trad
        else:
            target_input, target_output = -1, -1

        self.block_signals(True)
        if input_idx != target_input:
            self.input_combo.setCurrentIndex(target_input)
            changed = True
        if output_idx != target_output:
            self.output_combo.setCurrentIndex(target_output)
            changed = True
        self.block_signals(False)
        if changed:
            self.update_gui()

    def _apply_output_orientation_default_for_ui_language(self, lang_index, force=False):
        '''仅在用户未手动改动时按界面语言给出文字方向默认建议。'''
        if self.output_orientation_user_set and not force:
            return
        # Localized defaults:
        # - zh_TW: prefer vertical
        # - zh_HK: prefer horizontal
        # - zh_CN: prefer horizontal
        # - en: keep current selection (no auto switch)
        if lang_index == UI_LANG_ZH_TW:
            target_idx = 2  # Vertical
        elif lang_index == UI_LANG_ZH_HK:
            target_idx = 1  # Horizontal
        elif lang_index == UI_LANG_ZH_CN:
            target_idx = 1  # Horizontal
        else:
            return
        self.block_signals(True)
        self._set_output_orientation_index(target_idx)
        self.block_signals(False)
        self.direction_changed()
        self.update_gui()

    def _output_orientation_index(self):
        if self.text_dir_horizontal_button.isChecked():
            return 1
        if self.text_dir_vertical_button.isChecked():
            return 2
        return 0

    def _set_output_orientation_index(self, index):
        buttons = (
            self.text_dir_no_change_button,
            self.text_dir_horizontal_button,
            self.text_dir_vertical_button,
        )
        if 0 <= index < len(buttons):
            buttons[index].setChecked(True)

    def _set_text_direction_enabled(self, enabled):
        for btn in (
            self.text_dir_no_change_button,
            self.text_dir_horizontal_button,
            self.text_dir_vertical_button,
        ):
            btn.setEnabled(enabled)

    def _on_text_direction_clicked(self, _button):
        self._mark_output_orientation_user_set()
        self.direction_changed()
        self._apply_symbol_profile_default()

    def _on_locale_changed(self, _index):
        self.update_gui()
        self._apply_symbol_profile_default()

    def _selected_conversion_type(self):
        if self.trad_to_simp_button.isChecked():
            return 1
        if self.simp_to_trad_button.isChecked():
            return 2
        if self.trad_to_trad_button.isChecked():
            return 3
        return 0

    def _suggest_symbol_profile(self):
        orientation = self._output_orientation_index()
        input_locale = self.input_combo.currentIndex()
        output_locale = self.output_combo.currentIndex()
        conversion_type = self._selected_conversion_type()

        # 繁体来源 + 横排简体目标：默认采用简体横排符号体系。
        if orientation == 1 and output_locale == 0 and (conversion_type == 1 or input_locale in (1, 2)):
            return 1, True
        # 简体来源 + 竖排繁体目标：默认采用繁体竖排符号体系。
        if orientation == 2 and output_locale in (1, 2) and (conversion_type == 2 or input_locale == 0):
            return 2, True
        # 其余场景保持保守默认。
        return 0, False

    def _apply_symbol_profile_default(self, force=False):
        if self.symbol_profile_user_set and not force:
            return

        quotation_type, update_punctuation = self._suggest_symbol_profile()
        self.block_signals(True)
        if quotation_type == 1:
            self.quotation_trad_to_simp_button.setChecked(True)
        elif quotation_type == 2:
            self.quotation_simp_to_trad_button.setChecked(True)
        else:
            self.quotation_no_change_button.setChecked(True)
        self.update_punctuation.setChecked(update_punctuation)
        self.block_signals(False)
        self.update_gui()

    def _apply_quotation_for_ui_language(self, lang_index):
        '''简体界面 → 「」→“”；繁体界面 → “”→「」（常见转换习惯）。'''
        if lang_index not in (UI_LANG_ZH_CN,) and lang_index not in TRADITIONAL_UI_LANGS:
            return
        for btn in (
            self.quotation_no_change_button,
            self.quotation_trad_to_simp_button,
            self.quotation_simp_to_trad_button,
        ):
            btn.blockSignals(True)
        if lang_index == UI_LANG_ZH_CN:
            self.quotation_trad_to_simp_button.setChecked(True)
        else:
            self.quotation_simp_to_trad_button.setChecked(True)
        for btn in (
            self.quotation_no_change_button,
            self.quotation_trad_to_simp_button,
            self.quotation_simp_to_trad_button,
        ):
            btn.blockSignals(False)

    def on_ui_language_changed(self, index):
        from calibre_plugins.chinese_text_conversion.i18n import set_ui_language
        lang_index = normalize_ui_language(index)
        saved_pref_lang = normalize_ui_language(
            self.prefs.get('profile_ui_language',
                           self.prefs.get('ui_language', detect_calibre_ui_language())))
        # Persist UI language selection immediately so reopening the dialog
        # always uses the most recently chosen language.
        self.prefs['ui_language'] = lang_index
        self.prefs.commit()
        set_ui_language(lang_index)
        self.apply_translations()
        has_user_preferences = bool(self.prefs.get('has_user_preferences', False))
        if has_user_preferences and (lang_index == saved_pref_lang):
            # Restore last successful run settings when user returns to
            # the language tied to their saved preference profile.
            self.set_to_preferences()
        else:
            self._apply_conversion_direction_for_ui_language(lang_index)
            self._apply_locale_defaults_for_selected_direction(lang_index)
            self._apply_output_orientation_default_for_ui_language(lang_index, force=True)
            self._apply_symbol_profile_default(force=True)
        self._apply_symbol_profile_default()
        self.update_gui()

    def _mark_input_locale_user_set(self, *_args):
        self.input_locale_user_set = True

    def _mark_output_locale_user_set(self, *_args):
        self.output_locale_user_set = True

    def _mark_output_orientation_user_set(self, *_args):
        self.output_orientation_user_set = True

    def _mark_symbol_profile_user_set(self, *_args):
        self.symbol_profile_user_set = True

    def _on_use_target_phrases_changed(self, _state):
        # Persist immediately (same behavior as UI language):
        # dialog reopen always reflects the latest user choice.
        self.prefs['use_target_phrases'] = self.use_target_phrases.isChecked()
        self.prefs.commit()

    def apply_translations(self):
        self.setWindowTitle(_('Chinese Conversion'))
        self.ui_lang_label.setText(_('Interface Language:'))
        ui_lang_idx = self.ui_lang_combo.currentIndex()
        self.ui_lang_combo.blockSignals(True)
        self.ui_lang_combo.clear()
        self.ui_lang_combo.addItems(ui_language_combo_items())
        self.ui_lang_combo.setCurrentIndex(
            normalize_ui_language(ui_lang_idx))

        self._init_quote_strings()

        self.operation_group_box.setTitle(_('Conversion Direction'))
        self.no_conversion_button.setText(_('No Conversion'))
        self.trad_to_simp_button.setText(_('Traditional to Simplified'))
        self.simp_to_trad_button.setText(_('Simplified to Traditional'))
        self.trad_to_trad_button.setText(_('Traditional to Traditional'))
        self._update_trad_to_trad_help_text()

        self.style_group_box.setTitle(_('Language Styles'))
        self.input_region_label.setText(_('Input:'))
        self.output_region_label.setText(_('Output:'))
        for combo, regions in (
            (self.input_combo, [_('Mainland'), _('Hong Kong'), _('Taiwan'), _('Japan')]),
             (self.output_combo, [_('Mainland'), _('Hong Kong'), _('Taiwan'), _('Japan')]),
        ):
            idx = combo.currentIndex()
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(regions)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.blockSignals(False)
        self.input_combo.setToolTip(_('Select the origin region of the input'))
        self.output_combo.setToolTip(_('Select the desired region of the output'))
        self.use_target_phrases.setText(_('Use output target phrases if possible'))
        self._update_target_phrases_help_text()

        self.text_direction_group_box.setTitle(_('Text Direction:'))
        tip = _('Select the desired text orientation')
        self.text_direction_group_box.setToolTip(tip)
        self.text_dir_no_change_button.setText(_('No Change'))
        self.text_dir_horizontal_button.setText(_('Horizontal'))
        self.text_dir_vertical_button.setText(_('Vertical'))
        for btn in (self.text_dir_no_change_button, self.text_dir_horizontal_button,
                    self.text_dir_vertical_button):
            btn.setToolTip(tip)

        self.advanced_group_box.setTitle(_('Advanced options'))
        self.quotation_heading.setText(_('Quotation Marks'))
        self.quotation_no_change_button.setText(_('No Change'))
        self.quotation_trad_to_simp_button.setText(self.quote_for_simp_target)
        self.quotation_simp_to_trad_button.setText(self.quote_for_trad_target)
        self.update_punctuation.setText(_('Update punctuation'))
        self.punc_settings_btn.setText(_('Settings...'))

        self.book_source_button.setText(_('Entire eBook'))
        self.file_source_button.setText(_('Current File'))
        self.seltext_source_button.setText(_('Tagged Text in Current File'))
        self.seltext_source_button.setToolTip(
            _('“Tagged Text” is bracketed by <!--PI_SELTEXT_START--> and <!--PI_SELTEXT_END-->'))
        self.source_group_box.setTitle(_('Source'))
        self.ui_lang_combo.blockSignals(False)
        self.about_btn.setText(_('About'))
        self.check_updates_btn.setText(_('Check for updates'))
        self._translate_standard_buttons(self.button_box)

        if self.punctuation_dialog is not None:
            self.punctuation_dialog.apply_translations()

    def _translate_standard_buttons(self, button_box):
        ok_btn = button_box.button(QDialogButtonBox.Ok)
        cancel_btn = button_box.button(QDialogButtonBox.Cancel)
        if ok_btn is not None:
            ok_btn.setText(_('Start Processing') if self.force_entire_book else _('OK'))
        if cancel_btn is not None:
            cancel_btn.setText(_('Cancel'))

    def on_op_button_clicked(self, btn):
        self.block_signals(True)
        if btn == self.no_conversion_button:
            self.input_combo.setCurrentIndex(-1)  # blank out the entry
            self.output_combo.setCurrentIndex(-1) # blank out the entry
        else:
            self._apply_locale_defaults_for_selected_direction(
                normalize_ui_language(self.prefs.get('ui_language', detect_calibre_ui_language())))
        self.block_signals(False)
        self.update_gui()
        self._apply_symbol_profile_default()

    def block_signals(self, state):
        # block or unblock the signals generated by these objects to avoid recursive calls
        self.input_combo.blockSignals(state)
        self.output_combo.blockSignals(state)
        self.use_target_phrases.blockSignals(state)
        self.no_conversion_button.blockSignals(state)
        self.trad_to_simp_button.blockSignals(state)
        self.simp_to_trad_button.blockSignals(state)
        self.trad_to_trad_button.blockSignals(state)
        self.file_source_button.blockSignals(state)
        self.seltext_source_button.blockSignals(state)
        self.book_source_button.blockSignals(state)
        self.quotation_trad_to_simp_button.blockSignals(state)
        self.quotation_simp_to_trad_button.blockSignals(state)
        self.quotation_no_change_button.blockSignals(state)
        self.text_dir_no_change_button.blockSignals(state)
        self.text_dir_horizontal_button.blockSignals(state)
        self.text_dir_vertical_button.blockSignals(state)
        self.update_punctuation.blockSignals(state)


    def set_to_preferences(self):
        # set the gui values to match those in the preferences
        self.block_signals(True)

        self.input_combo.setCurrentIndex(self.prefs['input_locale'])
        self.output_combo.setCurrentIndex(self.prefs['output_locale'])
        self.use_target_phrases.setChecked(bool(self.prefs.get('use_target_phrases', True)))

        if self.prefs['conversion_type'] == 0:
            self.no_conversion_button.setChecked(True)
        elif self.prefs['conversion_type'] == 1:
            self.trad_to_simp_button.setChecked(True)
        elif self.prefs['conversion_type'] == 2:
            self.simp_to_trad_button.setChecked(True)
        else:
            self.trad_to_trad_button.setChecked(True)

        if not self.force_entire_book:
            if self.prefs['input_source'] == 1:
                self.file_source_button.setChecked(True)
            elif self.prefs['input_source'] == 2:
                self.seltext_source_button.setChecked(True)
            else:
                self.book_source_button.setChecked(True)
        else:
            self.book_source_button.setChecked(True)
            self.file_source_button.setChecked(False)
            self.seltext_source_button.setChecked(False)

        if self.prefs['quotation_type'] == 1:
            self.quotation_trad_to_simp_button.setChecked(True)
        elif self.prefs['quotation_type'] == 2:
            self.quotation_simp_to_trad_button.setChecked(True)
        else:
            self.quotation_no_change_button.setChecked(True)

        self._set_output_orientation_index(self.prefs['output_orientation'])
        self.update_punctuation.setChecked(self.prefs['update_punctuation'])

        self.block_signals(False)


    def direction_changed(self):
        # callback when text direction changes
        # punctuation toggle is independent from text direction.
        self.update_gui()

    def update_gui(self):
        # callback to update other gui items when one changes
        show_trad_help = self.trad_to_trad_button.isChecked()
        if self.no_conversion_button.isChecked():
            self.input_combo.setEnabled(False)
            self.output_combo.setEnabled(False)
            self.input_combo.setToolTip(_('Valid input/output combinations:\nNot Applicable'))
            self.output_combo.setToolTip(_('Valid input/output combinations:\nNot Applicable'))
            self.output_region_label.setEnabled(False)
            self.input_region_label.setEnabled(False)
            self.style_group_box.setEnabled(False)

        elif self.trad_to_simp_button.isChecked():
            self.input_combo.setEnabled(True)
            self.output_combo.setEnabled(True)
            self.use_target_phrases.setEnabled(True)
            self.output_region_label.setEnabled(True)
            self.input_region_label.setEnabled(True)
            self.input_combo.setToolTip(_('Valid input/output combinations:\nHong Kong/Mainland\nMainland/Mainland\nTaiwan/Mainland\nMainland/Japan'))
            self.output_combo.setToolTip(_('Valid input/output combinations:\nHong Kong/Mainland\nMainland/Mainland\nTaiwan/Mainland\nMainland/Japan'))
            self.style_group_box.setEnabled(True)

        elif self.simp_to_trad_button.isChecked():
            self.input_combo.setEnabled(True)
            self.output_combo.setEnabled(True)
            self.input_combo.setToolTip(_('Valid input/output combinations:\nMainland/Hong Kong\nMainland/Mainland\nMainland/Taiwan\nJapan/Mainland'))
            self.output_combo.setToolTip(_('Valid input/output combinations:\nMainland/Hong Kong\nMainland/Mainland\nMainland/Taiwan\nJapan/Mainland'))
            self.output_region_label.setEnabled(True)
            self.input_region_label.setEnabled(True)
            self.style_group_box.setEnabled(True)

        elif self.trad_to_trad_button.isChecked():
            self.input_combo.setEnabled(True)
            self.output_combo.setEnabled(True)
            self.input_combo.setToolTip(_('Valid input/output combinations:\nHong Kong/Mainland\nMainland/Hong Kong\nTaiwan/Mainland\nMainland/Taiwan\nMainland/Mainland\nHong Kong/Hong Kong\nTaiwan/Taiwan'))
            self.output_combo.setToolTip(_('Valid input/output combinations:\nHong Kong/Mainland\nMainland/Hong Kong\nTaiwan/Mainland\nMainland/Taiwan\nMainland/Mainland\nHong Kong/Hong Kong\nTaiwan/Taiwan'))
            self.output_region_label.setEnabled(True)
            self.input_region_label.setEnabled(True)
            self.style_group_box.setEnabled(True)

        # Keep phrase option independent from conversion-direction toggles.
        self.use_target_phrases.setEnabled(True)

        self.update_punctuation.blockSignals(True)
        self.update_punctuation.setEnabled(True)
        self.update_punctuation.blockSignals(False)

        if self.update_punctuation.isChecked():
            self.punc_settings_btn.setEnabled(True)
        else:
            self.punc_settings_btn.setEnabled(False)

        self.trad_to_trad_help_row.setVisible(show_trad_help)
        self.trad_to_trad_help.setVisible(show_trad_help)


    def _ok_clicked(self):
        # save current settings into preferences and close dialog
        self.savePrefs()
        self.accept()


    def _reject_clicked(self):
        # restore initial settings and close dialog
        self.set_to_preferences()
        self.update_gui()
        self.reject()


    def punc_settings_btn_clicked(self):
        # open the punctuation dialog
        self.punctuation_dialog.exec_()


    def on_button_toggled(self, checked):
        # The whole file radio button changed state
        if not checked:
            # set direction to no change
            # disable text direction changes
            self._set_output_orientation_index(0)
            self._set_text_direction_enabled(False)
        else:
            self._set_text_direction_enabled(True)

    def savePrefs(self):
        # save the current settings into the preferences
        self.prefs['ui_language'] = normalize_ui_language(
            self.ui_lang_combo.currentIndex())
        self.prefs['profile_ui_language'] = self.prefs['ui_language']
        self.prefs['has_user_preferences'] = True
        self.prefs['input_locale'] = self.input_combo.currentIndex()
        self.prefs['output_locale'] = self.output_combo.currentIndex()
        # Persist current locale choices as explicit user preferences.
        self.input_locale_user_set = True
        self.output_locale_user_set = True
        self.prefs['input_locale_user_set'] = True
        self.prefs['output_locale_user_set'] = True

        if self.trad_to_simp_button.isChecked():
            self.prefs['conversion_type'] = 1
        elif self.simp_to_trad_button.isChecked():
            self.prefs['conversion_type'] = 2
        elif self.trad_to_trad_button.isChecked():
            self.prefs['conversion_type'] = 3
        else:
            self.prefs['conversion_type'] = 0

        if self.force_entire_book:
            self.prefs['input_source'] = 0
        elif self.file_source_button.isChecked():
            self.prefs['input_source'] = 1
        elif self.seltext_source_button.isChecked():
            self.prefs['input_source'] = 2
        else:
            self.prefs['input_source'] = 0

        self.prefs['use_target_phrases'] = self.use_target_phrases.isChecked()

        if self.quotation_trad_to_simp_button.isChecked():
            self.prefs['quotation_type'] = 1
        elif self.quotation_simp_to_trad_button.isChecked():
            self.prefs['quotation_type'] = 2
        else:
            self.prefs['quotation_type'] = 0

        self.prefs['output_orientation'] = self._output_orientation_index()
        # Once user runs conversion with current settings, persist this as
        # recent preferred orientation and avoid language-based auto-overrides.
        self.output_orientation_user_set = True
        self.prefs['output_orientation_user_set'] = True
        self.prefs['symbol_profile_user_set'] = self.symbol_profile_user_set
        self.prefs['update_punctuation'] = self.update_punctuation.isChecked()


    def getRegex(self):
        # getter for the punctuation conversion regular expression object
        return self.punctuation_dialog.getRegex()


class LibraryConversionStatusDialog(QDialog):
    '''Processing / complete status and text preview when converting library books.'''

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowTitle(_('Chinese Conversion'))
        self.setMinimumSize(LIBRARY_STATUS_DIALOG_SIZE)
        self.resize(LIBRARY_STATUS_DIALOG_SIZE)

        layout = QVBoxLayout(self)
        configure_layout(layout, 'dialog')

        self.headline = QLabel()
        font = self.headline.font()
        font.setBold(True)
        self.headline.setFont(font)
        layout.addWidget(self.headline)

        self.preview = QPlainTextEdit(self)
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(320)
        layout.addWidget(self.preview, stretch=1)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.close_btn = self.button_box.button(QDialogButtonBox.Close)
        self.close_btn.setEnabled(False)
        self.close_btn.setText(_('Close'))
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(make_section_divider(self))
        layout.addWidget(self.button_box)
        apply_dialog_stylesheet(self)

        self.set_processing()

    def set_processing(self):
        self.headline.setText(_('Processing…'))
        self.close_btn.setEnabled(False)

    def set_complete(self):
        self.headline.setText(_('Processing complete'))
        self.close_btn.setEnabled(True)

    def apply_translations(self):
        self.setWindowTitle(_('Chinese Conversion'))
        self.close_btn.setText(_('Close'))
        if self.close_btn.isEnabled():
            self.headline.setText(_('Processing complete'))
        else:
            self.headline.setText(_('Processing…'))

    def append_preview(self, text):
        self.preview.appendPlainText(text)
        self.preview.verticalScrollBar().setValue(
            self.preview.verticalScrollBar().maximum())
        QApplication.processEvents()

    def log_processing(self, message):
        self.append_preview(message)

    def log_result(self, message):
        self.append_preview(message)


class PuncuationDialog(Dialog):

    def __init__(self, parent, prefs, punc_dict, default_omitted_puncuation):
        self.prefs = prefs
        self.punc_dict = punc_dict
        self.default_omitted_puncuation = default_omitted_puncuation
        self.parent = parent
        self.puncSettings = set()
        Dialog.__init__(self, _('Chinese Punctuation'), 'chinese_conversion_punctuation_dialog', parent)


    def setup_ui(self):
        self.punc_setting = {}
        self.checkbox_dict = {}

        layout = QVBoxLayout(self)
        self.setLayout(layout)
        configure_layout(layout, 'dialog')

        self.scrollArea = QScrollArea(self)
        polish_scroll_area(self.scrollArea)
        self.scrollArea.setWidgetResizable(True)

        self.scrollContentWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollContentWidget)
        widgetLayout = QVBoxLayout(self.scrollContentWidget)
        configure_layout(widgetLayout, 'sections')

        layout.addWidget(self.scrollArea, stretch=1)

        self.punctuation_group_box = QGroupBox(_('Punctuation'))
        widgetLayout.addWidget(self.punctuation_group_box)


        self.punctuation_group_box_layout = QVBoxLayout()
        configure_layout(self.punctuation_group_box_layout, 'section')
        self.punctuation_group_box.setLayout(self.punctuation_group_box_layout)

        for x in self.punc_dict:
            str = x + " <-> " + self.punc_dict[x]
            widget = QCheckBox(str)
            self.checkbox_dict[x] = widget
            self.punctuation_group_box_layout.addWidget(widget)
            if x in self.prefs['punc_omits']:
                widget.setChecked(False)
            else:
                widget.setChecked(True)


        self.button_box_settings = QDialogButtonBox()
        self.clearall_button = self.button_box_settings.addButton(
            _('Clear All'), QDialogButtonBox.ActionRole)
        self.setall_button = self.button_box_settings.addButton(
            _('Set All'), QDialogButtonBox.ActionRole)
        self.default_button = self.button_box_settings.addButton(
            _('Default'), QDialogButtonBox.ActionRole)
        self.button_box_settings.clicked.connect(self._action_clicked)
        layout.addWidget(self.button_box_settings)

        layout.addWidget(make_section_divider(self))
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._ok_clicked)
        self.button_box.rejected.connect(self._reject_clicked)
        layout.addWidget(self.button_box)
        apply_dialog_stylesheet(self)
        self.apply_translations()

    def apply_translations(self):
        self.setWindowTitle(_('Chinese Punctuation'))
        self.punctuation_group_box.setTitle(_('Punctuation'))
        self.clearall_button.setText(_('Clear All'))
        self.setall_button.setText(_('Set All'))
        self.default_button.setText(_('Default'))
        ok_btn = self.button_box.button(QDialogButtonBox.Ok)
        cancel_btn = self.button_box.button(QDialogButtonBox.Cancel)
        if ok_btn is not None:
            ok_btn.setText(_('OK'))
        if cancel_btn is not None:
            cancel_btn.setText(_('Cancel'))

    def savePrefs(self):
        setting = ""
        for x in self.puncSettings:
            setting = setting + x
        self.prefs['punc_omits'] = setting


    def _ok_clicked(self):
        self.puncSettings.clear()
        # Loop through and update set of unchecked items
        for x in self.checkbox_dict.keys():
            if not self.checkbox_dict[x].isChecked():
                self.puncSettings.add(x)
        self.savePrefs()
        self.accept()


    def _reject_clicked(self):
        # Restore back to values when first opened
        # This will be the same as the preferences
        ## loop through all checkboxes
        for x in self.checkbox_dict.keys():
            self.checkbox_dict[x].blockSignals(True)
            if x in self.prefs['punc_omits']:
                self.checkbox_dict[x].setChecked(False)
            else:
                self.checkbox_dict[x].setChecked(True)
            self.checkbox_dict[x].blockSignals(False)
        self.reject()


    def _action_clicked(self, button):
        ## Find out which button is pressed
        if button is self.clearall_button:
            ## loop through all checkboxes and unset
            for x in self.checkbox_dict.values():
                x.blockSignals(True)
                x.setChecked(False)
                x.blockSignals(False)

        elif button is self.setall_button:
            ## loop through all checkboxes and set
            for x in self.checkbox_dict.values():
                x.blockSignals(True)
                x.setChecked(True)
                x.blockSignals(False)

        elif button is self.default_button:
            ## loop through all checkboxes
            for x in self.checkbox_dict.keys():
                self.checkbox_dict[x].blockSignals(True)
                if x in self.default_omitted_puncuation:
                    self.checkbox_dict[x].setChecked(False)
                else:
                    self.checkbox_dict[x].setChecked(True)
                self.checkbox_dict[x].blockSignals(False)

