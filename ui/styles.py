"""
Application stylesheet - Modern dark mode theme with gradient accents.
"""

DARK_STYLESHEET = """
/* ============================================= */
/*  GLOBAL                                       */
/* ============================================= */
* {
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

QMainWindow {
    background-color: #0f0f14;
}

QWidget {
    background-color: transparent;
    color: #e0e0e8;
    font-size: 13px;
}

/* ============================================= */
/*  TAB WIDGET                                   */
/* ============================================= */
QTabWidget::pane {
    border: 1px solid #2a2a3a;
    border-radius: 8px;
    background-color: #16161e;
    top: -1px;
}

QTabBar::tab {
    background-color: #1a1a26;
    color: #8888a0;
    border: 1px solid #2a2a3a;
    border-bottom: none;
    padding: 10px 28px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #16161e;
    color: #a78bfa;
    border-bottom: 2px solid #a78bfa;
}

QTabBar::tab:hover:!selected {
    background-color: #20202e;
    color: #c0c0d0;
}

/* ============================================= */
/*  BUTTONS                                      */
/* ============================================= */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a78bfa);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c6cf7, stop:1 #b79bff);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5c4cd7, stop:1 #977bea);
}

QPushButton:disabled {
    background-color: #2a2a3a;
    color: #555566;
}

QPushButton#btnSecondary {
    background: transparent;
    border: 1px solid #3a3a5a;
    color: #a0a0b8;
}

QPushButton#btnSecondary:hover {
    background-color: #22223a;
    border-color: #6c5ce7;
    color: #c0c0d8;
}

QPushButton#btnDanger {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #e74c3c, stop:1 #e67e22);
}

QPushButton#btnDanger:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f75c4c, stop:1 #f68e32);
}

QPushButton#btnSuccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00b894, stop:1 #00cec9);
}

QPushButton#btnSuccess:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #10c8a4, stop:1 #10ded9);
}

/* ============================================= */
/*  COMBOBOX                                     */
/* ============================================= */
QComboBox {
    background-color: #1e1e2e;
    color: #e0e0e8;
    border: 1px solid #3a3a5a;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #6c5ce7;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #a78bfa;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e2e;
    color: #e0e0e8;
    border: 1px solid #3a3a5a;
    border-radius: 4px;
    selection-background-color: #6c5ce7;
    selection-color: #ffffff;
    padding: 4px;
}

/* ============================================= */
/*  PROGRESS BAR                                 */
/* ============================================= */
QProgressBar {
    background-color: #1a1a2e;
    border: 1px solid #2a2a3a;
    border-radius: 10px;
    text-align: center;
    color: #e0e0e8;
    font-weight: 600;
    font-size: 12px;
    min-height: 22px;
    max-height: 22px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:0.5 #a78bfa, stop:1 #00cec9);
    border-radius: 9px;
}

/* ============================================= */
/*  LABELS                                       */
/* ============================================= */
QLabel {
    color: #c0c0d0;
    font-size: 13px;
}

QLabel#titleLabel {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#subtitleLabel {
    font-size: 14px;
    color: #8888a0;
    font-weight: 400;
}

QLabel#sectionLabel {
    font-size: 15px;
    font-weight: 600;
    color: #a78bfa;
}

QLabel#infoLabel {
    font-size: 12px;
    color: #6a6a80;
}

QLabel#statusSuccess {
    color: #00b894;
    font-weight: 600;
}

QLabel#statusError {
    color: #e74c3c;
    font-weight: 600;
}

/* ============================================= */
/*  GROUP BOX                                    */
/* ============================================= */
QGroupBox {
    background-color: #16161e;
    border: 1px solid #2a2a3a;
    border-radius: 10px;
    margin-top: 16px;
    padding: 20px 16px 16px 16px;
    font-weight: 600;
    font-size: 14px;
    color: #a78bfa;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background-color: #1e1e2e;
    border: 1px solid #2a2a3a;
    border-radius: 6px;
    left: 12px;
}

/* ============================================= */
/*  TABLE WIDGET                                 */
/* ============================================= */
QTableWidget {
    background-color: #12121a;
    alternate-background-color: #16161e;
    border: 1px solid #2a2a3a;
    border-radius: 8px;
    gridline-color: #22223a;
    selection-background-color: #2a2a5a;
    selection-color: #ffffff;
    font-size: 12px;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #1e1e2e;
}

QHeaderView::section {
    background-color: #1a1a2e;
    color: #a78bfa;
    border: none;
    border-bottom: 2px solid #6c5ce7;
    padding: 8px 12px;
    font-weight: 600;
    font-size: 12px;
}

/* ============================================= */
/*  SCROLL BAR                                   */
/* ============================================= */
QScrollBar:vertical {
    background-color: #12121a;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #3a3a5a;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #6c5ce7;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #12121a;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #3a3a5a;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #6c5ce7;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ============================================= */
/*  TEXT EDIT / LOG                               */
/* ============================================= */
QTextEdit, QPlainTextEdit {
    background-color: #0d0d14;
    color: #b0b0c0;
    border: 1px solid #2a2a3a;
    border-radius: 8px;
    padding: 10px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
    selection-background-color: #3a3a6a;
}

/* ============================================= */
/*  SPLITTER                                     */
/* ============================================= */
QSplitter::handle {
    background-color: #2a2a3a;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* ============================================= */
/*  TOOLTIP                                      */
/* ============================================= */
QToolTip {
    background-color: #1e1e2e;
    color: #e0e0e8;
    border: 1px solid #3a3a5a;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ============================================= */
/*  LINE EDIT                                    */
/* ============================================= */
QLineEdit {
    background-color: #1e1e2e;
    color: #e0e0e8;
    border: 1px solid #3a3a5a;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    selection-background-color: #6c5ce7;
}

QLineEdit:focus {
    border-color: #6c5ce7;
}

/* ============================================= */
/*  SLIDER                                       */
/* ============================================= */
QSlider::groove:horizontal {
    background-color: #1a1a2e;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #6c5ce7, stop:1 #a78bfa);
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a78bfa);
    border-radius: 3px;
}
"""
