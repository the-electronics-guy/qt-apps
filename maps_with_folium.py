import sys
from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
import io
import folium

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

        # Create the Folium map and display it using QWebEngineView
        coordinate = (5.5988617, -0.2265554)
        m = folium.Map(
            tiles='OpenStreetMap',
            zoom_start=15,
            location=coordinate,
        )
        #Add map tiles
        folium.TileLayer('stamenterrain', attr='stamenterrain').add_to(m)
        folium.TileLayer('stamenwatercolor', attr='stamenwatercolor').add_to(m)
        folium.LayerControl().add_to(m)


        # draw a circle
        #folium.Circle(radius=700,
        #              location=[5.5961405, -0.2260515],
        #              tooltip="circle",
        #              fill=True
        #              ).add_to(m)

        #Add markers on the map
        folium.Marker(location=[5.5952954,-0.2237016],
                      icon=folium.Icon(icon="glyphicon-star", color='red'),
                      tooltip='Red team'
                      ).add_to(m)

        folium.Marker(location=[5.5935851,-0.2235987],
                      icon=folium.Icon(icon="glyphicon-flag", color='blue'),
                      tooltip='Blue Team'
                      ).add_to(m)

        folium.Marker(location=[5.5999059,-0.2286033],
                      icon=folium.Icon(icon="glyphicon-user", color='green'),
                      tooltip='Green Team'
                      ).add_to(m)

        # Save map data to a data object
        data = io.BytesIO()
        m.save(data, close_file=False)

        # Display the map with QWebEngineView
        web_view = QtWebEngineWidgets.QWebEngineView()
        web_view.setHtml(data.getvalue().decode())

        right_layout.addWidget(web_view)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    map_window = MapWindow()
    map_window.show()
    sys.exit(app.exec_())
