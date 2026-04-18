COMMERCIAL_THEME_QSS = """
QMainWindow, QWidget {
    background-color: #0D0D11;
    color: #E2E2E2;
    font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
QGroupBox {
    background-color: #141419;
    border: 1px solid #23232C;
    border-radius: 8px;
    margin-top: 24px;
    padding: 16px;
    font-size: 13px;
    font-weight: 500;
    color: #A0A0A5;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    color: #8C8C91;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
QLabel {
    color: #E2E2E2;
    background: transparent;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #23232C;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: #6A6A75;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #E2E2E2;
    border: 2px solid #0D0D11;
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #FFFFFF;
    border-color: #23232C;
}
QTextEdit {
    background-color: #0A0A0E;
    color: #A0A0A5;
    border: 1px solid #1E1E26;
    border-radius: 6px;
    font-family: "SF Mono", "Consolas", monospace;
    font-size: 12px;
    padding: 12px;
    line-height: 1.5;
}
QPushButton {
    background-color: #1E1E26;
    color: #E2E2E2;
    border: 1px solid #2C2C35;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.5px;
}
QPushButton:hover {
    background-color: #2C2C35;
    border-color: #3A3A45;
}
QPushButton:pressed {
    background-color: #141419;
}
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #23232C;
}
"""
