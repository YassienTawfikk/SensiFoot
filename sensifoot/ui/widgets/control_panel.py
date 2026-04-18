from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

class MasterControlWidget(QGroupBox):
    # Emits (value) when the master slider moves
    valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__("Sensor Telemetry Override", parent)
        self.active_sensor_name = "Sensor 0 (Heel)"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(12, 20, 12, 12)

        self.sensor_lbl = QLabel(f"Active Link: {self.active_sensor_name}")
        self.sensor_lbl.setStyleSheet("color: #00AAFF; font-size: 13px; font-weight: bold;")

        self.master_slider = QSlider(Qt.Horizontal)
        self.master_slider.setRange(0, 255)
        self.master_slider.setValue(128)

        self.label_val = QLabel("128")
        self.label_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_val.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px;")

        slider_row = QHBoxLayout()
        slider_row.addWidget(self.master_slider, stretch=1)
        slider_row.addWidget(self.label_val)

        inst_lbl = QLabel("Select an anatomical node on the wireframe to bind.")
        inst_lbl.setStyleSheet("color: #6A6A75; font-size: 11px;")
        inst_lbl.setWordWrap(True)

        layout.addWidget(self.sensor_lbl)
        layout.addLayout(slider_row)
        layout.addWidget(inst_lbl)
        layout.addStretch()

        self.master_slider.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self):
        val = self.master_slider.value()
        self.label_val.setText(str(val))
        self.valueChanged.emit(val)

    def set_active_sensor(self, name: str, current_value: int):
        self.active_sensor_name = name
        self.sensor_lbl.setText(f"Active Link: {self.active_sensor_name}")
        # Block signals so setting value programmatically doesn't emit feedback loop
        self.master_slider.blockSignals(True)
        self.master_slider.setValue(current_value)
        self.label_val.setText(str(current_value))
        self.master_slider.blockSignals(False)
