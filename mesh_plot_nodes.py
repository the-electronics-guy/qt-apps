from PySide6 import QtCore, QtWidgets, QtWebEngineWidgets
from gmplot import gmplot
import meshtastic
import meshtastic.serial_interface
import sys

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

        # Retrieve a list of available nodes and their IDs
        interface = meshtastic.serial_interface.SerialInterface()
        node_ids = list(interface.nodes.keys())

        # Check if there are any nodes in the network
        if not node_ids:
            print("No nodes found in the mesh network.")
        else:
            # Create a gmplot GoogleMapPlotter instance
            gmap = gmplot.GoogleMapPlotter(5.5900066, -0.1589106, 18)
            gmap.apikey = "AIzaSyDkw3a_XLgmpbUFB1yuuNj3o5cFlhP7HCo"  

            # Add markers for each node
            for node_id in node_ids:
                if node_id in interface.nodes:
                    current_node = interface.nodes[node_id]
                    position_data = current_node.get("position", {})

                    latitude = position_data.get("latitude")
                    longitude = position_data.get("longitude")
                    user_info = current_node.get("user", {})
                    short_name = user_info.get("shortName")

                    if latitude is not None and longitude is not None:
                        # Add a marker for each node with its respective coordinates
                        gmap.marker(latitude, longitude,
                                    color='blue',
                                    title=f'Node {short_name}',
                                    draggable=False,
                                    info_window=f"Node {short_name}")
                    else:
                        print(f"No position information available for node with ID '{node_id}'")
                else:
                    print(f"Node with ID '{node_id}' not found in the mesh network.")

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
    app.exec()
