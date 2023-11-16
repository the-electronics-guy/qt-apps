from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys
import io
from gmplot import gmplot


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SigTrack')
        self.setGeometry(100, 100, 1300, 500)
        self.UiComponents()
        self.show()

    def UiComponents(self):
        # Dock widget for the map
        dock_map = QtWidgets.QDockWidget("Map", self)
        dock_map.setMinimumSize(QtCore.QSize(300, 300))  # Adjust size as needed



        gmap = gmplot.GoogleMapPlotter(5.5940013,-0.1751592, 16, map_type='SATELLITE')
        gmap.apikey = "AIzaSyDkw3a_XLgmpbUFB1yuuNj3o5cFlhP7HCo"

        map_html = gmap.get()

        # Display the map with QWebEngineView
        web_view = QtWebEngineWidgets.QWebEngineView()
        web_view.setHtml(map_html)
        dock_map.setWidget(web_view)

        # Add the dock widgets to the main window
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_map)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
