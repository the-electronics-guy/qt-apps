import sys
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView
import io
from gmplot import gmplot


class MapWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QtCore.QSize(1300, 500))
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
        button1 = QtWidgets.QPushButton("Button 1")
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
        gmap = gmplot.GoogleMapPlotter(5.5988617, -0.2265554, 15)


        gmap.apikey = "AIzaSyDkw3a_XLgmpbUFB1yuuNj3o5cFlhP7HCo"

        # Add markers or other map elements using gmplot methods


        # static marker
        gmap.marker(5.5952954, -0.2237016,
                    color='red',
                    title='Red team',
                    draggable=True,
                    info_window="Red team")
        gmap.marker(5.5935851, -0.2235987,
                    'blue',
                    title='Blue Team',
                    draggable=True,
                    info_window="Blue team")
        gmap.marker(5.5999059, -0.2286033,
                    'green',
                    title='Green Team',
                    draggable=True,
                    info_window="Green Team")

        #dynamic marker
        gmap.enable_marker_dropping('orange')

        # Get the HTML content from gmplot
        map_html = gmap.get()

        # Display the map with QWebEngineView
        web_view = QtWebEngineWidgets.QWebEngineView()
        web_view.setHtml(map_html)

        right_layout.addWidget(web_view)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    map_window = MapWindow()
    map_window.show()
    sys.exit(app.exec_())
