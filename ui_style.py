# -*- coding: utf-8 -*-

__license__ = 'GPL 3'

'''Shared spacing, typography, and branding for plugin dialogs.'''

try:
    from qt.core import (
        QButtonGroup, QFrame, QGroupBox, QHBoxLayout, QLabel, QPalette, QPixmap,
        QRadioButton, QSizePolicy, QVBoxLayout, QWidget,
    )
except ImportError:
    from PyQt5.Qt import (
        QButtonGroup, QFrame, QGroupBox, QHBoxLayout, QLabel, QPalette, QPixmap,
        QRadioButton, QSizePolicy, QVBoxLayout, QWidget,
    )

ICON_RESOURCE = 'images/TradSimpIcon.png'
BRAND_ICON_PX = 40

# 8px spacing scale
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 20

DIALOG_MARGIN = SPACE_XL
DIALOG_SPACING = SPACE_LG
SECTION_SPACING = SPACE_MD
SECTION_INNER_SPACING = SPACE_SM
RADIO_SPACING = 6
FORM_ROW_SPACING = SPACE_SM
FORM_LABEL_MIN_WIDTH = 72
HELP_TEXT_INDENT = 20
FOOTER_TOP_MARGIN = SPACE_MD

BRAND_HEADER_ID = 'tradSimpBrandHeader'
BRAND_TITLE_ID = 'tradSimpBrandTitle'
BRAND_SUBTITLE_ID = 'tradSimpBrandSubtitle'
DIVIDER_ID = 'tradSimpSectionDivider'


def configure_layout(layout, role='section'):
    '''Apply consistent margins and spacing to a layout.'''
    if layout is None:
        return
    if role == 'dialog':
        layout.setContentsMargins(DIALOG_MARGIN, DIALOG_MARGIN, DIALOG_MARGIN, DIALOG_MARGIN)
        layout.setSpacing(DIALOG_SPACING)
    elif role == 'sections':
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SECTION_SPACING)
    elif role == 'section':
        layout.setContentsMargins(SPACE_LG, SPACE_MD, SPACE_LG, SPACE_MD)
        layout.setSpacing(SECTION_INNER_SPACING)
    elif role == 'radio':
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(RADIO_SPACING)
    elif role == 'form':
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(FORM_ROW_SPACING)
    elif role == 'footer':
        layout.setContentsMargins(0, FOOTER_TOP_MARGIN, 0, 0)
        layout.setSpacing(SPACE_SM)
    elif role == 'brand':
        layout.setContentsMargins(SPACE_LG, SPACE_MD, SPACE_LG, SPACE_MD)
        layout.setSpacing(SPACE_SM)
    elif role == 'zero':
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


def configure_form_label(label):
    try:
        from qt.core import Qt
    except ImportError:
        from PyQt5.Qt import Qt
    label.setMinimumWidth(FORM_LABEL_MIN_WIDTH)
    label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)


def style_help_label(label):
    mid = label.palette().color(QPalette.ColorRole.PlaceholderText)
    if not mid.isValid():
        mid = label.palette().color(QPalette.ColorRole.Mid)
    label.setStyleSheet(
        'color: {color}; padding-top: {pt}px; padding-bottom: {pb}px;'.format(
            color=mid.name(),
            pt=SPACE_XS,
            pb=SPACE_XS,
        ))


def help_text_row(parent, label):
    '''Indent secondary help copy to align with radio/checkbox labels.'''
    row = QWidget(parent)
    row_layout = QHBoxLayout(row)
    configure_layout(row_layout, 'zero')
    row_layout.setContentsMargins(HELP_TEXT_INDENT, 0, 0, 0)
    row_layout.addWidget(label)
    return row


def load_brand_pixmap():
    try:
        data = get_resources(ICON_RESOURCE)  # noqa: F821 — injected by Calibre
    except Exception:
        return None
    if not data:
        return None
    pixmap = QPixmap()
    if not pixmap.loadFromData(data):
        return None
    try:
        from qt.core import Qt
    except ImportError:
        from PyQt5.Qt import Qt
    return pixmap.scaled(
        BRAND_ICON_PX, BRAND_ICON_PX, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def build_brand_header(title, subtitle):
    header = QWidget()
    header.setObjectName(BRAND_HEADER_ID)

    outer = QHBoxLayout(header)
    configure_layout(outer, 'brand')

    icon_label = QLabel()
    icon_label.setFixedSize(BRAND_ICON_PX, BRAND_ICON_PX)
    try:
        from qt.core import Qt
    except ImportError:
        from PyQt5.Qt import Qt
    icon_label.setAlignment(Qt.AlignCenter)
    pixmap = load_brand_pixmap()
    if pixmap is not None and not pixmap.isNull():
        icon_label.setPixmap(pixmap)
    else:
        icon_label.hide()
    outer.addWidget(icon_label)

    text_col = QVBoxLayout()
    configure_layout(text_col, 'zero')
    text_col.setSpacing(SPACE_XS)

    title_label = QLabel(title)
    title_label.setObjectName(BRAND_TITLE_ID)
    title_font = title_label.font()
    title_font.setBold(True)
    title_font.setPointSize(title_font.pointSize() + 1)
    title_label.setFont(title_font)
    text_col.addWidget(title_label)

    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName(BRAND_SUBTITLE_ID)
    subtitle_label.setWordWrap(True)
    text_col.addWidget(subtitle_label)

    outer.addLayout(text_col, stretch=1)
    return header, title_label, subtitle_label


def make_section_divider(parent=None):
    line = QFrame(parent)
    line.setObjectName(DIVIDER_ID)
    line.setFrameShape(QFrame.Shape.HLine if hasattr(QFrame, 'Shape') else QFrame.HLine)
    line.setFrameShadow(QFrame.Shadow.Plain if hasattr(QFrame, 'Shadow') else QFrame.Plain)
    line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    line.setFixedHeight(1)
    return line


def apply_dialog_stylesheet(widget):
    '''Theme-aware chrome: brand header, group titles, nested advanced section.'''
    highlight = widget.palette().color(QPalette.ColorRole.Highlight).name()
    alt_base = widget.palette().color(QPalette.ColorRole.AlternateBase).name()
    mid = widget.palette().color(QPalette.ColorRole.Mid).name()
    widget.setStyleSheet(
        '''
        QWidget#{header_id} {{
            background-color: {alt_base};
            border-radius: 6px;
            border-left: 3px solid {accent};
        }}
        QLabel#{title_id} {{
            background: transparent;
        }}
        QLabel#{subtitle_id} {{
            color: {mid};
            background: transparent;
        }}
        QFrame#{divider_id} {{
            color: {mid};
            background: {mid};
            max-height: 1px;
            margin-top: {space_sm}px;
            margin-bottom: {space_xs}px;
        }}
        QGroupBox {{
            font-weight: 600;
            margin-top: {group_top}px;
            padding-top: {group_pad}px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: {space_sm}px;
            padding: 0 {space_xs}px;
        }}
        QLabel#tradSimpSubheading {{
            color: palette(windowText);
            font-weight: 600;
            margin-top: {space_xs}px;
            margin-bottom: {space_xs}px;
        }}
        '''.format(
            header_id=BRAND_HEADER_ID,
            title_id=BRAND_TITLE_ID,
            subtitle_id=BRAND_SUBTITLE_ID,
            divider_id=DIVIDER_ID,
            accent=highlight,
            alt_base=alt_base,
            mid=mid,
            space_sm=SPACE_SM,
            space_md=SPACE_MD,
            space_xs=SPACE_XS,
            group_top=SPACE_LG,
            group_pad=SPACE_MD,
        ))


def style_subheading_label(label):
    label.setObjectName('tradSimpSubheading')


def build_section_group(parent, title):
    '''Create a group box with canonical section spacing.'''
    group_box = QGroupBox(title, parent)
    section_layout = QVBoxLayout()
    configure_layout(section_layout, 'section')
    group_box.setLayout(section_layout)
    return group_box, section_layout


def build_radio_group(parent, labels, ids=None):
    '''Create canonical radio-list layout and return (button_group, layout, buttons).'''
    button_group = QButtonGroup(parent)
    radio_layout = QVBoxLayout()
    configure_layout(radio_layout, 'radio')
    buttons = []
    for idx, label in enumerate(labels):
        button = QRadioButton(label)
        button_id = ids[idx] if ids is not None and idx < len(ids) else idx
        button_group.addButton(button, button_id)
        radio_layout.addWidget(button)
        buttons.append(button)
    return button_group, radio_layout, buttons


def polish_scroll_area(scroll_area):
    try:
        from qt.core import Qt
    except ImportError:
        from PyQt5.Qt import Qt
    scroll_area.setFrameShape(QFrame.Shape.NoFrame if hasattr(QFrame, 'Shape') else QFrame.NoFrame)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
