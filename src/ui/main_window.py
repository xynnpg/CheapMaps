import os
import json
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QColor
from src.utils.geocoder import Geocoder
from src.ui.directions_panel import DirectionsPanel
from src.utils.completer_helper import LocationCompleter
from src.ui.bridge import MapBridge
from src.ui.weather_widget import WeatherWidget
from src.ui.weather_widget import WeatherWidget
from PyQt5.QtWidgets import QMenu, QAction
import requests
from src.utils.resource_path import get_resource_path

class ReverseGeocodeWorker(QThread):
    result_ready = pyqtSignal(str, float, float)

    def __init__(self, lat, lng):
        super().__init__()
        self.lat = lat
        self.lng = lng

    def run(self):
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': self.lat,
            'lon': self.lng,
            'format': 'json'
        }
        headers = {'User-Agent': 'ProiectLogis_MapApp/1.0'}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                name = data.get('display_name', f"{self.lat:.4f}, {self.lng:.4f}")
                self.result_ready.emit(name, self.lat, self.lng)
        except Exception as e:
            print(f"Reverse Geo Error: {e}")

class StatsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatsPanel")
        self.setVisible(False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        self.lbl_info = QLabel("ROCKET ROUTE 🚀")
        self.lbl_info.setStyleSheet("color: #00d4ff; font-weight: bold; font-size: 12px; letter-spacing: 1px;")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        
        self.lbl_duration = QLabel("0 min")
        self.lbl_duration.setStyleSheet("color: #ffffff; font-weight: 900; font-size: 32px;")
        self.lbl_duration.setAlignment(Qt.AlignCenter)
        
        self.lbl_distance = QLabel("0 km")
        self.lbl_distance.setStyleSheet("color: #aaaaaa; font-weight: normal; font-size: 16px;")
        self.lbl_distance.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.lbl_info)
        layout.addWidget(self.lbl_duration)
        layout.addWidget(self.lbl_distance)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
    def update_stats(self, duration_sec, distance_m, alt_count=0):
        hours = int(duration_sec // 3600)
        minutes = int((duration_sec % 3600) // 60)
        
        time_str = ""
        if hours > 0:
            time_str += f"{hours}h "
        time_str += f"{minutes}min"
        
        self.lbl_duration.setText(time_str)
        
        dist_km = distance_m / 1000
        self.lbl_distance.setText(f"{dist_km:.1f} km")
        
        if alt_count > 0:
            self.lbl_info.setText(f"BEST ROUTE (+{alt_count} ALTERNATIVES)")
        else:
             self.lbl_info.setText("FASTEST ROUTE")

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ControlPanel")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CheapMaps 🌑")
        self.resize(1200, 800)
        
        self.geocoder = Geocoder()
        self.pending_input_widget = None
        
        self.setup_ui()
        self.apply_styles()
        
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            #ControlPanel, #StatsPanel {
                background-color: rgba(20, 20, 20, 240);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            QWidget {
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.5);
                border: 1px solid #444;
                border-radius: 8px;
                padding: 10px 12px;
                color: #fff;
                font-size: 15px;
            }
            QLineEdit:focus {
                border: 1px solid #00d4ff;
                background-color: rgba(0, 0, 0, 0.8);
            }
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #555;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            
            QPushButton#SearchBtn {
                background-color: #00d4ff;
                color: #000;
                border: none;
            }
            QPushButton#SearchBtn:hover {
                background-color: #00b8dd;
            }
            
            QPushButton#DirectionsToggle {
                background-color: transparent;
                border: 1px solid #00ff9d;
                color: #00ff9d;
            }
            QPushButton#DirectionsToggle:checked {
                background-color: #00ff9d;
                color: #000;
            }
            
            QPushButton#LocBtn {
                background-color: transparent;
                border: none;
                font-size: 18px;
            }
            QPushButton#LocBtn:hover {
                background-color: rgba(255,255,255,0.1);
            }
            
            QStatusBar {
                background-color: #121212;
                color: #888;
                border-top: 1px solid #222;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            
            QListView {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                color: #e0e0e0;
                selection-background-color: #007acc;
                selection-color: white;
            }
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background-color: #121212;")
        
        # FIX: Register Channel BEFORE setting URL
        self.bridge = MapBridge()
        self.bridge.mapClickedSignal.connect(self.handle_map_click)
        self.bridge.mapClickedSignal.connect(self.handle_map_click)
        self.bridge.routeSelectedSignal.connect(self.handle_route_selection)
        
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        map_path = get_resource_path('src/map_app.html')
        
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.LocalContentCanAccessFileUrls, True)
        self.web_view.setUrl(QUrl.fromLocalFile(map_path))
        
        main_layout.addWidget(self.web_view)
        
        # Controls
        self.control_panel = ControlPanel(central_widget)
        self.control_panel = ControlPanel(central_widget)
        self.control_panel.setGeometry(20, 20, 380, 110)
        
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find a place...")
        self.search_input.returnPressed.connect(self.perform_search)
        
        self.search_completer = LocationCompleter(self)
        self.search_input.setCompleter(self.search_completer.completer)
        self.search_input.textEdited.connect(self.search_completer.update_text)
        
        self.search_btn = QPushButton("Go")
        self.search_btn.setObjectName("SearchBtn")
        self.search_btn.setFixedWidth(50)
        self.search_btn.clicked.connect(self.perform_search)
        
        self.directions_toggle = QPushButton("↱")
        self.directions_toggle.setObjectName("DirectionsToggle")
        self.directions_toggle.setToolTip("Directions")
        self.directions_toggle.setCheckable(True)
        self.directions_toggle.setFixedWidth(40)
        self.directions_toggle.clicked.connect(self.toggle_directions)
        
        self.loc_btn = QPushButton("◎")
        self.loc_btn.setObjectName("LocBtn")
        self.loc_btn.setToolTip("My Location")
        self.loc_btn.setFixedWidth(40)
        self.loc_btn.clicked.connect(self.use_current_location)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.directions_toggle)
        search_layout.addWidget(self.loc_btn)
        
        search_layout.addWidget(self.loc_btn)
        
        # --- Map Enhancement Controls ---
        extras_layout = QHBoxLayout()
        extras_layout.setSpacing(8)
        
        # Layers Menu
        self.layer_btn = QPushButton("🗺️ Layers")
        self.layer_btn.setStyleSheet("padding: 4px 8px; font-size: 12px;")
        self.layer_menu = QMenu(self)
        self.layer_menu.setStyleSheet("QMenu { background-color: #2b2b2b; color: white; border: 1px solid #444; } QMenu::item:selected { background-color: #007acc; }")
        
        layers = [("Dark", "dark"), ("Light", "light"), ("Satellite", "satellite"), ("Terrain", "terrain")]
        for name, code in layers:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, c=code: self.switch_map_layer(c))
            self.layer_menu.addAction(action)
            
        self.layer_btn.setMenu(self.layer_menu)
        
        self.layer_btn.setMenu(self.layer_menu)
        
        extras_layout.addWidget(self.layer_btn)
        extras_layout.addStretch()

        self.control_panel.layout.addLayout(search_layout)
        self.control_panel.layout.addLayout(extras_layout)
        
        self.directions_panel = DirectionsPanel()
        self.directions_panel.go_signal.connect(self.get_directions)
        self.directions_panel.request_map_pick.connect(self.enable_map_pick_mode)
        self.directions_panel.setVisible(False)
        
        self.control_panel.layout.addWidget(self.directions_panel)
        
        # Stats Panel
        self.stats_panel = StatsPanel(central_widget)

        # Weather Widget
        self.weather_widget = WeatherWidget(central_widget)
        # We'll position it in resizeEvent

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position Stats Center Bottom
        p_width = 300
        p_height = 120
        x = (self.width() - p_width) // 2
        y = self.height() - p_height - 60 
        self.stats_panel.setGeometry(x, y, p_width, p_height)

        # Position Weather Widget Top Right
        w_width = 160
        w_height = 80
        wx = self.width() - w_width - 20
        wy = 20
        self.weather_widget.setGeometry(wx, wy, w_width, w_height)

    def toggle_directions(self):
        is_directions = self.directions_toggle.isChecked()
        self.directions_panel.setVisible(is_directions)
        self.stats_panel.setVisible(False)
        
        self.control_panel.adjustSize()
        
        if is_directions:
             self.search_input.setVisible(False)
             self.search_btn.setVisible(False)
             self.directions_panel.set_start_location("My Location") 
        else:
             self.search_input.setVisible(True)
             self.search_btn.setVisible(True)
        
        self.control_panel.adjustSize()
        if self.control_panel.width() < 380:
             self.control_panel.resize(380, self.control_panel.height())

    def switch_map_layer(self, layer_code):
        js_code = f"switchLayer('{layer_code}');"
        self.web_view.page().runJavaScript(js_code)

    def perform_search(self):
        if self.directions_toggle.isChecked():
            self.get_directions()
            return
            
        self.stats_panel.setVisible(False)

        query = self.search_input.text().strip()
        if not query:
            return
            
        result = self.geocoder.search(query)
        
        if result:
            lat = result['lat']
            lon = result['lon']
            name = result['display_name'].replace("'", "\\'") 
            js_code = f"updateLocation({lat}, {lon}, '{name}');"
            self.web_view.page().runJavaScript(js_code)
            
            # Update weather for searched location
            self.weather_widget.fetch_weather(lat, lon, name)
        else:
            QMessageBox.warning(self, "Not Found", f"Could not find location: {query}")

    def get_directions(self):
        all_points_txt = self.directions_panel.get_locations()
        
        if len(all_points_txt) < 2:
            QMessageBox.warning(self, "Missing Info", "Start & End required.")
            return

        geocoded_points = []
        for location_txt in all_points_txt:
            if location_txt.lower() == "my location":
                loc = self.geocoder.get_current_location()
            else:
                loc = self.geocoder.search(location_txt)
            if not loc:
                QMessageBox.warning(self, "Not Found", f"Unknown: {location_txt}")
                return
            geocoded_points.append((loc['lat'], loc['lon']))
             
        routes = self.geocoder.get_route(geocoded_points)
        if routes:
            self.current_routes = routes # Store for selection
            routes_json = json.dumps(routes)
            
            waypoints_manifest = []
            
            waypoints_manifest.append({
                'lat': geocoded_points[0][0], 'lng': geocoded_points[0][1],
                'name': all_points_txt[0], 'type': 'start'
            })
            
            for i in range(1, len(geocoded_points) - 1):
                 waypoints_manifest.append({
                    'lat': geocoded_points[i][0], 'lng': geocoded_points[i][1],
                    'name': all_points_txt[i], 'type': 'stop', 'index': i
                })
            
            waypoints_manifest.append({
                'lat': geocoded_points[-1][0], 'lng': geocoded_points[-1][1],
                'name': all_points_txt[-1], 'type': 'end'
            })
            
            waypoints_json = json.dumps(waypoints_manifest)
            js_code = f"drawRoute({routes_json}, {waypoints_json});"
            self.web_view.page().runJavaScript(js_code)
            
            primary_route = routes[0]
            alt_count = len(routes) - 1
            self.stats_panel.update_stats(primary_route['duration'], primary_route['distance'], alt_count)
            self.stats_panel.setVisible(True)
            self.stats_panel.raise_()
            
        else:
            QMessageBox.warning(self, "Error", "Route not found.")
            
    def handle_route_selection(self, index):
        if hasattr(self, 'current_routes') and 0 <= index < len(self.current_routes):
            # The JS side re-orders the array so index 0 is always the selected one visually.
            # But the index passed here is the ORIGINAL index in the Python list?
            # Wait, in JS I did: window.currentRoutesData.splice(newIndex, 1); unshift...
            # And backend.routeSelected(newIndex) calls with the index BEFORE reordering.
            
            # BUT, since JS reorders its local copy, if I click again, indices might be messy if I don't sync.
            # actually, simplest way: Python remains the source of truth.
            # When user clicks index X:
            # 1. Python updates its self.current_routes to move X to 0.
            # 2. Python updates StatsPanel with new 0.
            # 3. (Optional) Python triggers redraw? 
            # In my JS implementation, JS REDRAWS IMMEDIATELY. so JS data is already reordered.
            # So I should reorder Python data too to match JS.
            
            # Reorder python list to match JS (move index to 0)
            selected_route = self.current_routes.pop(index)
            self.current_routes.insert(0, selected_route)
            
            # Update Stats
            primary_route = self.current_routes[0]
            alt_count = len(self.current_routes) - 1
            self.stats_panel.update_stats(primary_route['duration'], primary_route['distance'], alt_count)

    def use_current_location(self):
        loc = self.geocoder.get_current_location()
        if loc:
            lat = loc['lat']
            lon = loc['lon']
            name = "My Location"
            
            if self.directions_toggle.isChecked():
                 self.directions_panel.set_start_location("My Location")
            else:
                js_code = f"updateLocation({lat}, {lon}, '{name}');"
                self.web_view.page().runJavaScript(js_code)
            
            
            self.statusBar().showMessage(f"📍 {loc['display_name']}")
            
            # Fetch Weather
            location_name = loc.get('display_name', "Current Location")
            # Extract city if possible to keep it short
            if ',' in location_name:
                short_name = location_name.split(',')[0]
            else:
                short_name = location_name
                
            self.weather_widget.fetch_weather(lat, lon, short_name)
        else:
             self.statusBar().showMessage("⚠️ Location undetected.")
            
    def enable_map_pick_mode(self, row_widget):
        self.pending_input_widget = row_widget
        self.statusBar().showMessage("🖱️ Click map to select...")
        
    def handle_map_click(self, lat, lng):
        if not self.pending_input_widget:
            return
            
        self.statusBar().showMessage("✨ Resolving address...")
        self.geo_worker = ReverseGeocodeWorker(lat, lng)
        self.geo_worker.result_ready.connect(self.finish_map_pick)
        self.geo_worker.start()
        
    def finish_map_pick(self, name, lat, lng):
        if self.pending_input_widget:
            self.pending_input_widget.set_text(name)
            js_code = f"updateLocation({lat}, {lng}, '{name.replace('\'', '\\\'')}');"
            self.web_view.page().runJavaScript(js_code)
            
            # Update weather for picked location
            # Use short name
            short_name = name.split(',')[0] if ',' in name else name
            self.weather_widget.fetch_weather(lat, lng, short_name)
            
            self.statusBar().showMessage(f"✅ {name}")
            self.pending_input_widget = None
