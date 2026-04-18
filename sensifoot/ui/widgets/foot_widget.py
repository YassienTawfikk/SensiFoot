import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush, QFont
from PyQt5.QtCore import Qt, QPointF, pyqtSignal

class FootWireframeCanvas(QWidget):
    sensorClicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self.setMouseTracking(True)
        
        self.force_values = {i: 0.0 for i in range(6)}
        self.active_sensor_id = -1
        self.hovered_sensor_id = -1

        self.show_sensor_nodes = False
        self._build_zones()

        self.centroids = {
            0: QPointF(52, 200), 1: QPointF(52, 140), 2: QPointF(27, 80),  
            3: QPointF(52, 80),  4: QPointF(77, 80),  5: QPointF(52, 25)   
        }

    def _build_zones(self):
        self.zone_paths = {}

        L1, R1 = QPointF(15, 50), QPointF(90, 50)
        L2, R2 = QPointF(15, 110), QPointF(90, 110)
        L3, R3 = QPointF(25, 170), QPointF(80, 170)
        
        M1_T, M2_T = QPointF(40, 50), QPointF(65, 50)
        M1_B, M2_B = QPointF(40, 110), QPointF(65, 110)

        # 5
        p5 = QPainterPath()
        p5.moveTo(L1)
        p5.cubicTo(15, 20, 30, 0, 50, 5)            
        p5.cubicTo(70, 10, 85, 25, R1.x(), R1.y())  
        p5.lineTo(M2_T)                             
        p5.lineTo(M1_T)
        p5.lineTo(L1)
        self.zone_paths[5] = p5
        # 2
        p2 = QPainterPath()
        p2.moveTo(L1)
        p2.lineTo(M1_T)
        p2.lineTo(M1_B)
        p2.lineTo(L2)
        p2.cubicTo(0, 95, 5, 65, L1.x(), L1.y())    
        self.zone_paths[2] = p2
        # 3
        p3 = QPainterPath()
        p3.moveTo(M1_T)
        p3.lineTo(M2_T)
        p3.lineTo(M2_B)
        p3.lineTo(M1_B)
        p3.lineTo(M1_T)
        self.zone_paths[3] = p3
        # 4
        p4 = QPainterPath()
        p4.moveTo(M2_T)
        p4.lineTo(R1)
        p4.cubicTo(100, 65, 95, 95, R2.x(), R2.y()) 
        p4.lineTo(M2_B)
        p4.lineTo(M2_T)
        self.zone_paths[4] = p4
        # 1
        p1 = QPainterPath()
        p1.moveTo(L2)
        p1.lineTo(M1_B)
        p1.lineTo(M2_B)
        p1.lineTo(R2)
        p1.cubicTo(85, 130, 85, 150, R3.x(), R3.y()) 
        p1.lineTo(L3)
        p1.cubicTo(45, 150, 45, 130, L2.x(), L2.y()) 
        self.zone_paths[1] = p1
        # 0
        p0 = QPainterPath()
        p0.moveTo(L3)
        p0.lineTo(R3)
        p0.cubicTo(80, 200, 70, 230, 50, 230)       
        p0.cubicTo(30, 230, 25, 200, L3.x(), L3.y()) 
        self.zone_paths[0] = p0

    def toggle_sensor_nodes(self, show: bool):
        self.show_sensor_nodes = show
        self.update()

    def update_data(self, force_map: dict, active_id: int):
        self.force_values = force_map
        self.active_sensor_id = active_id
        self.update()

    def get_cop(self):
        weighted_x = 0.0
        weighted_y = 0.0
        total_weight = 0.0
        
        for idx, pt in self.centroids.items():
            f = self.force_values.get(idx, 0.0)
            if f > 0:
                weighted_x += f * pt.x()
                weighted_y += f * pt.y()
                total_weight += f
                
        if total_weight > 0:
            return QPointF(weighted_x / total_weight, weighted_y / total_weight)
        return None

    def mouseMoveEvent(self, event):
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        scale = min(w, h) / 200.0 # Synced perfectly to paintEvent geometry scaling

        mouse_x = (event.x() - cx) / scale
        mouse_y = (event.y() - cy) / scale
        
        abstract_x = mouse_x + 50
        abstract_y = mouse_y + 115

        hover_found = -1
        pt = QPointF(abstract_x, abstract_y)
        for i, path in self.zone_paths.items():
            if path.contains(pt):
                hover_found = i
                break
        
        if hover_found != self.hovered_sensor_id:
            self.hovered_sensor_id = hover_found
            if hover_found != -1:
                self.setCursor(Qt.PointingHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            self.update()

    def mousePressEvent(self, event):
        if self.hovered_sensor_id != -1:
            self.sensorClicked.emit(self.hovered_sensor_id)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#0D0D11"))

        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        scale = min(w, h) / 200.0   
        
        painter.translate(cx, cy)
        painter.scale(scale, scale)
        painter.translate(-50, -115)
        
        # Strict 3-Tier Z-Index Hierarchy
        draw_order = []
        
        # Tier 0: Inactive/Default Zones (Lowest Elevation)
        for i in self.zone_paths.keys():
            if i != self.active_sensor_id and i != self.hovered_sensor_id:
                draw_order.append(i)
                
        # Tier 1: Hovered Zones (Elevate over default adjacent borders)
        if self.hovered_sensor_id != -1 and self.hovered_sensor_id != self.active_sensor_id:
            draw_order.append(self.hovered_sensor_id)
            
        # Tier 2: Selected/Active Zones (Absolute Highest Elevation, Never Clipped)
        if self.active_sensor_id != -1:
            draw_order.append(self.active_sensor_id)
        
        for i in draw_order:
            path = self.zone_paths[i]
            force_val = self.force_values.get(i, 0.0)
            is_active = (i == self.active_sensor_id)
            is_hover = (i == self.hovered_sensor_id)

            # Cap opacity visualization at roughly 150N
            fill_op = min(255, max(10, int((force_val / 150.0) * 180)))
            
            if force_val > 85:
                fill_color = QColor(255, 51, 51, 200) # Blazing critical red
            else:
                fill_color = QColor(0, 170, 255, fill_op) if is_active else QColor(255, 255, 255, fill_op)
            
            painter.setBrush(QBrush(fill_color))

            stroke_pen = QPen()
            stroke_pen.setJoinStyle(Qt.RoundJoin)
            
            if is_active:
                stroke_pen.setColor(QColor("#00AAFF"))
                stroke_pen.setWidthF(3.5)
            elif is_hover:
                stroke_pen.setColor(QColor("#FFFFFF"))
                stroke_pen.setWidthF(2.0)
            else:
                stroke_pen.setColor(QColor("#4A4A55"))
                stroke_pen.setWidthF(1.5)
            
            painter.setPen(stroke_pen)
            painter.drawPath(path)

        # Sensor Node Overlay
        if self.show_sensor_nodes:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor("#B0B0B5")))
            for pt in self.centroids.values():
                painter.drawEllipse(pt, 3, 3)

            # Coordinate labels — convert to screen space to avoid scale distortion
            screen_pts = {idx: painter.transform().map(pt) for idx, pt in self.centroids.items()}
            painter.save()
            painter.resetTransform()
            _lbl_font = QFont()
            _lbl_font.setPointSize(8)
            painter.setFont(_lbl_font)
            painter.setPen(QPen(QColor("#A0A0A5")))
            for idx, spt in screen_pts.items():
                abs_pt = self.centroids[idx]
                painter.drawText(int(spt.x()) + 8, int(spt.y()) + 4,
                                 f"({int(abs_pt.x())}, {int(abs_pt.y())})")
            painter.restore()

        # Output B: High-Contrast Center of Pressure (CoP) mapping evaluated strictly via Force load
        cop_pt = self.get_cop()
        if cop_pt is not None:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 230, 0, 80)))
            painter.drawEllipse(cop_pt, 10, 10)
            painter.setBrush(QBrush(QColor("#FFE600")))
            painter.drawEllipse(cop_pt, 4, 4)

        painter.end()


class FootAssetWidget(QWidget):
    sensorClicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = FootWireframeCanvas()
        self.canvas.sensorClicked.connect(self.sensorClicked.emit)
        layout.addWidget(self.canvas)

    def update_data(self, force_map: dict, active_id: int):
        self.canvas.update_data(force_map, active_id)

    def toggle_sensor_nodes(self, show: bool):
        self.canvas.toggle_sensor_nodes(show)
