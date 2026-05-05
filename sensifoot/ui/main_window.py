import os
import time
import queue
import datetime
import pyttsx3
from fpdf import FPDF
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QFrame, QDialog, QMessageBox, QCheckBox, QDoubleSpinBox
from PyQt5.QtCore import Qt, QThread

from sensifoot.core.state import SensorState
from sensifoot.core.clinical import calculate_gait_phase, check_ulcer_risk
from sensifoot.ui.widgets.foot_widget import FootAssetWidget
from sensifoot.core.cleanup import perform_cleanup

class VoiceCoachThread(QThread):
    def __init__(self):
        super().__init__()
        self.message_queue = queue.Queue()
        self.running = True

    def run(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        while self.running:
            try:
                msg = self.message_queue.get(timeout=0.5)
                if msg:
                    engine.say(msg)
                    engine.runAndWait()
            except queue.Empty:
                pass

    def speak(self, text):
        self.message_queue.put(text)

    def stop(self):
        self.running = False
        self.wait()

class CorrectionDialog(QDialog):
    def __init__(self, zone_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Posture Realignment Required")
        self.setMinimumWidth(400)
        self.setStyleSheet("QDialog { background: #141419; }")
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Posture Realignment Required")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF3333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        instructions = {
            0: "Weight is too heavy on the heel. Lean your torso slightly forward and engage your core.",
            1: "Ankle is rolling. Focus on pushing down evenly through both the inside and outside of your foot.",
            2: "Over-reliance on the front of the foot. Lower your heel and distribute your weight evenly across the sole.",
            3: "Over-reliance on the front of the foot. Lower your heel and distribute your weight evenly across the sole.",
            4: "Over-reliance on the front of the foot. Lower your heel and distribute your weight evenly across the sole.",
            5: "Excessive pressure on the big toe. Shift your weight slightly back toward the center of your foot."
        }
        
        instruction_text = instructions.get(zone_id, "Adjust your posture.")
        
        self.lbl_instruction = QLabel(instruction_text)
        self.lbl_instruction.setWordWrap(True)
        self.lbl_instruction.setStyleSheet("font-size: 14px; color: #E2E2E2;")
        self.lbl_instruction.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_instruction)
        
        layout.addSpacing(20)
        
        btn_dismiss = QPushButton("Dismiss / Return to Simulation")
        btn_dismiss.setCursor(Qt.PointingHandCursor)
        btn_dismiss.setStyleSheet(
            "QPushButton { background: #1E1E26; color: #E2E2E2; border-radius: 6px;"
            " padding: 8px; border: 1px solid #2C2C35; font-size: 13px; }"
            "QPushButton:hover { background: #2A2A35; border-color: #3A3A45; }"
        )
        btn_dismiss.clicked.connect(self.accept)
        layout.addWidget(btn_dismiss, alignment=Qt.AlignCenter)

class TelemetryLabelBlock(QWidget):
    """Encapsulated UI component for a high-fidelity telemetry block mapping with Gestalt tight-grouping."""
    def __init__(self, title: str, is_hero: bool = False, align_right: bool = False):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2) 
        
        self.title_lbl = QLabel(title)
        self.val_lbl = QLabel("--")
        
        align = Qt.AlignRight if align_right else Qt.AlignLeft
        self.title_lbl.setAlignment(align | Qt.AlignVCenter)
        self.val_lbl.setAlignment(align | Qt.AlignVCenter)
        
        base_style = "border: none; background: transparent; "
        
        if is_hero:
            self.title_lbl.setStyleSheet(base_style + "color: #9A9AA5; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
            self.val_lbl.setStyleSheet(base_style + "color: #00FFB3; font-weight: bold; font-size: 28px; font-family: 'Courier New', monospace;")
            self.setMinimumWidth(180)
        else:
            self.title_lbl.setStyleSheet(base_style + "color: #6A6A75; font-weight: normal; font-size: 11px;")
            self.val_lbl.setStyleSheet(base_style + "color: #B0B0B5; font-weight: bold; font-size: 17px; font-family: 'Courier New', monospace;")
            self.setMinimumWidth(130)

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.val_lbl)

    def set_value(self, val_str: str):
        self.val_lbl.setText(val_str)


class SensiFootApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SensiFoot System - FSR Physics Simulation")
        self.setMinimumSize(950, 850)

        self.state_manager = SensorState()
        self._scenario_state = 0
        self.sensor_names = {
            0: "Heel (Zone 0)",
            1: "Midfoot Lateral (Zone 1)",
            2: "Metatarsal I (Zone 2)",
            3: "Metatarsal III (Zone 3)",
            4: "Metatarsal V (Zone 4)",
            5: "Hallux (Zone 5)"
        }

        self.voice_coach_thread = VoiceCoachThread()
        self.voice_coach_thread.start()
        self.last_speech_time = 0

        self._build_ui()
        self._sync_ui_state()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        header_text = '<span style="font-weight: bold; font-size: 18px; color: #E2E2E2;">Sensifoot™</span> <span style="font-weight: 300; font-size: 16px; color: #7A7A85;"> | FSR Clinical Array</span>'
        header = QLabel(header_text)
        
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setFixedWidth(100)
        self.btn_exit.setCursor(Qt.PointingHandCursor)
        self.btn_exit.clicked.connect(self.close)

        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_exit)
        root.addLayout(header_layout)

        # Output A: Top HUD
        self.label_gait_phase = QLabel("Current Phase: TRANSITIONAL / STATIC")
        self.label_gait_phase.setAlignment(Qt.AlignCenter)
        self.label_gait_phase.setStyleSheet(
            "color: #E2E2E2; font-size: 24px; font-weight: bold;"
            "background: #1E1E26; border-radius: 8px; padding: 16px; border: 1px solid #2C2C35;"
        )
        root.addWidget(self.label_gait_phase)

        # Output C: Alert Container — fixed height horizontal layout
        self.alert_container = QWidget()
        self.alert_container.setFixedHeight(60)
        self.alert_container.setVisible(False)
        alert_layout = QHBoxLayout(self.alert_container)
        alert_layout.setContentsMargins(0, 0, 0, 0)
        alert_layout.setSpacing(20)

        self.label_alert = QLabel("")
        self.label_alert.setAlignment(Qt.AlignCenter | Qt.AlignLeft)
        self.label_alert.setStyleSheet(
            "color: #FF3333; font-size: 16px; font-weight: bold;"
            " background: #2A0A0A; padding: 8px; border-radius: 4px;"
        )
        
        self.btn_correction = QPushButton("View Correction Instructions")
        self.btn_correction.setFixedWidth(250)
        self.btn_correction.setCursor(Qt.PointingHandCursor)
        self.btn_correction.setStyleSheet(
            "QPushButton { background: #FF3333; color: white; border-radius: 6px;"
            " padding: 8px; font-weight: bold; font-size: 14px; border: none; }"
            "QPushButton:hover { background: #CC0000; }"
        )
        self.btn_correction.clicked.connect(self._show_correction_dialog)
        
        alert_layout.addWidget(self.label_alert, stretch=1)
        alert_layout.addWidget(self.btn_correction)
        
        root.addWidget(self.alert_container)

        # Central Asset + Right-Edge Action Menu
        _ACTION_W = 200  # 180px buttons + 12px left gap + 8px buffer

        _btn_style = (
            "QPushButton { background: #1E1E26; color: #E2E2E2; border-radius: 6px;"
            " padding: 8px; border: 1px solid #2C2C35; font-size: 13px; }"
            "QPushButton:hover { background: #2A2A35; border-color: #3A3A45; }"
            "QPushButton:pressed { background: #141419; }"
        )

        self.btn_scenario = QPushButton("Scenario: Manual")
        self.btn_clear = QPushButton("Clear Array")
        self.btn_toggle_sensors = QPushButton("Show Sensors")
        
        self.btn_report = QPushButton("Generate Patient Report")

        for _btn in (self.btn_scenario, self.btn_clear, self.btn_toggle_sensors, self.btn_report):
            _btn.setStyleSheet(_btn_style)
            _btn.setCursor(Qt.PointingHandCursor)
            _btn.setFixedWidth(180)
            _btn.setMinimumHeight(36)

        self.btn_scenario.clicked.connect(self._on_scenario_clicked)
        self.btn_clear.clicked.connect(self._on_clear_clicked)
        self.btn_toggle_sensors.clicked.connect(self._on_toggle_sensors_clicked)
        self.btn_report.clicked.connect(self._on_generate_report_clicked)

        self.asset_widget = FootAssetWidget()
        self.asset_widget.sensorClicked.connect(self._on_sensor_clicked)

        # Left Panel (Patient Profile)
        _left_panel = QWidget()
        _left_panel.setFixedWidth(_ACTION_W)
        _left_inner = QVBoxLayout(_left_panel)
        _left_inner.setContentsMargins(0, 0, 12, 0)
        _left_inner.setSpacing(15)
        _left_inner.addStretch(1)
        
        lbl_profile = QLabel("Patient Profile")
        lbl_profile.setStyleSheet("color: #9A9AA5; font-weight: bold; font-size: 14px; letter-spacing: 1px;")
        _left_inner.addWidget(lbl_profile)
        
        lbl_weight = QLabel("Patient Weight (kg):")
        lbl_weight.setStyleSheet("color: #E2E2E2; font-size: 13px;")
        _left_inner.addWidget(lbl_weight)
        
        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(20.0, 200.0)
        self.spin_weight.setValue(70.0)
        self.spin_weight.setSingleStep(1.0)
        self.spin_weight.setStyleSheet(
            "QDoubleSpinBox { background: #1E1E26; color: #E2E2E2; border-radius: 6px;"
            " padding: 8px; border: 1px solid #2C2C35; font-size: 14px; }"
        )
        self.spin_weight.valueChanged.connect(self._on_weight_changed)
        _left_inner.addWidget(self.spin_weight)
        _left_inner.addStretch(2)

        # Right action panel: fixed width, buttons vertically centred
        _action_panel = QWidget()
        _action_panel.setFixedWidth(_ACTION_W)
        _action_inner = QVBoxLayout(_action_panel)
        _action_inner.setContentsMargins(12, 0, 0, 0)
        _action_inner.setSpacing(15)
        _action_inner.addStretch(1)
        _action_inner.addWidget(self.btn_scenario)
        _action_inner.addWidget(self.btn_clear)
        _action_inner.addWidget(self.btn_toggle_sensors)
        _action_inner.addWidget(self.btn_report)
        
        self.cb_voice_coach = QCheckBox("Voice Coach: OFF")
        self.cb_voice_coach.setChecked(False)
        self.cb_voice_coach.setStyleSheet("color: #E2E2E2; font-size: 13px; font-weight: bold; margin-top: 10px;")
        self.cb_voice_coach.setCursor(Qt.PointingHandCursor)
        self.cb_voice_coach.stateChanged.connect(self._on_voice_coach_toggled)
        _action_inner.addWidget(self.cb_voice_coach)
        
        _action_inner.addStretch(2)

        asset_container = QWidget()
        asset_layout = QHBoxLayout(asset_container)
        asset_layout.setContentsMargins(0, 0, 0, 0)
        asset_layout.setSpacing(0)
        asset_layout.addWidget(_left_panel)
        asset_layout.addWidget(self.asset_widget, stretch=1, alignment=Qt.AlignCenter)
        asset_layout.addWidget(_action_panel)

        root.addWidget(asset_container, stretch=1)

        # -----------------------------
        # Physical Telemetry HUD Module
        # -----------------------------
        self.control_panel = QFrame()
        self.control_panel.setObjectName("MasterControlPanel")
        self.control_panel.setStyleSheet("#MasterControlPanel { background: #141419; border-radius: 8px; border: 1px solid #23232C; }")

        control_layout = QVBoxLayout(self.control_panel)
        control_layout.setContentsMargins(20, 15, 25, 20)
        control_layout.setSpacing(12)

        # Slider Row
        slider_row = QHBoxLayout()
        self.label_active_sensor = QLabel("No Zone Selected")
        self.label_active_sensor.setStyleSheet("border: none; background: transparent; color: #6A6A75; font-weight: normal; font-size: 14px;")
        self.label_active_sensor.setFixedWidth(240)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 180)
        self.slider.setEnabled(False) 
        self.slider.setCursor(Qt.PointingHandCursor)
        
        slider_qss = """
        QSlider {
            background: transparent;
            border: none;
            min-height: 26px; /* Expands bounding box bounding edge to eliminate thumb rendering clips */
        }
        QSlider::groove:horizontal {
            border: none;
            height: 8px;
            background: #2C2C35;
            border-radius: 4px;
        }
        QSlider::sub-page:horizontal {
            background: #00FFB3;
            border-radius: 4px;
        }
        QSlider::add-page:horizontal {
            background: #2C2C35;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #FFFFFF;
            width: 20px;
            height: 20px;
            margin: -6px 0;
            border-radius: 10px;
        }
        QSlider::handle:horizontal:disabled {
            background: #4A4A55;
        }
        QSlider::sub-page:horizontal:disabled {
            background: #3A3A45;
        }
        """
        self.slider.setStyleSheet(slider_qss)
        self.slider.valueChanged.connect(self._on_slider_changed)

        slider_row.addWidget(self.label_active_sensor)
        slider_row.addWidget(self.slider, stretch=1)
        control_layout.addLayout(slider_row)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("border: none; background: #23232C; max-height: 1px;")
        control_layout.addWidget(divider)

        # Telemetry Block Array
        pipeline_layout = QHBoxLayout()
        pipeline_layout.setSpacing(0)
        
        secondary_layout = QHBoxLayout()
        secondary_layout.setSpacing(35)
        
        self.block_v = TelemetryLabelBlock("VOLTAGE OUTPUT")
        self.block_r = TelemetryLabelBlock("SENSOR RESISTANCE")
        self.block_g = TelemetryLabelBlock("CONDUCTANCE")
        
        secondary_layout.addWidget(self.block_v)
        secondary_layout.addWidget(self.block_r)
        secondary_layout.addWidget(self.block_g)
        secondary_layout.addStretch()
        
        self.block_f = TelemetryLabelBlock("APPLIED FORCE", is_hero=True, align_right=True)
        
        pipeline_layout.addLayout(secondary_layout, stretch=1)
        pipeline_layout.addWidget(self.block_f)
        
        control_layout.addLayout(pipeline_layout)
        root.addWidget(self.control_panel)

    def _format_metric(self, val: float, unit: str) -> str:
        if val == float('inf'):
            return "Open (∞)"
        
        if unit == "V":
            return f"{val:,.2f} V"
            
        elif unit == "Ω":
            if val >= 1_000_000:
                return f"{val / 1_000_000:,.2f} MΩ"
            elif val >= 1_000:
                return f"{val / 1_000:,.2f} kΩ"
            return f"{val:,.2f} Ω"
            
        elif unit == "S":
            if val < 0.000001:
                if val == 0: return "0.00 S"
                return f"{val:.2e} S"
            elif val < 0.001:
                return f"{val * 1_000_000:,.2f} µS"
            elif val < 1.0:
                return f"{val * 1_000:,.2f} mS"
            return f"{val:,.2f} S"
            
        elif unit == "N":
            if val >= 1_000_000:
                return f"{val / 1_000_000:,.2f} MN"
            elif val >= 1_000:
                return f"{val / 1_000:,.2f} kN"
            return f"{val:,.2f} N"
            
        return f"{val:,.2f}"

    def _on_sensor_clicked(self, sensor_idx: int):
        if self.state_manager.active_sensor_id == sensor_idx:
            # Null state deselection toggle
            self.state_manager.active_sensor_id = -1
        else:
            self.state_manager.active_sensor_id = sensor_idx
        
        active_id = self.state_manager.active_sensor_id
        
        # Deselected Null State Locking
        if active_id == -1:
            self.label_active_sensor.setText("No Zone Selected")
            self.label_active_sensor.setStyleSheet("border: none; background: transparent; color: #6A6A75; font-weight: normal; font-size: 14px;")
            
            self.slider.blockSignals(True)
            self.slider.setEnabled(False) 
            self.slider.setValue(0)
            self.slider.blockSignals(False)
            
            self.block_v.set_value("-- V")
            self.block_r.set_value("-- Ω")
            self.block_g.set_value("-- S")
            self.block_f.set_value("-- N")
        else:
            # Active Mapping
            name = self.sensor_names.get(active_id, f"Zone {active_id}")
            self.label_active_sensor.setText(name)
            self.label_active_sensor.setStyleSheet("border: none; background: transparent; color: #FFFFFF; font-weight: bold; font-size: 14px;")
            
            current_vout = self.state_manager.get_active_vout()
            val_int = int(current_vout * 100)
            
            self.slider.blockSignals(True)
            self.slider.setEnabled(True)
            self.slider.setValue(val_int)
            self.slider.blockSignals(False)
        
        self._sync_ui_state()

    def _on_slider_changed(self, value: int):
        if self.state_manager.active_sensor_id == -1: return
        if self._scenario_state != 0:
            self._scenario_state = 0
            self.btn_scenario.setText("Scenario: Manual")
        v_out = value / 100.0
        self.state_manager.update_active_vout(v_out)
        self._sync_ui_state()

    def _sync_ui_state(self):
        active_id = self.state_manager.active_sensor_id
        
        if active_id != -1:
            v_out = self.state_manager.get_active_vout()
            physics = self.state_manager.calculate_physics(v_out)
            
            self.block_v.set_value(self._format_metric(physics['v_out'], "V"))
            self.block_r.set_value(self._format_metric(physics['r_fsr'], "Ω"))
            self.block_g.set_value(self._format_metric(physics['conductance'], "S"))
            self.block_f.set_value(self._format_metric(physics['force'], "N"))

        force_map = self.state_manager.get_full_force_array()
        thresholds = {i: self.state_manager.get_threshold_for_zone(i) for i in range(6)}
        self.asset_widget.update_data(force_map, active_id, thresholds)

        phase = calculate_gait_phase(force_map)
        self.label_gait_phase.setText(f"Current Phase: {phase}")

        # Evaluate Risk dynamically based on state manager thresholds
        critical = False
        msg = ""
        trigger_zone = -1
        max_excess = 0
        
        labels = {0: "Heel", 1: "Midfoot Lateral", 2: "Metatarsal I", 3: "Metatarsal III", 4: "Metatarsal V", 5: "Hallux (Big Toe)"}
        for sensor_id, force_n in force_map.items():
            threshold = self.state_manager.get_threshold_for_zone(sensor_id)
            excess = force_n - threshold
            if excess > max_excess:
                max_excess = excess
                trigger_zone = sensor_id
                
        if trigger_zone != -1:
            critical = True
            force_n = force_map[trigger_zone]
            threshold = self.state_manager.get_threshold_for_zone(trigger_zone)
            msg = f"WARNING: Critical Pressure Load at {labels.get(trigger_zone, 'Unknown')} ({force_n:.1f}N). Threshold is {threshold:.1f}N."
            
        if critical:
            self.label_alert.setText(msg)
            self.alert_container.setVisible(True)
            self.current_risk_zone = trigger_zone
        else:
            self.alert_container.setVisible(False)
            self.current_risk_zone = -1

        if hasattr(self, 'cb_voice_coach') and self.cb_voice_coach.isChecked():
            current_time = time.time()
            if critical:
                if current_time - self.last_speech_time > 5.0:
                    max_zone = max(force_map.keys(), key=lambda k: force_map[k])
                    speech_msg = ""
                    if max_zone == 0:
                        speech_msg = "Warning: High heel pressure. Please shift your weight slightly forward."
                    elif max_zone in [2, 3, 4]:
                        speech_msg = "Warning: High forefoot pressure. Please lower your heel."
                    elif max_zone == 1:
                        speech_msg = "Warning: Ankle rolling detected. Please stand flat."
                    elif max_zone == 5:
                        speech_msg = "Warning: High forefoot pressure. Please lower your heel."
                        
                    if speech_msg:
                        self.voice_coach_thread.speak(speech_msg)
                        self.last_speech_time = current_time
            else:
                if current_time - self.last_speech_time > 10.0 and sum(force_map.values()) > 0:
                    self.voice_coach_thread.speak("Posture is balanced. Good job.")
                    self.last_speech_time = current_time

    def _show_correction_dialog(self):
        if hasattr(self, 'current_risk_zone') and self.current_risk_zone != -1:
            dialog = CorrectionDialog(self.current_risk_zone, self)
            dialog.exec_()

    def _on_clear_clicked(self):
        self._scenario_state = 0
        self.btn_scenario.setText("Scenario: Manual")
        for i in range(6):
            self.state_manager.vout_values[i] = 0.0
        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)
        self._sync_ui_state()

    def _on_scenario_clicked(self):
        self._scenario_state = (self._scenario_state + 1) % 4

        _scenarios = {
            0: ("Scenario: Manual",     None),
            1: ("Scenario: Heel Strike", {0: 2.9, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1}),
            2: ("Scenario: Mid-Stance",  {i: 1.5 for i in range(6)}),
            3: ("Scenario: Heel-Off",    {0: 0.1, 1: 0.3, 2: 2.5, 3: 2.5, 4: 2.5, 5: 2.5}),
        }

        label, voltages = _scenarios[self._scenario_state]
        self.btn_scenario.setText(label)

        if voltages is not None:
            for i, v in voltages.items():
                self.state_manager.vout_values[i] = v
            if self.state_manager.active_sensor_id != -1:
                current_vout = self.state_manager.get_active_vout()
                self.slider.blockSignals(True)
                self.slider.setValue(int(current_vout * 100))
                self.slider.blockSignals(False)

        self._sync_ui_state()

    def _on_generate_report_clicked(self):
        force_map = self.state_manager.get_full_force_array()
        if not force_map:
            QMessageBox.warning(self, "No Data", "No pressure data available to generate report.")
            return

        # 1. Capture Screenshot
        img_path = "temp_foot_map.png"
        pixmap = self.asset_widget.grab()
        pixmap.save(img_path)

        # 2. Extract Data
        phase = calculate_gait_phase(force_map)
        critical, risk_msg = check_ulcer_risk(force_map, self.state_manager.patient_weight)
        max_zone = max(force_map.keys(), key=lambda k: force_map[k])

        advice = ""
        if critical:
            if max_zone == 0:
                advice = ("What This Means: Putting too much weight on your heel for a long time can cause "
                          "painful sores and put unnecessary strain on the back of your knee.\n\n"
                          "Action Plan: Have your prosthetist check if your socket is leaning too far back. "
                          "Adding a softer heel cushion and practicing shifting your weight slightly forward "
                          "when you walk will help protect your joints.")
            elif max_zone in [2, 3, 4]:
                advice = ("What This Means: Constantly standing on the ball of your foot can cause severe foot pain, "
                          "skin damage, and eventually lead to hip pain from walking unevenly.\n\n"
                          "Action Plan: Ask your prosthetist to check if your foot is angled too far down. "
                          "Using special pressure-relief pads and practicing a smooth 'heel-to-toe' stepping motion "
                          "will relieve this strain.")
            elif max_zone == 1:
                advice = ("What This Means: Leaning too much on the inside or outside edge of your foot means your body "
                          "is off-balance. Over time, this uneven walking can wear down your healthy knee and hip joints.\n\n"
                          "Action Plan: Your socket needs to be adjusted so your foot sits flat on the ground. Physical "
                          "therapy exercises to strengthen your hip and side muscles will help keep your body straight "
                          "and balanced when you walk.")
            elif max_zone == 5:
                advice = ("What This Means: Constantly standing on the ball of your foot can cause severe foot pain, "
                          "skin damage, and eventually lead to hip pain from walking unevenly.\n\n"
                          "Action Plan: Ask your prosthetist to check if your foot is angled too far down. "
                          "Using special pressure-relief pads and practicing a smooth 'heel-to-toe' stepping motion "
                          "will relieve this strain.")
            else:
                advice = "Pressure imbalance detected. Please consult your prosthetist."
        else:
            advice = ("What This Means: Excellent job. Your current weight distribution is balanced and safe. "
                      "Your socket alignment is properly distributing the load across your foot, which protects your skin and your healthy joints.\n\n"
                      "Action Plan: Keep up the good work! Continue practicing this posture and gait. No immediate adjustments to your prosthetic alignment are necessary at this time.")

        # 3. Generate PDF
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, txt="SensiFoot Patient Posture Report", ln=True, align='C')

        pdf.set_font("Helvetica", '', 12)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 10, txt=f"Date: {current_time}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, txt="Section 1: Current Stance", ln=True)
        pdf.set_font("Helvetica", '', 12)
        pdf.cell(0, 10, txt=f"Active Gait Phase: {phase}", ln=True)
        pdf.ln(5)

        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, txt="Section 2: Visual Map", ln=True)
        pdf.set_font("Helvetica", '', 12)
        pdf.cell(0, 10, txt="Below is the current plantar pressure map:", ln=True)
        pdf.ln(5)

        if os.path.exists(img_path):
            pdf.image(img_path, x=55, w=100)
            pdf.ln(5)

        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, txt="Section 3: High-Pressure Areas", ln=True)
        pdf.set_font("Helvetica", '', 12)
        if critical:
            pdf.multi_cell(0, 8, txt=f"Alert: {risk_msg}")
        else:
            pdf.multi_cell(0, 8, txt="No high-pressure ulcer risks detected currently.")
        pdf.ln(5)

        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, txt="Section 4: Long-Term Advice", ln=True)
        pdf.set_font("Helvetica", '', 12)
        pdf.multi_cell(0, 6, txt=advice)

        report_path = "patient_report.pdf"
        try:
            pdf.output(report_path)
            QMessageBox.information(self, "Report Generated", f"Patient report saved successfully as {report_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")

        if os.path.exists(img_path):
            os.remove(img_path)

    def _on_toggle_sensors_clicked(self):
        new_state = not self.asset_widget.canvas.show_sensor_nodes
        self.asset_widget.toggle_sensor_nodes(new_state)
        self.btn_toggle_sensors.setText("Hide Sensors" if new_state else "Show Sensors")

    def _on_voice_coach_toggled(self, state):
        if state == Qt.Checked:
            self.cb_voice_coach.setText("Voice Coach: ON")
        else:
            self.cb_voice_coach.setText("Voice Coach: OFF")

    def _on_weight_changed(self, value: float):
        self.state_manager.update_weight(value)
        self._sync_ui_state()

    def closeEvent(self, event):
        if hasattr(self, 'voice_coach_thread'):
            self.voice_coach_thread.stop()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.dirname(os.path.dirname(current_dir))
        perform_cleanup(workspace_root)
        event.accept()
