# -*- coding: utf-8 -*-

__license__   = 'GPL v3'

import os, re

try:
    from qt.core import (Qt, QVBoxLayout, QLabel, QComboBox, QApplication, QSizePolicy,
                  QGroupBox, QButtonGroup, QRadioButton, QDialogButtonBox, QHBoxLayout,
                  QProgressDialog, QSize, QDialog, QCheckBox, QSpinBox, QScrollArea, QWidget,
                  QPushButton, QPlainTextEdit)
except ImportError:
    from PyQt5.Qt import (Qt, QVBoxLayout, QLabel, QComboBox, QApplication, QSizePolicy,
                          QGroupBox, QButtonGroup, QRadioButton, QDialogButtonBox, QHBoxLayout,
                          QProgressDialog, QSize, QDialog, QCheckBox, QSpinBox, QScrollArea, QWidget,
                          QPushButton, QPlainTextEdit)

from calibre.utils.config import config_dir

from calibre.gui2.tweak_book.widgets import Dialog

from calibre_plugins.chinese_text_conversion import PLUGIN_VERSION
from calibre_plugins.chinese_text_conversion.i18n import (
    _, apply_ui_language_from_prefs, detect_calibre_ui_language,
    normalize_ui_language, ui_language_combo_items,
    UI_LANG_EN, UI_LANG_ZH_CN, UI_LANG_ZH_TW, UI_LANG_ZH_HK, TRADITIONAL_UI_LANGS,
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
LIBRARY_CONVERSION_DIALOG_SIZE = QSize(760, 680)
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

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        self.title_label = QLabel()
        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(title_font.pointSize() + 2)
        self.title_label.setFont(title_font)
        content_layout.addWidget(self.title_label)

        self.version_label = QLabel()
        content_layout.addWidget(self.version_label)

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

        content_layout.addStretch(1)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        layout.addWidget(self.button_box)

    def apply_translations(self):
        self.setWindowTitle(_('About Chinese Text Conversion'))
        self.title_label.setText(_('About Chinese Text Conversion'))
        self.version_label.setText(_('Version {}').format(PLUGIN_VERSION))
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
        ok_btn = self.button_box.button(QDialogButtonBox.Ok)
        if ok_btn is not None:
            ok_btn.setText(_('Got it'))

    def mark_first_run_complete(self):
        if self.first_run:
            self.prefs['about_shown'] = True
            self.prefs.commit()


class ConversionDialog(Dialog):
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
        return QSize(640, 560)

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

        # Create layout for entire dialog
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        lang_layout = QHBoxLayout()
        layout.addLayout(lang_layout)
        self.ui_lang_label = QLabel(_('Interface Language:'))
        lang_layout.addWidget(self.ui_lang_label)
        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.addItems(ui_language_combo_items())
        self.ui_lang_combo.setCurrentIndex(
            normalize_ui_language(self.prefs.get(
                'ui_language', detect_calibre_ui_language())))
        self.ui_lang_combo.currentIndexChanged.connect(self.on_ui_language_changed)
        lang_layout.addWidget(self.ui_lang_combo)

        #Create a scroll area for the top part of the dialog
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        # Create widget for all the contents of the dialog except the OK and Cancel buttons
        self.scrollContentWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollContentWidget)
        widgetLayout = QVBoxLayout(self.scrollContentWidget)

        # Add scrollArea to dialog
        layout.addWidget(self.scrollArea)

        self.operation_group_box = QGroupBox(_('Conversion Direction'))
        widgetLayout.addWidget(self.operation_group_box)
        operation_group_box_layout = QVBoxLayout()
        operation_group_box_layout.setSpacing(4)
        self.operation_group_box.setLayout(operation_group_box_layout)

        self.operation_group=QButtonGroup(self)
        self.no_conversion_button = QRadioButton(_('No Conversion'))
        self.operation_group.addButton(self.no_conversion_button)
        self.trad_to_simp_button = QRadioButton(_('Traditional to Simplified'))
        self.operation_group.addButton(self.trad_to_simp_button)
        self.simp_to_trad_button = QRadioButton(_('Simplified to Traditional'))
        self.operation_group.addButton(self.simp_to_trad_button)
        self.trad_to_trad_button = QRadioButton(_('Traditional to Traditional'))
        self.operation_group.addButton(self.trad_to_trad_button)

        operation_radio_layout = QVBoxLayout()
        operation_radio_layout.setContentsMargins(0, 0, 0, 0)
        operation_radio_layout.setSpacing(8)
        operation_radio_layout.addWidget(self.no_conversion_button)
        operation_radio_layout.addWidget(self.trad_to_simp_button)
        operation_radio_layout.addWidget(self.simp_to_trad_button)
        operation_radio_layout.addWidget(self.trad_to_trad_button)
        operation_group_box_layout.addLayout(operation_radio_layout)

        self.trad_to_trad_help = QLabel()
        self.trad_to_trad_help.setWordWrap(True)
        self.trad_to_trad_help.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        trad_to_trad_help_row = QWidget()
        trad_to_trad_help_layout = QHBoxLayout(trad_to_trad_help_row)
        trad_to_trad_help_layout.setContentsMargins(22, 0, 0, 0)
        trad_to_trad_help_layout.addWidget(self.trad_to_trad_help)
        operation_group_box_layout.addWidget(trad_to_trad_help_row)
        self._update_trad_to_trad_help_text()
        self.operation_group.buttonClicked.connect(self.on_op_button_clicked)

        self.style_group_box = QGroupBox(_('Language Styles'))
        widgetLayout.addWidget(self.style_group_box)
        style_group_box_layout = QVBoxLayout()
        self.style_group_box.setLayout(style_group_box_layout)

        input_layout = QHBoxLayout()
        style_group_box_layout.addLayout(input_layout)
        self.input_region_label = QLabel(_('Input:'))
        input_layout.addWidget(self.input_region_label)
        self.input_combo = QComboBox()
        input_layout.addWidget(self.input_combo)
        self.input_combo.addItems([_('Mainland'), _('Hong Kong'), _('Taiwan'), _('Japan')])
        self.input_combo.setToolTip(_('Select the origin region of the input'))
        self.input_combo.currentIndexChanged.connect(self.update_gui)
        self.input_combo.activated.connect(self._mark_input_locale_user_set)

        output_layout = QHBoxLayout()
        style_group_box_layout.addLayout(output_layout)
        self.output_region_label = QLabel(_('Output:'))
        output_layout.addWidget(self.output_region_label)
        self.output_combo = QComboBox()
        output_layout.addWidget(self.output_combo)
        self.output_combo.addItems([_('Mainland'), _('Hong Kong'), _('Taiwan'), _('Japan')])
        self.output_combo.setToolTip(_('Select the desired region of the output'))
        self.output_combo.currentIndexChanged.connect(self.update_gui)
        self.output_combo.activated.connect(self._mark_output_locale_user_set)

        self.use_target_phrases = QCheckBox(_('Use output target phrases if possible'))
        style_group_box_layout.addWidget(self.use_target_phrases)
        self.use_target_phrases_help = QLabel()
        self.use_target_phrases_help.setWordWrap(True)
        self.use_target_phrases_help.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        style_group_box_layout.addWidget(self.use_target_phrases_help)
        self._update_target_phrases_help_text()
        self.use_target_phrases.stateChanged.connect(self.update_gui)

        self.quotation_group_box = QGroupBox(_('Quotation Marks'))
        widgetLayout.addWidget(self.quotation_group_box)
        quotation_group_box_layout = QVBoxLayout()
        self.quotation_group_box.setLayout(quotation_group_box_layout)

        quotation_group=QButtonGroup(self)
        self.quotation_no_conversion_button = QRadioButton(_('No Conversion'))
        quotation_group.addButton(self.quotation_no_conversion_button)
        self.quotation_trad_to_simp_button = QRadioButton(self.quote_for_simp_target)
        quotation_group.addButton(self.quotation_trad_to_simp_button)
        self.quotation_simp_to_trad_button = QRadioButton(self.quote_for_trad_target)
        quotation_group.addButton(self.quotation_simp_to_trad_button)
        quotation_group_box_layout.addWidget(self.quotation_no_conversion_button)
        quotation_group_box_layout.addWidget(self.quotation_simp_to_trad_button)
        quotation_group_box_layout.addWidget(self.quotation_trad_to_simp_button)
        self.quotation_no_conversion_button.toggled.connect(self.update_gui)
        self.quotation_trad_to_simp_button.toggled.connect(self.update_gui)
        self.quotation_simp_to_trad_button.toggled.connect(self.update_gui)

        self.other_group_box = QGroupBox(_('Other Changes'))
        widgetLayout.addWidget(self.other_group_box)
        other_group_box_layout = QVBoxLayout()
        self.other_group_box.setLayout(other_group_box_layout)

        text_dir_layout = QHBoxLayout()
        other_group_box_layout.addLayout(text_dir_layout)
        self.direction_label = QLabel(_('Text Direction:'))
        text_dir_layout.addWidget(self.direction_label)
        self.text_dir_combo = QComboBox()
        text_dir_layout.addWidget(self.text_dir_combo)
        self.text_dir_combo.addItems([_('No Change'), _('Horizontal'), _('Vertical')])
        self.text_dir_combo.setToolTip(_('Select the desired text orientation'))
        self.text_dir_combo.currentIndexChanged.connect(self.direction_changed)
        self.text_dir_combo.activated.connect(self._mark_output_orientation_user_set)

        punctuation_layout = QHBoxLayout()
        other_group_box_layout.addLayout(punctuation_layout)
        self.update_punctuation = QCheckBox(_('Update punctuation'))
        punctuation_layout.addWidget(self.update_punctuation)
        self.update_punctuation.stateChanged.connect(self.update_gui)
        self.punc_settings_btn = QPushButton()
        self.punc_settings_btn.setText(_('Settings...'))

        punctuation_layout.addWidget(self.punc_settings_btn)
        self.punc_settings_btn.clicked.connect(self.punc_settings_btn_clicked)
        self.punctuation_dialog = None

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
            widgetLayout.addWidget(self.source_group_box)
            source_group_box_layout = QVBoxLayout()
            self.source_group_box.setLayout(source_group_box_layout)
            source_group_box_layout.addWidget(self.book_source_button)
            source_group_box_layout.addWidget(self.file_source_button)
            source_group_box_layout.addWidget(self.seltext_source_button)

        self.book_source_button.toggled.connect(self.on_button_toggled)

        layout.addSpacing(10)
        footer_layout = QHBoxLayout()
        self.about_btn = QPushButton()
        self.about_btn.clicked.connect(self._show_about_dialog)
        footer_layout.addWidget(self.about_btn)
        footer_layout.addStretch(1)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._ok_clicked)
        self.button_box.rejected.connect(self._reject_clicked)
        footer_layout.addWidget(self.button_box)
        layout.addLayout(footer_layout)

        self.set_to_preferences()
        self.apply_translations()
        self.update_gui()
        ui_lang = normalize_ui_language(
            self.prefs.get('ui_language', detect_calibre_ui_language()))
        if self.prefs.get('conversion_type', 0) == 0:
            self._apply_conversion_direction_for_ui_language(ui_lang)
        if self.prefs.get('quotation_type', 0) == 0:
            self._apply_quotation_for_ui_language(ui_lang)
        self.about_btn.setText(_('About'))
        if not self.prefs.get('about_shown', True):
            self._show_about_dialog(first_run=True)

    def _show_about_dialog(self, first_run=False):
        dlg = PluginAboutDialog(self.parent, self.prefs, first_run=first_run)
        dlg.exec_()
        dlg.mark_first_run_complete()

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

    def _apply_language_style_defaults_for_ui_language(self, lang_index):
        '''仅在用户未手动改动时按界面语言给出输入/输出默认建议。'''
        changed = False
        self.block_signals(True)
        if lang_index == UI_LANG_ZH_CN:
            if not self.input_locale_user_set:
                self.input_combo.setCurrentIndex(2)   # Taiwan
                changed = True
            if not self.output_locale_user_set:
                self.output_combo.setCurrentIndex(0)  # Mainland
                changed = True
        elif lang_index in TRADITIONAL_UI_LANGS:
            output_locale = self._ui_output_locale(lang_index)
            if not self.input_locale_user_set:
                self.input_combo.setCurrentIndex(0)   # Mainland
                changed = True
            if (output_locale is not None) and (not self.output_locale_user_set):
                self.output_combo.setCurrentIndex(output_locale)
                changed = True
        self.block_signals(False)
        if changed:
            self.update_gui()

    def _apply_output_orientation_default_for_ui_language(self, lang_index):
        '''仅在用户未手动改动时按界面语言给出文字方向默认建议。'''
        if self.output_orientation_user_set:
            return
        if lang_index == UI_LANG_ZH_CN:
            target_idx = 1  # Horizontal
        elif lang_index in TRADITIONAL_UI_LANGS:
            target_idx = 2  # Vertical
        else:
            return
        self.block_signals(True)
        self.text_dir_combo.setCurrentIndex(target_idx)
        self.block_signals(False)
        self.direction_changed()
        self.update_gui()

    def _apply_quotation_for_ui_language(self, lang_index):
        '''简体界面 → 「」→“”；繁体界面 → “”→「」（常见转换习惯）。'''
        if lang_index not in (UI_LANG_ZH_CN,) and lang_index not in TRADITIONAL_UI_LANGS:
            return
        for btn in (
            self.quotation_no_conversion_button,
            self.quotation_trad_to_simp_button,
            self.quotation_simp_to_trad_button,
        ):
            btn.blockSignals(True)
        if lang_index == UI_LANG_ZH_CN:
            self.quotation_trad_to_simp_button.setChecked(True)
        else:
            self.quotation_simp_to_trad_button.setChecked(True)
        for btn in (
            self.quotation_no_conversion_button,
            self.quotation_trad_to_simp_button,
            self.quotation_simp_to_trad_button,
        ):
            btn.blockSignals(False)

    def on_ui_language_changed(self, index):
        from calibre_plugins.chinese_text_conversion.i18n import set_ui_language
        lang_index = normalize_ui_language(index)
        self.prefs['ui_language'] = lang_index
        set_ui_language(lang_index)
        self.apply_translations()
        self._apply_conversion_direction_for_ui_language(lang_index)
        self._apply_language_style_defaults_for_ui_language(lang_index)
        self._apply_quotation_for_ui_language(lang_index)
        self._apply_output_orientation_default_for_ui_language(lang_index)
        self.update_gui()

    def _mark_input_locale_user_set(self, *_args):
        self.input_locale_user_set = True

    def _mark_output_locale_user_set(self, *_args):
        self.output_locale_user_set = True

    def _mark_output_orientation_user_set(self, *_args):
        self.output_orientation_user_set = True

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

        self.quotation_group_box.setTitle(_('Quotation Marks'))
        self.quotation_no_conversion_button.setText(_('No Conversion'))
        self.quotation_trad_to_simp_button.setText(self.quote_for_simp_target)
        self.quotation_simp_to_trad_button.setText(self.quote_for_trad_target)

        self.other_group_box.setTitle(_('Other Changes'))
        self.direction_label.setText(_('Text Direction:'))
        text_dir_idx = self.text_dir_combo.currentIndex()
        self.text_dir_combo.blockSignals(True)
        self.text_dir_combo.clear()
        self.text_dir_combo.addItems([_('No Change'), _('Horizontal'), _('Vertical')])
        if text_dir_idx >= 0:
            self.text_dir_combo.setCurrentIndex(text_dir_idx)
        self.text_dir_combo.blockSignals(False)
        self.text_dir_combo.setToolTip(_('Select the desired text orientation'))
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
            self.input_combo.setCurrentIndex(0)   # mainland
            self.output_combo.setCurrentIndex(0)  # mainland
        self.block_signals(False)
        self.update_gui()

    def block_signals(self, state):
        # block or unblock the signals generated by these objects to avoid recursive calls
        self.input_combo.blockSignals(state)
        self.output_combo.blockSignals(state)
        self.no_conversion_button.blockSignals(state)
        self.trad_to_simp_button.blockSignals(state)
        self.simp_to_trad_button.blockSignals(state)
        self.trad_to_trad_button.blockSignals(state)
        self.file_source_button.blockSignals(state)
        self.seltext_source_button.blockSignals(state)
        self.book_source_button.blockSignals(state)
        self.quotation_trad_to_simp_button.blockSignals(state)
        self.quotation_simp_to_trad_button.blockSignals(state)
        self.quotation_no_conversion_button.blockSignals(state)
        self.text_dir_combo.blockSignals(state)
        self.update_punctuation.blockSignals(state)


    def set_to_preferences(self):
        # set the gui values to match those in the preferences
        self.block_signals(True)

        self.input_combo.setCurrentIndex(self.prefs['input_locale'])
        self.output_combo.setCurrentIndex(self.prefs['output_locale'])

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
            self.quotation_no_conversion_button.setChecked(True)

        self.text_dir_combo.setCurrentIndex(self.prefs['output_orientation'])
        if self.text_dir_combo.currentIndex() == 0:
            self.update_punctuation.setChecked(False)
        else:
            self.update_punctuation.setChecked(self.prefs['update_punctuation'])

        self.block_signals(False)


    def direction_changed(self):
        # callback when text direction changes
        self.update_punctuation.blockSignals(True)
        self.punc_settings_btn.blockSignals(True)

        if self.text_dir_combo.currentIndex() == 0:    # no direction change
            self.update_punctuation.setChecked(False)
            self.update_punctuation.setEnabled(False)
            self.punc_settings_btn.setEnabled(False)

        else:
            self.update_punctuation.setChecked(True)
            self.update_punctuation.setEnabled(True)
            self.punc_settings_btn.setEnabled(True)

        self.punc_settings_btn.blockSignals(False)
        self.update_punctuation.blockSignals(False)

    def update_gui(self):
        # callback to update other gui items when one changes
        if self.no_conversion_button.isChecked():
            self.input_combo.setEnabled(False)
            self.output_combo.setEnabled(False)
            self.input_combo.setToolTip(_('Valid input/output combinations:\nNot Applicable'))
            self.output_combo.setToolTip(_('Valid input/output combinations:\nNot Applicable'))
            self.use_target_phrases.setEnabled(False)
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
            self.use_target_phrases.setEnabled(True)
            self.output_region_label.setEnabled(True)
            self.input_region_label.setEnabled(True)
            self.style_group_box.setEnabled(True)

        elif self.trad_to_trad_button.isChecked():
            self.input_combo.setEnabled(True)
            self.output_combo.setEnabled(True)
            self.input_combo.setToolTip(_('Valid input/output combinations:\nHong Kong/Mainland\nMainland/Hong Kong\nTaiwan/Mainland\nMainland/Taiwan\nMainland/Mainland\nHong Kong/Hong Kong\nTaiwan/Taiwan'))
            self.output_combo.setToolTip(_('Valid input/output combinations:\nHong Kong/Mainland\nMainland/Hong Kong\nTaiwan/Mainland\nMainland/Taiwan\nMainland/Mainland\nHong Kong/Hong Kong\nTaiwan/Taiwan'))
            self.use_target_phrases.setEnabled(True)
            self.output_region_label.setEnabled(True)
            self.input_region_label.setEnabled(True)
            self.style_group_box.setEnabled(True)

        if self.text_dir_combo.currentIndex() == 0:
            self.update_punctuation.blockSignals(True)
            self.update_punctuation.setChecked(False)
            self.update_punctuation.setEnabled(False)
            self.update_punctuation.blockSignals(False)
        else:
            self.update_punctuation.blockSignals(True)
            self.update_punctuation.setEnabled(True)
            self.update_punctuation.blockSignals(False)

        if self.update_punctuation.isChecked():
            self.punc_settings_btn.setEnabled(True)
        else:
            self.punc_settings_btn.setEnabled(False)


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
            self.text_dir_combo.setCurrentIndex(0)
            self.text_dir_combo.setEnabled(False)
        else:
            # enable text direction changes
            self.text_dir_combo.setEnabled(True)

    def savePrefs(self):
        # save the current settings into the preferences
        self.prefs['ui_language'] = normalize_ui_language(
            self.ui_lang_combo.currentIndex())
        self.prefs['input_locale'] = self.input_combo.currentIndex()
        self.prefs['output_locale'] = self.output_combo.currentIndex()
        self.prefs['input_locale_user_set'] = self.input_locale_user_set
        self.prefs['output_locale_user_set'] = self.output_locale_user_set

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

        self.prefs['output_orientation'] = self.text_dir_combo.currentIndex()
        self.prefs['output_orientation_user_set'] = self.output_orientation_user_set
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
        layout.addWidget(self.button_box)

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

        # Create layout for entire dialog
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        #Create a scroll area for the top part of the dialog
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        # Create widget for all the contents of the dialog except the buttons
        self.scrollContentWidget = QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollContentWidget)
        widgetLayout = QVBoxLayout(self.scrollContentWidget)

        # Add scrollArea to dialog
        layout.addWidget(self.scrollArea)

        self.punctuation_group_box = QGroupBox(_('Punctuation'))
        widgetLayout.addWidget(self.punctuation_group_box)


        self.punctuation_group_box_layout = QVBoxLayout()
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

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._ok_clicked)
        self.button_box.rejected.connect(self._reject_clicked)
        layout.addWidget(self.button_box)
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

