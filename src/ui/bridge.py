from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class MapBridge(QObject):
    mapClickedSignal = pyqtSignal(float, float)
    routeSelectedSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    @pyqtSlot(float, float)
    def mapClicked(self, lat, lng):
        self.mapClickedSignal.emit(lat, lng)

    @pyqtSlot(int)
    def routeSelected(self, index):
        print(f"Route selected: {index}")
        self.routeSelectedSignal.emit(index)
