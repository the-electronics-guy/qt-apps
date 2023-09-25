import sys
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtGui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
import io
from gmplot import gmplot

class MapWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(1300, 500))
        self.setWindowTitle('Map')

        # Create a central widget for the main layout
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a horizontal layout to split the window into two parts
        layout = QtWidgets.QHBoxLayout(central_widget)

        # Create the left widget with three push buttons
        left_widget = QtWidgets.QWidget(self)
        left_widget.setMinimumWidth(200)
        left_widget.setMaximumWidth(220)
        layout.addWidget(left_widget)

        # Create a vertical layout for the left widget
        left_layout = QtWidgets.QVBoxLayout(left_widget)

        # Create three push buttons for the left widget
        button1 = QtWidgets.QPushButton("Show Markers")
        button1.clicked.connect(self.show_markers)  # Connect button click to show_markers method
        button2 = QtWidgets.QPushButton("Button 2")
        button3 = QtWidgets.QPushButton("Button 3")

        left_layout.addWidget(button1)
        left_layout.addWidget(button2)
        left_layout.addWidget(button3)

        # Create the right widget (80% of the window) to display a map
        right_widget = QtWidgets.QWidget(self)
        layout.addWidget(right_widget)
        layout.setStretch(1, 4)  # Right widget covers 80% of the window

        # Create a layout for the right widget
        right_layout = QtWidgets.QVBoxLayout(right_widget)

        # Create a gmplot GoogleMapPlotter instance
        self.gmap = gmplot.GoogleMapPlotter(5.5988617, -0.2265554, 18)

        self.gmap.apikey = "AIzaSyDkw3a_XLgmpbUFB1yuuNj3o5cFlhP7HCo"  # Replace with your API key

        # List of custom marker parameters
        custom_markers = [
            (5.5952954, -0.2237016, 'qt icons/4026454_device_drone_electronic_machine_technology_icon.png', 'Starting Point', True, "Starting Point"),
            (5.5999059, -0.2286033,'qt icons/4026454_device_drone_electronic_machine_technology_icon.png', 'Destination Point', True, "Destination Point")
        ]

        # Add custom markers using the list when the map loads
        for marker_params in custom_markers:
            self.add_custom_marker(*marker_params)

        # Get the HTML content from gmplot
        map_html = self.gmap.get()

        # Display the map with QWebEngineView
        self.web_view = QtWebEngineWidgets.QWebEngineView()
        self.web_view.setHtml(map_html)

        right_layout.addWidget(self.web_view)

    def add_custom_marker(self, lat, lng, custom_marker_path, title, draggable, info_window):
        # Create a marker with custom icon using QIcon
        icon = QtGui.QIcon(custom_marker_path)
        marker = QtWebEngineWidgets.QWebEngineView(self.web_view)
        marker.setHtml('<img src="data:image/png;base64,{}"/>'.format(icon.pixmap(32).toImage().toBase64()))
        marker.page().runJavaScript("new google.maps.InfoWindow({content: '{}'});".format(info_window))
        marker.page().runJavaScript("new google.maps.Marker({position: new google.maps.LatLng({}, {}), map: map, icon: '{}'});".format(lat, lng, icon.pixmap(32).toImage().toBase64()))
        marker.resize(32, 32)
        self.web_view.page().mainFrame().addToJavaScriptWindowObject("marker", marker)

 #   def show_markers(self):
#        pass
        #No need to change this method; markers are already displayed when the map loads

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    map_window = MapWindow()
    map_window.show()
    sys.exit(app.exec_())
