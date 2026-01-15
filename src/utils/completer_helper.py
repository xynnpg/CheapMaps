from PyQt5.QtWidgets import QCompleter, QListView
from PyQt5.QtCore import Qt, QObject, QTimer, pyqtSignal, QStringListModel, QThread
import requests

class CompleterWorker(QThread):
    suggestions_ready = pyqtSignal(list, str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': self.query,
            'format': 'json',
            'addressdetails': 1,
            'limit': 5
        }
        headers = {'User-Agent': 'ProiectLogis_MapApp/1.0'}
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                suggestions = [item['display_name'] for item in data]
                self.suggestions_ready.emit(suggestions, self.query)
        except Exception as e:
            print(f"Worker Error: {e}")

class LocationCompleter(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        
        popup = QListView()
        self.completer.setPopup(popup)
        
        self.model = QStringListModel()
        self.completer.setModel(self.model)
        
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.start_worker)
        
        self.current_text = ""
        self.cache = {}
        self.current_worker = None
        
    def update_text(self, text):
        if len(text) < 3:
            return 
        self.current_text = text
        self.timer.start()
        
    def start_worker(self):
        query = self.current_text
        if query in self.cache:
            self.model.setStringList(self.cache[query])
            return
            
        self.current_worker = CompleterWorker(query)
        self.current_worker.suggestions_ready.connect(self.handle_results)
        self.current_worker.start()
        
    def handle_results(self, suggestions, query):
        self.cache[query] = suggestions
        self.model.setStringList(suggestions)
