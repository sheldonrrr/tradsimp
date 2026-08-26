# -*- coding: utf-8 -*-

__license__ = 'GPL 3'

'''Shared spacing, typography, and branding for plugin dialogs.'''

try:
    from qt.core import (
        QAbstractButton, QApplication, QColor, QButtonGroup, QFont, QFrame, QGroupBox,
        QHBoxLayout, QIcon, QLabel, QLineF, QPalette, QPainter, QPen, QPixmap, QRadioButton,
        QRectF, QSize, QSizePolicy, QStyle, QStyleOption, QSyntaxHighlighter, QTextCharFormat,
        Qt, QTimer, QVBoxLayout, QWidget,
        pyqtSignal,
    )
except ImportError:
    from PyQt5.Qt import (
        QAbstractButton, QApplication, QColor, QButtonGroup, QFont, QFrame, QGroupBox,
        QHBoxLayout, QIcon, QLabel, QLineF, QPalette, QPainter, QPen, QPixmap, QRadioButton,
        QRectF, QSize, QSizePolicy, QStyle, QStyleOption, Qt, QTimer, QVBoxLayout, QWidget,
    )
    from PyQt5.QtCore import pyqtSignal
    from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat

ICON_RESOURCE = 'images/TradSimpIcon.png'
BRAND_ICON_PX = 40
ABOUT_ICON_PX = 64
TEXT_DIRECTION_ICON_PX = 24

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
TEXT_DIRECTION_ICON_TEXT_GAP = SPACE_SM

BRAND_HEADER_ID = 'tradSimpBrandHeader'
BRAND_TITLE_ID = 'tradSimpBrandTitle'
BRAND_SUBTITLE_ID = 'tradSimpBrandSubtitle'
DIVIDER_ID = 'tradSimpSectionDivider'
RECOMMEND_CARD_ID = 'tradSimpRecommendCard'
EXAMPLE_ZONE_ID = 'tradSimpExampleZone'
EXAMPLE_CARD_ID = 'tradSimpExampleCard'
EXAMPLE_TITLE_ID = 'tradSimpExampleTitle'
EXAMPLE_BODY_ID = 'tradSimpExampleBody'
EXAMPLE_SECONDARY_ID = 'tradSimpExampleSecondary'
TEXT_DIRECTION_TILE_ID = 'tradSimpTextDirTile'
TEXT_DIRECTION_TILE_PAD_Y = SPACE_LG
TEXT_DIRECTION_TILE_PAD_X = SPACE_MD


def _palette_role(role_name, fallback):
    roles = getattr(QPalette, 'ColorRole', QPalette)
    role = getattr(roles, role_name, None)
    if role is not None:
        return role
    return getattr(QPalette, fallback)


def _palette_color(palette, role_name, fallback_role, fallback_color):
    color = palette.color(_palette_role(role_name, fallback_role))
    if color.isValid():
        return color
    return QColor(*fallback_color)


def _muted_text_color(palette):
    '''Secondary copy color that stays readable in light and dark themes.

    Prefer PlaceholderText (meant for muted UI text). Mid is a bevel/border
    tone and often too dark against AlternateBase in dark themes.
    '''
    color = palette.color(_palette_role('PlaceholderText', 'PlaceholderText'))
    if color.isValid():
        return color
    return palette.color(_palette_role('Mid', 'Mid'))


def _is_dark_palette(palette):
    window = palette.color(_palette_role('Window', 'Window'))
    return window.isValid() and window.lightness() < 128


def _mix_colors(base, other, factor):
    return QColor(
        int(base.red() + (other.red() - base.red()) * factor),
        int(base.green() + (other.green() - base.green()) * factor),
        int(base.blue() + (other.blue() - base.blue()) * factor),
    )


def _checked_tile_fill(palette):
    '''Lifted panel so the selected card is clearly brighter than its neighbors.'''
    window = _palette_color(palette, 'Window', 'Window', (32, 32, 32))
    if _is_dark_palette(palette):
        return _mix_colors(window, QColor(255, 255, 255), 0.24)
    accent = _palette_color(palette, 'Highlight', 'Highlight', (40, 110, 220))
    panel = _palette_color(palette, 'AlternateBase', 'AlternateBase', (240, 240, 240))
    return _mix_colors(panel, accent, 0.22)


def _checked_tile_border(palette):
    '''High-contrast ring. macOS Highlight is often too close to the panel.'''
    window = _palette_color(palette, 'Window', 'Window', (32, 32, 32))
    text = _palette_color(palette, 'WindowText', 'WindowText', (230, 230, 230))
    if _is_dark_palette(palette):
        return _mix_colors(window, text, 0.82)
    accent = _palette_color(palette, 'Highlight', 'Highlight', (40, 110, 220))
    if accent.lightness() > 190:
        return _mix_colors(accent, text, 0.5)
    return accent


def _separator_color(palette):
    '''Border / divider color with enough contrast in dark themes.

    QPalette.Mid is correct for light chrome but often near-black in Calibre
    dark themes, so HLine and 1px borders vanish. Lift Mid toward WindowText
    when the window is dark and Mid is too close to the panel.
    '''
    mid = palette.color(_palette_role('Mid', 'Mid'))
    if not mid.isValid():
        mid = QColor(120, 120, 120)
    if not _is_dark_palette(palette):
        return mid
    window = palette.color(_palette_role('Window', 'Window'))
    # Already a clear step above the panel — keep theme Mid.
    if mid.lightness() >= window.lightness() + 45:
        return mid
    text = palette.color(_palette_role('WindowText', 'WindowText'))
    if not text.isValid():
        return QColor(150, 150, 150)
    # Blend ~40% toward text so the line reads as a separator, not a shadow.
    return _mix_colors(mid, text, 0.4)


def _qt_enum(owner, namespaced, legacy):
    group = getattr(owner, namespaced.split('.')[0], None) if '.' in namespaced else None
    if group is not None:
        value = getattr(group, namespaced.split('.')[-1], None)
        if value is not None:
            return value
    return getattr(owner, legacy)


def _text_direction_pen(color, width=None):
    if width is None:
        width = max(1.8, TEXT_DIRECTION_ICON_PX * 0.085)
    pen = QPen(color)
    pen.setWidthF(width)
    pen.setCapStyle(_qt_enum(Qt, 'PenCapStyle.RoundCap', 'RoundCap'))
    pen.setJoinStyle(_qt_enum(Qt, 'PenJoinStyle.RoundJoin', 'RoundJoin'))
    return pen


def _draw_bounding_box_circles(painter, size, color):
    '''Stroke-only frame: hollow corner rings, sides stopping at the rims.'''
    width = max(1.35, size * 0.058)
    radius = size * 0.16
    margin = radius + width * 0.5 + 1.1
    left = margin
    right = size - margin
    top = margin
    bottom = size - margin

    painter.setBrush(_qt_enum(Qt, 'BrushStyle.NoBrush', 'NoBrush'))
    line_pen = _text_direction_pen(color, width)
    line_pen.setCapStyle(_qt_enum(Qt, 'PenCapStyle.FlatCap', 'FlatCap'))
    painter.setPen(line_pen)
    painter.drawLine(QLineF(left + radius, top, right - radius, top))
    painter.drawLine(QLineF(right, top + radius, right, bottom - radius))
    painter.drawLine(QLineF(left + radius, bottom, right - radius, bottom))
    painter.drawLine(QLineF(left, top + radius, left, bottom - radius))

    painter.setPen(_text_direction_pen(color, width))
    diameter = radius * 2.0
    for cx, cy in ((left, top), (right, top), (left, bottom), (right, bottom)):
        painter.drawEllipse(QRectF(cx - radius, cy - radius, diameter, diameter))


def _draw_horizontal_text_lines(painter, size, color):
    painter.setPen(_text_direction_pen(color))
    pad = size * 0.16
    span = size - pad * 2.0
    widths = (1.0, 0.78, 0.52)
    for i, fraction in enumerate(widths):
        y = pad + span * (0.12 + i * 0.38)
        painter.drawLine(int(round(pad)), int(round(y)),
                         int(round(pad + span * fraction)), int(round(y)))


def _draw_vertical_text_lines(painter, size, color):
    '''Right-to-left columns of vertical strokes, like CJK vertical type.'''
    painter.setPen(_text_direction_pen(color))
    pad = size * 0.16
    span = size - pad * 2.0
    heights = (1.0, 0.78, 0.52)
    for i, fraction in enumerate(heights):
        x = size - pad - span * (0.12 + i * 0.38)
        painter.drawLine(int(round(x)), int(round(pad)),
                         int(round(x)), int(round(pad + span * fraction)))


def make_text_direction_icon(palette, kind='horizontal'):
    '''Theme-aware text-direction tile icon (unchanged / horizontal / vertical).'''
    logical = TEXT_DIRECTION_ICON_PX
    dpr = _device_pixel_ratio()
    phys = max(1, int(round(logical * dpr)))
    pixmap = QPixmap(phys, phys)
    pixmap.fill(Qt.GlobalColor.transparent if hasattr(Qt, 'GlobalColor') else Qt.transparent)

    text_color = _palette_color(palette, 'WindowText', 'WindowText', (80, 80, 80))
    painter = QPainter(pixmap)
    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing
        if hasattr(QPainter, 'RenderHint') else QPainter.Antialiasing)
    if dpr != 1.0:
        painter.scale(dpr, dpr)

    if kind == 'unchanged':
        _draw_bounding_box_circles(painter, logical, text_color)
    elif kind == 'vertical':
        _draw_vertical_text_lines(painter, logical, text_color)
    else:
        _draw_horizontal_text_lines(painter, logical, text_color)

    painter.end()
    try:
        pixmap.setDevicePixelRatio(dpr)
    except Exception:
        pass
    return QIcon(pixmap)


class TextDirectionTile(QAbstractButton):
    '''Card with a fixed 24px icon, explicit padding, and a label underneath.'''

    def __init__(self, label, parent=None):
        super(TextDirectionTile, self).__init__(parent)
        self.setObjectName(TEXT_DIRECTION_TILE_ID)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setAttribute(
            _qt_enum(Qt, 'WidgetAttribute.WA_StyledBackground', 'WA_StyledBackground'),
            True)
        self.setSizePolicy(
            _qt_enum(QSizePolicy, 'Policy.Expanding', 'Expanding'),
            _qt_enum(QSizePolicy, 'Policy.Preferred', 'Preferred'),
        )
        self.setMinimumHeight(
            TEXT_DIRECTION_ICON_PX + TEXT_DIRECTION_ICON_TEXT_GAP + 20
            + TEXT_DIRECTION_TILE_PAD_Y * 2)

        transparent = _qt_enum(Qt, 'WidgetAttribute.WA_TransparentForMouseEvents',
                               'WA_TransparentForMouseEvents')
        align_center = _qt_enum(Qt, 'AlignmentFlag.AlignCenter', 'AlignCenter')
        align_hcenter = _qt_enum(Qt, 'AlignmentFlag.AlignHCenter', 'AlignHCenter')

        self._icon_label = QLabel(self)
        self._icon_label.setFixedSize(TEXT_DIRECTION_ICON_PX, TEXT_DIRECTION_ICON_PX)
        self._icon_label.setAlignment(align_center)
        self._icon_label.setAttribute(transparent, True)

        self._text_label = QLabel(label, self)
        self._text_label.setAlignment(align_hcenter)
        self._text_label.setWordWrap(True)
        self._text_label.setAttribute(transparent, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            TEXT_DIRECTION_TILE_PAD_X,
            TEXT_DIRECTION_TILE_PAD_Y,
            TEXT_DIRECTION_TILE_PAD_X,
            TEXT_DIRECTION_TILE_PAD_Y,
        )
        layout.setSpacing(TEXT_DIRECTION_ICON_TEXT_GAP)
        layout.addWidget(self._icon_label, 0, align_hcenter)
        layout.addWidget(self._text_label, 0, align_hcenter)
        QAbstractButton.setText(self, label)
        self.toggled.connect(self._sync_checked_chrome)
        self._sync_checked_chrome(self.isChecked())

    def setText(self, text):
        self._text_label.setText(text)
        QAbstractButton.setText(self, text)

    def setIcon(self, icon):
        size = QSize(TEXT_DIRECTION_ICON_PX, TEXT_DIRECTION_ICON_PX)
        pixmap = icon.pixmap(size)
        self._icon_label.setPixmap(pixmap)

    def setIconSize(self, _size):
        self._icon_label.setFixedSize(TEXT_DIRECTION_ICON_PX, TEXT_DIRECTION_ICON_PX)

    def _sync_checked_chrome(self, checked):
        font = self._text_label.font()
        if checked:
            try:
                weight = _qt_enum(QFont, 'Weight.DemiBold', 'DemiBold')
            except AttributeError:
                weight = _qt_enum(QFont, 'Weight.Bold', 'Bold')
        else:
            weight = _qt_enum(QFont, 'Weight.Normal', 'Normal')
        font.setWeight(weight)
        self._text_label.setFont(font)
        self.setProperty('tileChecked', 'true' if checked else 'false')
        style = self.style()
        style.unpolish(self)
        style.polish(self)
        self.update()

    def paintEvent(self, event):
        option = QStyleOption()
        option.initFrom(self)
        state_on = _qt_enum(QStyle, 'StateFlag.State_On', 'State_On')
        if self.isChecked():
            option.state |= state_on
        painter = QPainter(self)
        try:
            self.style().drawPrimitive(
                _qt_enum(QStyle, 'PrimitiveElement.PE_Widget', 'PE_Widget'),
                option, painter, self)
        finally:
            painter.end()


def _text_direction_tile_stylesheet(palette):
    return (
        'QWidget#{tile_id} {{'
        ' background-color: {alt_base};'
        ' border: 2px solid transparent;'
        ' border-radius: 8px;'
        '}}'
        'QWidget#{tile_id}:hover:!checked {{'
        ' border-color: {muted_text};'
        '}}'
        'QWidget#{tile_id}:checked,'
        'QWidget#{tile_id}[tileChecked=\"true\"] {{'
        ' background-color: {tile_checked};'
        ' border: 2px solid {tile_checked_border};'
        '}}'
        'QWidget#{tile_id}:disabled {{'
        ' color: {muted_text};'
        '}}'
        'QWidget#{tile_id}:checked:disabled {{'
        ' border-color: {separator};'
        ' background-color: {alt_base};'
        '}}'
        'QWidget#{tile_id} QLabel {{'
        ' background: transparent;'
        ' border: none;'
        '}}'
    ).format(
        tile_id=TEXT_DIRECTION_TILE_ID,
        alt_base=palette.color(_palette_role('AlternateBase', 'AlternateBase')).name(),
        separator=_separator_color(palette).name(),
        muted_text=_muted_text_color(palette).name(),
        tile_checked=_checked_tile_fill(palette).name(),
        tile_checked_border=_checked_tile_border(palette).name(),
    )


def apply_text_direction_icons(no_change_button, horizontal_button, vertical_button):
    '''Attach keep-as-is, horizontal, and vertical icons to the three tiles.'''
    palette = no_change_button.palette()
    icon_size = QSize(TEXT_DIRECTION_ICON_PX, TEXT_DIRECTION_ICON_PX)
    sheet = _text_direction_tile_stylesheet(palette)
    for button, kind in (
        (no_change_button, 'unchanged'),
        (horizontal_button, 'horizontal'),
        (vertical_button, 'vertical'),
    ):
        button.setIcon(make_text_direction_icon(palette, kind))
        button.setIconSize(icon_size)
        button.setStyleSheet(sheet)


def build_text_direction_tiles(parent, labels, ids=None, tooltips=None):
    '''Three equal columns: custom cards with icon above label.'''
    button_group = QButtonGroup(parent)
    button_group.setExclusive(True)
    row = QHBoxLayout()
    configure_layout(row, 'radio')
    row.setSpacing(SPACE_SM)
    buttons = []
    for idx, label in enumerate(labels):
        button = TextDirectionTile(label, parent)
        if tooltips is not None and idx < len(tooltips) and tooltips[idx]:
            button.setToolTip(tooltips[idx])
        button_id = ids[idx] if ids is not None and idx < len(ids) else idx
        button_group.addButton(button, button_id)
        row.addWidget(button, 1)
        buttons.append(button)
    if len(buttons) >= 3:
        apply_text_direction_icons(buttons[0], buttons[1], buttons[2])
    return button_group, row, buttons


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


class CommentLineHighlighter(QSyntaxHighlighter):
    '''Render # lines in the dictionary editor as muted notes.'''

    def __init__(self, document, palette):
        super(CommentLineHighlighter, self).__init__(document)
        self._fmt = QTextCharFormat()
        self._fmt.setForeground(_muted_text_color(palette))

    def set_palette(self, palette):
        self._fmt.setForeground(_muted_text_color(palette))
        self.rehighlight()

    def highlightBlock(self, text):
        if (text or '').lstrip().startswith('#'):
            self.setFormat(0, len(text), self._fmt)


def attach_comment_line_highlighter(editor):
    highlighter = CommentLineHighlighter(editor.document(), editor.palette())
    editor._comment_line_highlighter = highlighter
    return highlighter


def style_help_label(label, enabled=True):
    muted = _muted_text_color(label.palette())
    alpha = 1.0 if enabled else 0.45
    label.setStyleSheet(
        'color: rgba({r}, {g}, {b}, {a});'
        ' padding-top: {pt}px; padding-bottom: {pb}px;'.format(
            r=muted.red(),
            g=muted.green(),
            b=muted.blue(),
            a=alpha,
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


def _device_pixel_ratio():
    try:
        app = QApplication.instance()
        if app is not None:
            return max(1.0, float(app.devicePixelRatio()))
    except Exception:
        pass
    return 1.0


def load_brand_pixmap(size=None):
    try:
        data = get_resources(ICON_RESOURCE)  # noqa: F821 — injected by Calibre
    except Exception:
        return None
    if not data:
        return None
    pixmap = QPixmap()
    if not pixmap.loadFromData(data):
        return None
    px = int(size or BRAND_ICON_PX)
    dpr = _device_pixel_ratio()
    phys = max(1, int(round(px * dpr)))
    scaled = pixmap.scaled(
        phys, phys, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    try:
        scaled.setDevicePixelRatio(dpr)
    except Exception:
        pass
    return scaled


def make_about_icon_label():
    '''Large centered plugin icon for the About dialog (macOS-style).'''
    label = QLabel()
    label.setFixedSize(ABOUT_ICON_PX, ABOUT_ICON_PX)
    label.setAlignment(Qt.AlignCenter)
    pixmap = load_brand_pixmap(ABOUT_ICON_PX)
    if pixmap is not None and not pixmap.isNull():
        label.setPixmap(pixmap)
    else:
        label.hide()
    return label


def build_about_identity():
    '''Centered icon + name + version block for the About dialog.'''
    header = QWidget()
    header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    layout = QVBoxLayout(header)
    layout.setContentsMargins(0, SPACE_SM, 0, SPACE_SM)
    layout.setSpacing(SPACE_XS)

    icon_label = make_about_icon_label()
    layout.addWidget(icon_label, 0, Qt.AlignHCenter)
    layout.addSpacing(SPACE_LG)

    title_label = QLabel()
    title_label.setObjectName(BRAND_TITLE_ID)
    title_label.setAlignment(Qt.AlignHCenter)
    title_label.setWordWrap(False)
    title_font = title_label.font()
    title_font.setBold(True)
    title_font.setPointSize(title_font.pointSize() + 1)
    title_label.setFont(title_font)
    layout.addWidget(title_label)

    version_label = QLabel()
    version_label.setObjectName(BRAND_SUBTITLE_ID)
    version_label.setAlignment(Qt.AlignHCenter)
    layout.addWidget(version_label)
    return header, title_label, version_label


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
    palette = widget.palette()
    highlight = palette.color(QPalette.ColorRole.Highlight).name()
    alt_base = palette.color(QPalette.ColorRole.AlternateBase).name()
    base = palette.color(QPalette.ColorRole.Base).name()
    # Borders / dividers: Mid in light themes; lifted Mid in dark themes.
    separator = _separator_color(palette).name()
    # Muted labels (brand subtitle, example titles): PlaceholderText, not Mid.
    muted_text = _muted_text_color(palette).name()
    tile_checked = _checked_tile_fill(palette).name()
    tile_checked_border = _checked_tile_border(palette).name()
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
            color: {muted_text};
            background: transparent;
        }}
        QFrame#{divider_id} {{
            color: {separator};
            background: {separator};
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
        QLabel#tradSimpSubheadingBreak {{
            color: palette(windowText);
            font-weight: 600;
            margin-top: {space_lg}px;
            margin-bottom: {space_xs}px;
            padding-top: {space_md}px;
            border-top: 1px solid {separator};
        }}
        QWidget#{example_zone_id} {{
            background: transparent;
            margin-top: {space_xs}px;
            margin-bottom: {space_sm}px;
        }}
        QWidget#{example_card_id} {{
            background-color: {alt_base};
            border: 1px solid {separator};
            border-radius: 8px;
        }}
        QWidget#{example_card_id}[interactive=\"true\"] {{
            border: 1px solid {accent};
        }}
        QWidget#{example_card_id}[flash=\"true\"] {{
            border: 2px solid {accent};
            background-color: {base};
        }}
        QWidget#{example_card_id} QLabel {{
            background: transparent;
        }}
        QLabel#{example_title_id} {{
            color: {muted_text};
            font-size: 11px;
        }}
        QLabel#{example_secondary_id} {{
            color: {muted_text};
        }}
        QWidget#{tile_id} {{
            background-color: {alt_base};
            border: 2px solid transparent;
            border-radius: 8px;
        }}
        QWidget#{tile_id}:hover:!checked {{
            border-color: {muted_text};
        }}
        QWidget#{tile_id}:checked,
        QWidget#{tile_id}[tileChecked=\"true\"] {{
            background-color: {tile_checked};
            border: 2px solid {tile_checked_border};
        }}
        QWidget#{tile_id}:disabled {{
            color: {muted_text};
        }}
        QWidget#{tile_id}:checked:disabled {{
            border-color: {separator};
            background-color: {alt_base};
        }}
        QWidget#{tile_id} QLabel {{
            background: transparent;
            border: none;
        }}
        '''.format(
            header_id=BRAND_HEADER_ID,
            title_id=BRAND_TITLE_ID,
            subtitle_id=BRAND_SUBTITLE_ID,
            divider_id=DIVIDER_ID,
            example_zone_id=EXAMPLE_ZONE_ID,
            example_card_id=EXAMPLE_CARD_ID,
            example_title_id=EXAMPLE_TITLE_ID,
            example_secondary_id=EXAMPLE_SECONDARY_ID,
            tile_id=TEXT_DIRECTION_TILE_ID,
            tile_pad_y=TEXT_DIRECTION_TILE_PAD_Y,
            tile_pad_x=TEXT_DIRECTION_TILE_PAD_X,
            tile_checked=tile_checked,
            tile_checked_border=tile_checked_border,
            accent=highlight,
            alt_base=alt_base,
            base=base,
            separator=separator,
            muted_text=muted_text,
            space_sm=SPACE_SM,
            space_md=SPACE_MD,
            space_lg=SPACE_LG,
            space_xs=SPACE_XS,
            group_top=SPACE_LG,
            group_pad=SPACE_MD,
        ))


def style_subheading_label(label, section_break=False):
    '''Mark a nested advanced-options heading; section_break adds a clearer gap.'''
    label.setObjectName(
        'tradSimpSubheadingBreak' if section_break else 'tradSimpSubheading')


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


def style_recommend_card(card):
    '''Theme-aware background for plugin recommendation cards in About dialog.'''
    card.setObjectName(RECOMMEND_CARD_ID)
    palette = card.palette()
    alt_base = palette.color(QPalette.ColorRole.AlternateBase).name()
    separator = _separator_color(palette).name()
    card.setStyleSheet(
        'QWidget#{card_id} {{'
        ' background-color: {alt_base};'
        ' border: 1px solid {separator};'
        ' border-radius: 8px;'
        '}}'
        'QWidget#{card_id} QLabel {{ background: transparent; }}'.format(
            card_id=RECOMMEND_CARD_ID,
            alt_base=alt_base,
            separator=separator,
        ))


class ExamplePreviewCard(QWidget):
    '''Dedicated preview zone for plain-text / code / bilingual samples.'''

    clicked = pyqtSignal()

    def __init__(self, parent=None, title='', interactive=False):
        super(ExamplePreviewCard, self).__init__(parent)
        self.setObjectName(EXAMPLE_CARD_ID)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self._interactive = False
        self._flash_timer = QTimer(self)
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(self._clear_flash)

        outer = QVBoxLayout(self)
        configure_layout(outer, 'zero')
        outer.setContentsMargins(SPACE_MD, SPACE_SM, SPACE_MD, SPACE_SM)
        outer.setSpacing(SPACE_XS)

        self.title_label = QLabel(title)
        self.title_label.setObjectName(EXAMPLE_TITLE_ID)
        outer.addWidget(self.title_label)

        self.body_label = QLabel()
        self.body_label.setObjectName(EXAMPLE_BODY_ID)
        self.body_label.setWordWrap(True)
        outer.addWidget(self.body_label)

        self.secondary_label = QLabel()
        self.secondary_label.setObjectName(EXAMPLE_SECONDARY_ID)
        self.secondary_label.setWordWrap(True)
        secondary_font = self.secondary_label.font()
        if secondary_font.pointSize() > 0:
            secondary_font.setPointSize(max(9, secondary_font.pointSize() - 1))
        self.secondary_label.setFont(secondary_font)
        self.secondary_label.hide()
        outer.addWidget(self.secondary_label)

        self._plain_font = self.body_label.font()
        self._code_font = self.body_label.font()
        self._code_font.setFamily('Menlo')
        self.set_interactive(interactive)

    def set_interactive(self, interactive):
        self._interactive = bool(interactive)
        self.setProperty('interactive', 'true' if self._interactive else 'false')
        if self._interactive:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.unsetCursor()
        self.style().unpolish(self)
        self.style().polish(self)

    def set_title(self, title):
        self.title_label.setText(title or '')
        self.title_label.setVisible(bool(title))

    def set_plain_example(self, text, flash=False):
        changed = self.body_label.text() != (text or '')
        self.body_label.setFont(self._plain_font)
        self.body_label.setText(text or '')
        self.secondary_label.hide()
        self.secondary_label.clear()
        if flash and changed:
            self.flash()

    def set_code_example(self, text, flash=False):
        changed = self.body_label.text() != (text or '')
        self.body_label.setFont(self._code_font)
        self.body_label.setText(text or '')
        self.secondary_label.hide()
        self.secondary_label.clear()
        if flash and changed:
            self.flash()

    def set_bilingual_example(self, primary, secondary, flash=False):
        changed = (
            self.body_label.text() != (primary or '')
            or self.secondary_label.text() != (secondary or ''))
        self.body_label.setFont(self._plain_font)
        self.body_label.setText(primary or '')
        if secondary:
            self.secondary_label.setText(secondary)
            self.secondary_label.show()
        else:
            self.secondary_label.hide()
            self.secondary_label.clear()
        if flash and changed:
            self.flash()

    def flash(self):
        self.setProperty('flash', 'true')
        self.style().unpolish(self)
        self.style().polish(self)
        self._flash_timer.start(220)

    def _clear_flash(self):
        self.setProperty('flash', 'false')
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if self._interactive and event.button() == Qt.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super(ExamplePreviewCard, self).mousePressEvent(event)


def build_example_preview_card(parent=None, title='', interactive=False):
    '''Create a dedicated example zone placed above feature controls.'''
    zone = QWidget(parent)
    zone.setObjectName(EXAMPLE_ZONE_ID)
    zone.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
    zone_layout = QVBoxLayout(zone)
    configure_layout(zone_layout, 'zero')
    zone_layout.setContentsMargins(0, 0, 0, 0)
    card = ExamplePreviewCard(zone, title=title, interactive=interactive)
    zone_layout.addWidget(card)
    return zone, card
