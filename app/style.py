class Style:
    BASE = """
    QWidget {
        font-family: "Segoe UI";
        font-size: 9pt;
        color: #E6E6E6;
    }
    QLabel#TitleLabel {
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    QLabel#StatusIndicator {
        padding: 0 6px;
    }
    QWidget#TitleBar {
        background: #1C1F26;
        border-bottom: 1px solid #2C313B;
    }
    QLabel#Preview {
        background: #0F1115;
        border: 1px solid #2C313B;
    }
    QToolButton {
        background: #232833;
        border: 1px solid #2C313B;
        padding: 2px 8px;
        border-radius: 4px;
    }
    QToolButton:hover {
        background: #2B3140;
    }
    QToolButton:pressed {
        background: #313849;
    }
    QPushButton#CancelButton {
        background: #2B3140;
        border: 1px solid #2C313B;
        padding: 4px 10px;
        border-radius: 4px;
    }
    QPushButton#CancelButton:hover {
        background: #343B4D;
    }
    QSlider::groove:horizontal {
        height: 4px;
        background: #2C313B;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        width: 10px;
        margin: -4px 0;
        background: #5ED5FF;
        border-radius: 5px;
    }
    """
