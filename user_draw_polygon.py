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
        self.marker_coordinates = []  # List to store marker coordinates

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

        # Connect button1 to a slot method
        button1.clicked.connect(self.draw_lines_between_markers)

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
        self.gmap = gmplot.GoogleMapPlotter(5.5988617, -0.2265554, 15, map_type='SATELLITE')
        self.gmap.apikey = "AIzaSyDkw3a_XLgmpbUFB1yuuNj3o5cFlhP7HCo"

        # text
        self.gmap.text(5.5988617, -0.2265554, 'sigtrack')

        # Add markers or other map elements using gmplot methods

        # static marker
        self.gmap.marker(5.5952954, -0.2237016,
                    color='red',
                    title='Red team',
                    draggable=True,
                    info_window="Red team")
        self.gmap.marker(5.5935851, -0.2235987,
                    'blue',
                    title='Blue Team',
                    draggable=True,
                    info_window="Blue team")
        self.gmap.marker(5.5999059, -0.2286033,
                    'green',
                    title='Green Team',
                    draggable=True,
                    info_window="Green Team")

        # Store the coordinates of the markers in the self.marker_coordinates list
        #self.marker_coordinates.append((5.597812,  -0.225461))
        #self.marker_coordinates.append((5.597021,  -0.224367))
        #self.marker_coordinates.append((5.596071,  -0.222404))
        self.marker_coordinates.append((5.605697,  -0.231373))
        self.marker_coordinates.append((5.6016609, -0.2393982))
        self.marker_coordinates.append((5.5935851, -0.2235987))
        self.marker_coordinates.append((5.5908486, -0.2350852))

        # dynamic marker
        self.gmap.enable_marker_dropping('orange')

        # Get the HTML content from gmplot
        map_html = self.gmap.get()

        # Display the map with QWebEngineView
        self.web_view = QtWebEngineWidgets.QWebEngineView()
        self.web_view.setHtml(map_html)

        right_layout.addWidget(self.web_view)

    def draw_lines_between_markers(self):
        if len(self.marker_coordinates) >= 2:
            # Clear the existing markers and lines
            self.gmap.marker_lats = []
            self.gmap.marker_lngs = []
            self.gmap.lines = []

            # Scatter and plot new markers and lines
            self.gmap.scatter(
                [coord[0] for coord in self.marker_coordinates],
                [coord[1] for coord in self.marker_coordinates],
                'blue',
                size=40,
                marker=True
            )
            self.gmap.polygon(
                [coord[0] for coord in self.marker_coordinates],
                [coord[1] for coord in self.marker_coordinates],
                'black',
                edge_width=3.5
            )

            # Update the map
            map_html = self.gmap.get()
            self.web_view.setHtml(map_html)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    map_window = MapWindow()
    map_window.show()
    sys.exit(app.exec_())
