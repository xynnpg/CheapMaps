from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from src.utils.completer_helper import LocationCompleter

class WaypointRow(QWidget):
    move_up_signal = pyqtSignal(QWidget)
    move_down_signal = pyqtSignal(QWidget)
    delete_signal = pyqtSignal(QWidget)
    return_pressed_signal = pyqtSignal()
    request_map_pick_signal = pyqtSignal(QWidget)

    def __init__(self, placeholder="Location..."):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 2, 0, 2)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.returnPressed.connect(self.return_pressed_signal.emit)
        
        self.loc_completer = LocationCompleter(self)
        self.input.setCompleter(self.loc_completer.completer)
        self.input.textEdited.connect(self.loc_completer.update_text)
        
        self.map_btn = QPushButton("📍")
        self.map_btn.setToolTip("Pick on Map")
        self.map_btn.setFixedWidth(25)
        self.map_btn.clicked.connect(lambda: self.request_map_pick_signal.emit(self))
        
        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedWidth(25)
        self.up_btn.clicked.connect(lambda: self.move_up_signal.emit(self))
        
        self.down_btn = QPushButton("↓")
        self.down_btn.setFixedWidth(25)
        self.down_btn.clicked.connect(lambda: self.move_down_signal.emit(self))
        
        self.del_btn = QPushButton("✕")
        self.del_btn.setFixedWidth(25)
        self.del_btn.clicked.connect(lambda: self.delete_signal.emit(self))
        
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.map_btn)
        self.layout.addWidget(self.up_btn)
        self.layout.addWidget(self.down_btn)
        self.layout.addWidget(self.del_btn)
        
    def text(self):
        return self.input.text()
        
    def set_text(self, text):
        self.input.setText(text)

class DirectionsPanel(QWidget):
    go_signal = pyqtSignal()
    request_map_pick = pyqtSignal(QWidget)
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        
        self.waypoints = []
        self.init_waypoints()
        
        self.controls_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("+ Add Stop")
        self.add_btn.clicked.connect(lambda: self.add_waypoint("Stop..."))
        
        self.go_btn = QPushButton("Go")
        self.go_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white;")
        self.go_btn.clicked.connect(self.go_signal.emit)
        
        self.controls_layout.addWidget(self.add_btn)
        self.controls_layout.addWidget(self.go_btn)
        
        self.layout.addWidget(self.scroll)
        self.layout.addLayout(self.controls_layout)
        
    def init_waypoints(self):
        self.add_waypoint("Start Location...")
        self.add_waypoint("Destination...")
        
    def add_waypoint(self, placeholder="Stop..."):
        row = WaypointRow(placeholder)
        row.move_up_signal.connect(self.move_row_up)
        row.move_down_signal.connect(self.move_row_down)
        row.delete_signal.connect(self.delete_row)
        row.return_pressed_signal.connect(self.go_signal.emit)
        row.request_map_pick_signal.connect(self.request_map_pick.emit)
        
        self.waypoints.append(row)
        self.scroll_layout.addWidget(row)
        self.update_buttons_state()
        
    def move_row_up(self, row):
        idx = self.waypoints.index(row)
        if idx > 0:
            self.waypoints[idx], self.waypoints[idx-1] = self.waypoints[idx-1], self.waypoints[idx]
            self.refresh_layout()
            
    def move_row_down(self, row):
        idx = self.waypoints.index(row)
        if idx < len(self.waypoints) - 1:
            self.waypoints[idx], self.waypoints[idx+1] = self.waypoints[idx+1], self.waypoints[idx]
            self.refresh_layout()

    def delete_row(self, row):
        if len(self.waypoints) <= 2:
            return 
            
        self.waypoints.remove(row)
        row.deleteLater()
        self.update_buttons_state()
        
    def refresh_layout(self):
        for i, row in enumerate(self.waypoints):
            self.scroll_layout.removeWidget(row)
            self.scroll_layout.insertWidget(i, row)
        self.update_buttons_state()
            
    def update_buttons_state(self):
        count = len(self.waypoints)
        for i, row in enumerate(self.waypoints):
            row.up_btn.setEnabled(i > 0)
            row.down_btn.setEnabled(i < count - 1)
            row.del_btn.setEnabled(count > 2)
            
            if i == 0:
                row.input.setPlaceholderText("Start Location (or My Location)...")
            elif i == count - 1:
                row.input.setPlaceholderText("Destination...")
            else:
                row.input.setPlaceholderText(f"Stop {i}...")

    def get_locations(self):
        return [row.text().strip() for row in self.waypoints if row.text().strip()]
    
    def set_start_location(self, text):
        if self.waypoints:
            self.waypoints[0].set_text(text)
