from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QCursor
from src.utils.weather_service import WeatherService
from src.ui.weather_details import WeatherDetailDialog

class WeatherWorker(QThread):
    result_ready = pyqtSignal(object)

    def __init__(self, lat, lon):
        super().__init__()
        self.lat = lat
        self.lon = lon
        self.service = WeatherService()

    def run(self):
        data = self.service.get_current_weather(self.lat, self.lon)
        self.result_ready.emit(data)

class WeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WeatherWidget")
        
        # Layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.layout.setSpacing(10)
        
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        # State
        self.current_lat = 0
        self.current_lon = 0
        # Default name if none provided/known
        self.location_name = "Selected Location"
        
        # UI Elements
        self.lbl_icon = QLabel("🌍")
        self.lbl_icon.setStyleSheet("font-size: 24px; background: transparent;")
        
        self.lbl_temp = QLabel("--°C")
        self.lbl_temp.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background: transparent;")
        
        self.lbl_desc = QLabel("Loading...")
        self.lbl_desc.setStyleSheet("font-size: 12px; color: #ccc; background: transparent;")
        
        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.addWidget(self.lbl_temp)
        text_layout.addWidget(self.lbl_desc)
        
        self.layout.addWidget(self.lbl_icon)
        self.layout.addLayout(text_layout)
        
        # Style
        self.setStyleSheet("""
            WeatherWidget {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.hide() 

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            dlg = WeatherDetailDialog(self.current_lat, self.current_lon, self.location_name, self)
            dlg.exec_()

    def fetch_weather(self, lat, lon, name="Current Location"):
        self.current_lat = lat
        self.current_lon = lon
        self.location_name = name
        
        self.lbl_desc.setText("Loading...")
        self.show()
        
        self.worker = WeatherWorker(lat, lon)
        self.worker.result_ready.connect(self.update_ui)
        self.worker.start()

    def update_ui(self, data):
        if data:
            self.lbl_temp.setText(f"{data['temperature']}°C")
            
            # Split emoji and text if possible
            desc = data['description']
            if " " in desc:
                emoji, text = desc.split(" ", 1)
                self.lbl_icon.setText(emoji)
                self.lbl_desc.setText(text)
            else:
                self.lbl_desc.setText(desc)
        else:
            self.lbl_desc.setText("Unavailable")
