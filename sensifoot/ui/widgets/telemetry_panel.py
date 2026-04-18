from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QTextEdit, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class TelemetryPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        diag_group = QGroupBox("Algorithmic Diagnostic Engine")
        diag_layout = QVBoxLayout(diag_group)
        diag_layout.setSpacing(12)

        self.label_diagnostic = QLabel("AWAITING\nINPUT")
        self.label_diagnostic.setAlignment(Qt.AlignCenter)
        diag_font = QFont()
        diag_font.setPointSize(28)
        diag_font.setBold(True)
        self.label_diagnostic.setFont(diag_font)
        self.label_diagnostic.setWordWrap(True)
        self.label_diagnostic.setStyleSheet("color: #555555;")
        self.label_diagnostic.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )

        diag_layout.addStretch()
        diag_layout.addWidget(self.label_diagnostic)
        diag_layout.addStretch()

        telem_lbl = QLabel("Algorithm Metrics Array")
        telem_lbl.setStyleSheet("color: #555555; font-size: 11px;")
        diag_layout.addWidget(telem_lbl)

        self.text_telemetry = QTextEdit()
        self.text_telemetry.setReadOnly(True)
        self.text_telemetry.setFixedHeight(200)
        self.text_telemetry.setPlainText("Processing values...")
        diag_layout.addWidget(self.text_telemetry)

        layout.addWidget(diag_group)

    def update_diagnostics(self, label_text: str, desc: str, color: str, confidences: list, descriptions: list, class_id: int):
        self.label_diagnostic.setText(
            f"{label_text}\n{desc}\nAlgorithmic State"
        )
        self.label_diagnostic.setStyleSheet(
            f"color: {color}; font-size: 28pt; font-weight: bold;"
        )

        lines = [
            f"  Class {i}: {confidences[i] * 100:5.1f}%  {descriptions[i]}"
            for i in range(len(descriptions))
        ]
        lines[class_id] = ">" + lines[class_id].lstrip()
        self.text_telemetry.setPlainText("\n".join(lines))
