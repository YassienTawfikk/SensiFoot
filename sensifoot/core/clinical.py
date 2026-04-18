from typing import Tuple, List

def calculate_gait_phase(force_map: dict) -> str:
    """
    Calculates the biomechanical gait phase using relative Force (Newtons) ratios.
    """
    total_force = sum(force_map.get(i, 0.0) for i in range(6))

    if total_force < 10.0:
        return "SWING PHASE"

    heel_force  = force_map.get(0, 0.0)
    front_force = sum(force_map.get(i, 0.0) for i in (2, 3, 4, 5))

    if heel_force > front_force:
        return "HEEL STRIKE"

    if front_force > heel_force * 4.0:
        return "HEEL-OFF"

    return "MID-STANCE"

def check_ulcer_risk(force_map: dict) -> Tuple[bool, str]:
    """
    Triggers true if any localized zone exceeds the 85 Newtons physical threshold.
    """
    labels = {
        0: "Heel",
        1: "Midfoot Lateral",
        2: "Metatarsal I",
        3: "Metatarsal III",
        4: "Metatarsal V",
        5: "Hallux (Big Toe)"
    }
    
    for sensor_id, force_n in force_map.items():
        if force_n > 85:
            return True, f"WARNING: Critical Pressure Load at {labels.get(sensor_id, 'Unknown')} ({force_n:.1f}N). Adjust Prosthetic Alignment."
            
    return False, ""
