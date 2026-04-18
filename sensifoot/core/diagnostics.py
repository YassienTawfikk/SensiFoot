from typing import Tuple, List

def evaluate_pressure(sensor_values: dict) -> Tuple[int, List[float]]:
    """
    Evaluates the 6-point pressure array using a deterministic algorithm and returns a 
    class_id and simulated confidence metrics list.
    
    Sensors:
    0: Heel, 1: Midfoot Lateral, 2: Meta 1 (Inner), 3: Meta 3 (Center), 4: Meta 5 (Outer), 5: Hallux
    """
    confidences = [0.0] * 9
    class_id = 0
    
    heel = sensor_values[0]
    mid_lat = sensor_values[1]
    meta_inner = sensor_values[2]
    meta_center = sensor_values[3]
    meta_outer = sensor_values[4]
    toe = sensor_values[5]
    
    # Compute aggregate distributions
    total_front = meta_inner + meta_center + meta_outer + toe
    total_back = heel + mid_lat
    
    lateral_load = meta_outer + mid_lat
    medial_load = meta_inner + toe
    
    # Basic logic
    # Pronation risk: high medial load, low lateral
    if medial_load - lateral_load > 150:
        class_id = 5 # Left Lateral (Pronation Risk)
    elif lateral_load - medial_load > 150:
        class_id = 6 # Right Lateral (Supination Risk)
    else:
        diff_fw_bw = total_front - (total_back * 2) # Adjust for sensor count
        if diff_fw_bw > 150:
            class_id = 1 # Forward Lean
        elif diff_fw_bw < -150:
            class_id = 3 # Backward Lean
        else:
            class_id = 0 # Normal Gait
            
    # Danger states
    if any(val >= 240 for val in sensor_values.values()):
        class_id = 7 # Severe Misalignment (General Danger)
        
    confidences[class_id] = 0.98
    for i in range(9):
        if i != class_id:
            confidences[i] = 0.02 / 8.0
            
    return class_id, confidences
