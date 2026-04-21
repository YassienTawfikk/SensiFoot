from dataclasses import dataclass, field
from typing import Dict

@dataclass
class SensorState:
    """
    Manages the physical hardware telemetry state of the 6-sensor FSR circuit array.
    """
    # Raw Voltage maps sensor_id (0-5) to V_out (0.0 to 3.3V)
    vout_values: Dict[int, float] = field(default_factory=lambda: {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.0
    })
    
    active_sensor_id: int = -1
    
    # Constants
    V_CC = 3.3
    R_FIXED = 10_000.0      # 10 kΩ
    FORCE_M = 1_000_000.0   # 1 MN
    FORCE_B = 0.0

    def update_active_vout(self, voltage: float):
        if self.active_sensor_id != -1:
            self.vout_values[self.active_sensor_id] = max(0.0, min(self.V_CC, voltage))
            
    def get_active_vout(self) -> float:
        return self.vout_values.get(self.active_sensor_id, 0.0)

    def calculate_physics(self, v_out: float) -> dict:
        """
        Executes mathematically sound raw FSR pipeline.
        Returns Dictionary of pipeline steps.
        """
        if v_out <= 0.01:
            r_fsr = float('inf')
            g_fsr = 0.0
            force = 0.0
        else:
            try:
                # Standard Divider Algorithm
                r_fsrRaw = self.R_FIXED * ((self.V_CC / v_out) - 1.0)
                # Hard Hardware Cap to prevent Infinity cascade
                r_fsr = max(50.0, r_fsrRaw)
                
                g_fsr = 1.0 / r_fsr
                force = (self.FORCE_M * g_fsr) + self.FORCE_B
            except ZeroDivisionError:
                r_fsr = 50.0
                g_fsr = 1.0 / r_fsr
                force = (self.FORCE_M * g_fsr) + self.FORCE_B

        return {
            "v_out": v_out,
            "r_fsr": r_fsr,
            "conductance": g_fsr,
            "force": force
        }

    def get_full_force_array(self) -> Dict[int, float]:
        """
        Extracts exclusively the resulting physical Force mapping for Clinical diagnostics.
        """
        forces = {}
        for sensor_id, vout in self.vout_values.items():
            forces[sensor_id] = self.calculate_physics(vout)["force"]
        return forces
