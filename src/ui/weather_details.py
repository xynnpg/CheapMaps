from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QWidget, QPushButton, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QDate, QPoint
from PyQt5.QtGui import QColor, QLinearGradient, QPalette, QBrush
from src.utils.weather_service import WeatherService

class WeatherDayCard(QFrame):
    def __init__(self, day_name, date_str, emoji, high, low, prob, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            WeatherDayCard {
                background-color: #252525;
                border-radius: 8px;
                border: 1px solid #333;
            }
            WeatherDayCard:hover {
                background-color: #2f2f2f;
                border: 1px solid #444;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        # Date Section
        date_layout = QVBoxLayout()
        day_lbl = QLabel(day_name)
        day_lbl.setStyleSheet("font-size: 15px; font-weight: 600; color: #e0e0e0;")
        
        date_sub_lbl = QLabel(date_str)
        date_sub_lbl.setStyleSheet("font-size: 12px; color: #808080;")
        
        date_layout.addWidget(day_lbl)
        date_layout.addWidget(date_sub_lbl)
        
        # Icon Section
        icon_lbl = QLabel(emoji)
        icon_lbl.setStyleSheet("font-size: 24px; background: transparent;")
        icon_lbl.setAlignment(Qt.AlignCenter)
        
        # Rain/Prob Section
        rain_widget = QWidget()
        rain_layout = QHBoxLayout(rain_widget)
        rain_layout.setContentsMargins(0,0,0,0)
        rain_layout.setSpacing(4)
        
        if prob > 0:
            rain_icon = QLabel("💧")
            rain_icon.setStyleSheet("font-size: 10px; color: #00d4ff; background: transparent;")
            rain_val = QLabel(f"{prob}%")
            rain_val.setStyleSheet("font-size: 13px; font-weight: 600; color: #00d4ff; background: transparent;")
            rain_layout.addWidget(rain_icon)
            rain_layout.addWidget(rain_val)
        else:
            rain_val = QLabel("")
            rain_layout.addWidget(rain_val)
            
        # Temp Section
        temp_layout = QVBoxLayout()
        high_lbl = QLabel(f"{high}°")
        high_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        high_lbl.setAlignment(Qt.AlignRight)
        
        low_lbl = QLabel(f"{low}°")
        low_lbl.setStyleSheet("font-size: 13px; font-weight: normal; color: #666;")
        low_lbl.setAlignment(Qt.AlignRight)
        
        temp_layout.addWidget(high_lbl)
        temp_layout.addWidget(low_lbl)
        
        # Assemble
        layout.addLayout(date_layout, stretch=3)
        layout.addWidget(icon_lbl, stretch=2)
        layout.addWidget(rain_widget, stretch=2, alignment=Qt.AlignCenter)
        layout.addLayout(temp_layout, stretch=2)

class WeatherDetailDialog(QDialog):
    def __init__(self, lat, lon, location_name, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(400)
        self.setFixedHeight(550)
        
        self.m_drag_position = None
        
        # Main Container - Minimalistic Dark
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 400, 550)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #3d3d3d;
            }
        """)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Header ---
        header = QFrame()
        header.setStyleSheet("background: transparent; border-bottom: 1px solid #2b2b2b; border-radius: 0px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_box = QVBoxLayout()
        city_lbl = QLabel(location_name)
        city_lbl.setStyleSheet("font-size: 18px; font-weight: 700; color: #ffffff; border: none;")
        sub_lbl = QLabel("7-DAY FORECAST")
        sub_lbl.setStyleSheet("font-size: 11px; color: #00d4ff; font-weight: 600; letter-spacing: 1px; border: none;")
        
        title_box.addWidget(city_lbl)
        title_box.addWidget(sub_lbl)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #fff;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(close_btn, alignment=Qt.AlignTop)
        
        main_layout.addWidget(header)
        
        # --- Scroll Area ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,0.1);
                width: 6px;
                border-radius: 3px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.2);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(20, 10, 20, 20)
        
        self.scroll.setWidget(content)
        main_layout.addWidget(self.scroll)
        
        # Fetch Data
        self.service = WeatherService()
        data = self.service.get_forecast(lat, lon)
        if data:
            self.populate_forecast(data)
        else:
            err = QLabel("Could not load forecast data.")
            err.setStyleSheet("color: rgba(255,255,255,0.5); font-style: italic;")
            err.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(err)

    def populate_forecast(self, data):
        times = data.get('time', [])
        codes = data.get('weathercode', [])
        max_temps = data.get('temperature_2m_max', [])
        min_temps = data.get('temperature_2m_min', [])
        probs = data.get('precipitation_probability_max', [])
        
        for i in range(len(times)):
            date_str = times[i]
            code = codes[i]
            high = round(max_temps[i])
            low = round(min_temps[i])
            prob = probs[i] if probs else 0
            
            # Format Date
            date_obj = QDate.fromString(date_str, "yyyy-MM-dd")
            day_name = date_obj.toString("dddd")
            short_date = date_obj.toString("MMM d")
            if i == 0: day_name = "Today"
            
            # Icon
            desc = self.service._get_weather_description(code)
            emoji = desc.split(" ")[0] if " " in desc else "❓"
            
            card = WeatherDayCard(day_name, short_date, emoji, high, low, prob)
            
            # Anim effect (optional/simple)
            shadow = QGraphicsDropShadowEffect(card)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 50))
            shadow.setOffset(0, 4)
            card.setGraphicsEffect(shadow)
            
            self.content_layout.addWidget(card)

    # --- Dragging Logic for Frameless Window ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.m_drag_position:
            self.move(event.globalPos() - self.m_drag_position)
            event.accept()
