import cv2
import numpy as np

def synthesize_heatmap(heel: int, toe: int, balance: int) -> np.ndarray:
    """
    Translate slider values into a 224x224 RGB pressure heatmap.

    Parameters
    ----------
    heel    : 0-255   posterior socket pressure
    toe     : 0-255   anterior socket pressure
    balance : -100-100  lateral offset (negative = left, positive = right)

    Returns
    -------
    np.ndarray  shape (224, 224, 3), dtype uint8, RGB colour order
    """
    canvas = np.zeros((224, 224), dtype=np.float32)

    offset_x = int(balance * 0.5)                        # maps +-100 to +-50 px
    heel_x = int(np.clip(112 + offset_x, 20, 204))
    toe_x  = int(np.clip(112 + offset_x, 20, 204))

    heel_radius = max(5, int(heel / 255.0 * 55))         # 5-55 px
    toe_radius  = max(5, int(toe  / 255.0 * 45))         # 5-45 px

    heel_intensity = heel / 255.0
    toe_intensity  = toe  / 255.0

    cv2.circle(canvas, (heel_x, 180), heel_radius, heel_intensity, thickness=-1)
    cv2.circle(canvas, (toe_x,  44),  toe_radius,  toe_intensity,  thickness=-1)

    canvas = cv2.GaussianBlur(canvas, (21, 21), 0)

    heatmap_bgr = cv2.applyColorMap(np.uint8(canvas * 255), cv2.COLORMAP_JET)
    return cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)   # (224,224,3) uint8 RGB
