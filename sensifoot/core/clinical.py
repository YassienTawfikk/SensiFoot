from typing import Tuple, List, Optional

def calculate_cop(force_map: dict, centroids: dict) -> Optional[Tuple[float, float]]:
    """
    Calculates the Center of Pressure (CoP) by evaluating the weighted average
    of physical force loads across structural centroid coordinate assignments.
    Returns standard (X, Y) float tuple cleanly decoupied from UI implementations.
    """
    weighted_x = 0.0
    weighted_y = 0.0
    total_weight = 0.0
    
    for idx, (cx, cy) in centroids.items():
        f = force_map.get(idx, 0.0)
        if f > 0:
            weighted_x += f * cx
            weighted_y += f * cy
            total_weight += f

    if total_weight > 0:
        return (weighted_x / total_weight, weighted_y / total_weight)

    return None

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

def check_ulcer_risk(force_map: dict, patient_weight: float = 70.0) -> Tuple[bool, str]:
    """
    Triggers true if any localized zone exceeds the dynamic weight-based threshold.
    """
    labels = {
        0: "Heel",
        1: "Midfoot Lateral",
        2: "Metatarsal I",
        3: "Metatarsal III",
        4: "Metatarsal V",
        5: "Hallux (Big Toe)"
    }
    
    thresholds = {
        0: patient_weight * 0.80,
        1: patient_weight * 0.25,
        2: patient_weight * 0.70,
        3: patient_weight * 0.70,
        4: patient_weight * 0.70,
        5: patient_weight * 0.30
    }
    
    for sensor_id, force_n in force_map.items():
        threshold = thresholds.get(sensor_id, 85.0)
        if force_n > threshold:
            return True, f"WARNING: Critical Pressure Load at {labels.get(sensor_id, 'Unknown')} ({force_n:.1f}N). Threshold is {threshold:.1f}N."
            
    return False, ""
