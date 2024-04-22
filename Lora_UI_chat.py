import sys
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QFont
from PySide6.QtWebEngineWidgets import QWebEngineView
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget,
                               QWidget, QVBoxLayout,
                               QPushButton, QHBoxLayout,
                               QListWidget, QLineEdit, QToolButton,
                               QToolBar, QLabel, QTabWidget,
                               QTableWidget, QRadioButton,
                               QTableWidgetItem,  QGridLayout, QScrollArea
                               )
from PySide6.QtGui import QIcon, QPixmap
import folium
from folium.plugins import Draw
import meshtastic.serial_interface
from PySide6.QtCore import Signal
from pubsub import pub
import os
from qt_material import apply_stylesheet
from datetime import datetime

interface = meshtastic.serial_interface.SerialInterface()


class MeshtasticChatInterface(QWidget):
    def __init__(self, interface):
        super().__init__()
        self.interface = interface

        # Main layout for the chat interface
        self.main_layout = QHBoxLayout(self)

        # Left layout for radio buttons
        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)

        # Right layout for chat display and message input
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.right_layout)

        # Create radio buttons
        self.create_radio_buttons()

        # Chat display
        self.chat_display = QListWidget()
        self.right_layout.addWidget(self.chat_display)

        # Message input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        self.right_layout.addLayout(input_layout)

        # Subscribe to message reception events
        pub.subscribe(self.on_receive_message, "meshtastic.receive")

        # Broadcast icon button
        self.broadcast_icon = QRadioButton()
        self.broadcast_icon.setIcon(QIcon("qt icons/broadcast_line_icon.svg"))
        self.broadcast_icon.setToolTip("Broadcast")
        self.left_layout.addWidget(self.broadcast_icon)

        # Store the selected node ID
        self.selected_node_id = None

    def send_message(self):
        message = self.message_input.text()

        if self.broadcast_icon.isChecked():
            self.interface.sendText(message)
            self.chat_display.addItem(f"Broadcast message: {message}")
        elif self.selected_node_id:
            # Get the short name of the selected node
            short_name = self.find_short_name_by_node_id(self.selected_node_id)
            # Send the message to the selected node using its short name
            self.interface.sendText(message, destinationId=self.selected_node_id)
            self.chat_display.addItem(f"Direct message to {short_name}: {message}")
        else:
            self.chat_display.addItem("No node selected. Cannot send message.")

        self.message_input.clear()

    def on_receive_message(self, packet):
        print("Received packet:", packet)  # Print the packet contents for debugging

        sender_id = packet.get('fromId')  # Get the sender's ID from the packet
        if sender_id:
            sender_name = self.find_short_name_by_node_id(sender_id)
        else:
            sender_name = 'Unknown'
        if packet['decoded']['text']:
            message_text = packet['decoded']['text']
            self.chat_display.addItem(f"{sender_name}: {message_text}")
        else:
            self.chat_display.addItem(f"Received packet with no text content: {packet}")


    def find_short_name_by_node_id(self, node_id):
        # Retrieve the short name of the node associated with the given node ID
        node_info = self.interface.nodes.get(node_id)
        if node_info:
            user_info = node_info.get("user", {})
            return user_info.get("shortName", "Unknown")
        return "Unknown"

    def create_radio_buttons(self):
        # Check if there are any nodes in the network
        self.node_ids = list(self.interface.nodes.keys())
        if not self.node_ids:
            print("No nodes found in the mesh network.")
        else:
            # Iterate through all available nodes
            for node_id in self.node_ids:
                if node_id in self.interface.nodes:
                    current_node = self.interface.nodes[node_id]

                    # Get short name of the radio associated with the node
                    user_info = current_node.get("user", {})
                    short_name = user_info.get("shortName", "Unknown")

                    # Create a QRadioButton for each node
                    radio_button = QRadioButton(short_name, parent=self)
                    radio_button.clicked.connect(self.handle_radio_button_clicked)

                    self.left_layout.addWidget(radio_button)

                else:
                    print(f"Node with ID '{node_id}' not found in the mesh network.")

    def handle_radio_button_clicked(self):
        # Get the text of the radio button that was clicked
        sender = self.sender()
        radio_button_text = sender.text()

        # Assuming the radio button text is the short name, find its corresponding node ID
        self.selected_node_id = self.find_node_id_by_short_name(radio_button_text)
        self.chat_display.clear()

    def find_node_id_by_short_name(self, short_name):
        for node_id, node_info in self.interface.nodes.items():
            user_info = node_info.get("user", {})
            if user_info.get("shortName") == short_name:
                return node_id
        return None



class SymbolManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Choose an Image")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.images_root = "Nato Icons"

        self.load_images()

    def load_images(self):
        subfolders = [folder for folder in os.listdir(self.images_root) if
                      os.path.isdir(os.path.join(self.images_root, folder))]

        for folder in subfolders:
            image_layout = QGridLayout()
            tab = QWidget()
            tab.setLayout(image_layout)

            images_folder = os.path.join(self.images_root, folder)
            images = [os.path.join(images_folder, img) for img in os.listdir(images_folder) if img.endswith(".png")]

            row = 0
            col = 0
            for img_path in images:
                pixmap = QPixmap(img_path)
                label = QLabel()
                label.setPixmap(pixmap)
                label.mousePressEvent = lambda event, img=img_path: self.image_clicked(img)
                image_layout.addWidget(label, row, col)
                col += 1
                if col == 6:
                    col = 0
                    row += 1

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(tab)

            self.tab_widget.addTab(scroll_area, folder)

    def image_clicked(self, img_path):
        self.selected_image = img_path
        self.accept()


class VesselTracking(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vessel Tracking")
        self.setGeometry(100, 100, 800, 600)

        # Create a QWebEngineView to display the Vessel Finder map
        self.web_view = QWebEngineView()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)

        # Load the Vessel Finder map
        self.load_vessel_finder_map()

    def load_vessel_finder_map(self):
        # Load the Vessel Finder map HTML content
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Vessels</title>
        </head>
        <body>
        <script type="text/javascript">
            // Map appearance
            var width="100%";         // width in pixels or percentage
            var height="700";         // height in pixels
            var latitude="36.00";     // center latitude (decimal degrees)
            var longitude="-5.40";    // center longitude (decimal degrees)
            var names=true;           // always show ship names (defaults to false)

            // Fleet tracking
            var fleet="1e58b2abd5a74f781d3e452e2c2876c7"; // your personal Fleet key (displayed in your User Profile)
            var fleet_name="Carnival"; // display particular fleet from your fleet list
            var fleet_timespan="1440"; // maximum age in minutes of the displayed ship positions
        </script>
        <script type="text/javascript" src="https://www.vesselfinder.com/aismap.js"></script>
        </body>
        </html>
        """
        # Set the HTML content to the QWebEngineView
        self.web_view.setHtml(html_content, QUrl("https://www.vesselfinder.com/"))


class MapDisplay(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Map Application")
        self.setGeometry(100, 100, 800, 600)

        self.node_ids = list(interface.nodes.keys())

        # Create a transparent vertical toolbar on the left side
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setMovable(True)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        # Chat button
        self.chat_button = QToolButton()
        self.chat_button.setIcon(QIcon("qt icons/message_icon.ico"))
        self.chat_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.chat_button.setToolTip("Message")
        self.chat_button.clicked.connect(self.show_chat_interface)
        self.toolbar.addWidget(self.chat_button)

        # Symbol
        self.symbol_button = QToolButton()
        self.symbol_button.setIcon(QIcon("qt icons/box_icon.svg"))
        self.symbol_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.symbol_button.setToolTip("Add Symbol")
        self.symbol_button.clicked.connect(self.show_symbols)
        self.toolbar.addWidget(self.symbol_button)

        # Peers button
        self.peers_button = self.create_tool_button("qt icons/people_icon.svg", "Peers")
        self.peers_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.peers_button.setToolTip("Peers")
        self.peers_button.clicked.connect(self.show_peers)
        self.toolbar.addWidget(self.peers_button)

        # Weather button
        self.weather_button = self.create_tool_button("qt icons/weather_icon.svg", "Weather")
        self.weather_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.weather_button.setToolTip("Weather")
        self.weather_button.clicked.connect(self.show_weather)
        self.toolbar.addWidget(self.weather_button)

        # ship button
        self.ship_button = self.create_tool_button("qt icons/ship.svg", "Vessels")
        self.ship_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.ship_button.setToolTip("Track Vessels")
        self.ship_button.clicked.connect(self.show_vessel_tracking)
        self.toolbar.addWidget(self.ship_button)

        # Toggle dock button
        self.toggle_dock_button = QToolButton()
        self.toggle_dock_button.setIcon(QIcon("qt icons/toggle_icon.svg"))
        self.toggle_dock_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.toggle_dock_button.setToolTip("Toggle Dock Widget")
        self.toggle_dock_button.clicked.connect(self.toggle_dock_widget)
        self.toolbar.addWidget(self.toggle_dock_button)

        # Create the map
        self.m = folium.Map([5.590039, -0.156270], zoom_start=14).add_child(
            folium.ClickForMarker(popup="Select Icon"))

        draw = Draw(export=True)
        draw.add_to(self.m)
        folium.LatLngPopup().add_to(self.m)

        if not self.node_ids:
            print("No nodes found in the mesh network.")
        else:
            for node_id in self.node_ids:
                if node_id in interface.nodes:
                    current_node = interface.nodes[node_id]
                    position_data = current_node.get("position", {})

                    latitude = position_data.get("latitude")
                    longitude = position_data.get("longitude")
                    user_info = current_node.get("user", {})
                    short_name = user_info.get("shortName")

                    if latitude is not None and longitude is not None:


                        # Add a marker for each node with its respective coordinates
                        icon_node = folium.CustomIcon(icon_image='tbeam_nodes.png', icon_size=(30, 45))
                        folium.Marker([latitude, longitude], popup=f'Node {short_name}', icon=icon_node).add_to(self.m)
                    else:
                        print(f"No position information available for node with ID '{node_id}'")
                else:
                    print(f"Node with ID '{node_id}' not found in the mesh network.")

        folium.LayerControl().add_to(self.m)
        # Save the map
        self.map_html = "map_test_bench.html"
        self.m.save(self.map_html)

        # Display the map with QWebEngineView
        self.web_view = QWebEngineView()
        self.web_view.setHtml(open(self.map_html, 'r').read())
        self.setCentralWidget(self.web_view)

        # Add Weather Widget
        self.weather_widget = WeatherApp()
        self.weather_widget.move(200, 500)  # Move to desired position
        self.weather_widget.hide()

        # Create a dock widget for stacking interfaces
        self.dock_widget = QDockWidget(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        self.dock_widget.hide()

    def show_vessel_tracking(self):
        self.vessel_tracking = VesselTracking()
        self.setCentralWidget(self.vessel_tracking)


    def add_custom_marker(self, icon):
        # Add a custom marker to the map
        latitude, longitude = 5.590039, -0.156270  # Example coordinates, replace with actual coordinates
        custom_icon = folium.CustomIcon(icon)
        folium.Marker([latitude, longitude], popup="Custom Marker", icon=custom_icon).add_to(self.m)
        # Update the HTML file to reflect changes
        self.m.save(self.map_html)
        # Reload the map in the QWebEngineView
        self.web_view.setHtml(open(self.map_html, 'r').read())



    def toggle_dock_widget(self):
        if self.dock_widget.isHidden():
            self.dock_widget.show()
        else:
            self.dock_widget.hide()


    def create_tool_button(self, icon_path, text):
        button = QToolButton()
        button.setIcon(QIcon(icon_path))
        button.setText(text)
        button.setIconSize(QSize(50, 50))
        button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        return button

    def show_chat_interface(self):
        self.chat_interface = MeshtasticChatInterface(interface)
        self.dock_widget.setWidget(self.chat_interface)

    def show_peers(self):
        self.peer_table = Peers(self)
        self.dock_widget.setWidget(self.peer_table)

    def show_symbols(self):
        self.symbol_manager = SymbolManager(self)
        self.dock_widget.setWidget(self.symbol_manager)

    def show_weather(self):
        self.weather_info = WeatherApp()
        self.dock_widget.setWidget(self.weather_info)


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")

        self.setStyleSheet("background-color: #f0f0f0;")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.cityName = "Accra"
        self.api_key = 'd2ed8137acc17a02bcd284b4548d5b88'
        self.BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

        self.weather_label = QLabel()
        self.weather_label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.weather_label)

        self.weather_icon_label = QLabel()
        self.layout.addWidget(self.weather_icon_label)

        temperature_layout = QHBoxLayout()
        self.layout.addLayout(temperature_layout)

        temperature_icon = QLabel()
        temperature_icon.setPixmap(QPixmap("qt icons/temperature_icon.svg").scaled(30, 30))
        temperature_layout.addWidget(temperature_icon)

        self.temperature_label = QLabel()
        temperature_layout.addWidget(self.temperature_label)

        humidity_layout = QHBoxLayout()
        self.layout.addLayout(humidity_layout)

        humidity_icon = QLabel()
        humidity_icon.setPixmap(QPixmap("qt icons/humidity_icon.svg").scaled(30, 30))
        humidity_layout.addWidget(humidity_icon)

        self.humidity_label = QLabel()
        humidity_layout.addWidget(self.humidity_label)

        wind_speed_layout = QHBoxLayout()
        self.layout.addLayout(wind_speed_layout)

        wind_icon = QLabel()
        wind_icon.setPixmap(QPixmap("qt icons/wind_speed_icon.svg").scaled(30, 30))
        wind_speed_layout.addWidget(wind_icon)

        self.wind_speed_label = QLabel()
        wind_speed_layout.addWidget(self.wind_speed_label)

        pressure_layout = QHBoxLayout()
        self.layout.addLayout(pressure_layout)

        pressure_icon = QLabel()
        pressure_icon.setPixmap(QPixmap("qt icons/air_pressure.svg").scaled(30, 30))
        pressure_layout.addWidget(pressure_icon)

        self.pressure_label = QLabel()
        pressure_layout.addWidget(self.pressure_label)

        sea_level_layout = QHBoxLayout()
        self.layout.addLayout(sea_level_layout)

        sea_level_icon = QLabel()
        sea_level_icon.setPixmap(QPixmap("qt icons/sea-level.svg").scaled(30, 30))
        sea_level_layout.addWidget(sea_level_icon)

        self.sea_level_label = QLabel()
        sea_level_layout.addWidget(self.sea_level_label)

        ground_level_layout = QHBoxLayout()
        self.layout.addLayout(ground_level_layout)

        ground_level_icon = QLabel()
        ground_level_icon.setPixmap(QPixmap("qt icons/sea-level.svg").scaled(30, 30))
        ground_level_layout.addWidget(ground_level_icon)

        self.ground_level_label = QLabel()
        ground_level_layout.addWidget(self.ground_level_label)

        visibility_layout = QHBoxLayout()
        self.layout.addLayout(visibility_layout)

        visibility_icon = QLabel()
        visibility_icon.setPixmap(QPixmap("qt icons/visibility.svg").scaled(30, 30))
        visibility_layout.addWidget(visibility_icon)

        self.visibility_label = QLabel()
        visibility_layout.addWidget(self.visibility_label)

        gust_layout = QHBoxLayout()
        self.layout.addLayout(gust_layout)

        gust_icon = QLabel()
        gust_icon.setPixmap(QPixmap("qt icons/gust.svg").scaled(30, 30))
        gust_layout.addWidget(gust_icon)

        self.gust_label = QLabel()
        gust_layout.addWidget(self.gust_label)

        clouds_layout = QHBoxLayout()
        self.layout.addLayout(clouds_layout)

        clouds_icon = QLabel()
        clouds_icon.setPixmap(QPixmap("qt icons/weather_icon.svg").scaled(30, 30))
        clouds_layout.addWidget(clouds_icon)

        self.clouds_label = QLabel()
        clouds_layout.addWidget(self.clouds_label)

        country_layout = QHBoxLayout()
        self.layout.addLayout(country_layout)

        country_icon = QLabel()
        country_icon.setPixmap(QPixmap("qt icons/country-flag.svg").scaled(30, 30))
        country_layout.addWidget(country_icon)

        self.country_label = QLabel()
        country_layout.addWidget(self.country_label)

        sunrise_layout = QHBoxLayout()
        self.layout.addLayout(sunrise_layout)

        sunrise_icon = QLabel()
        sunrise_icon.setPixmap(QPixmap("qt icons/sunrise.svg").scaled(30, 30))
        sunrise_layout.addWidget(sunrise_icon)

        self.sunrise_label = QLabel()
        sunrise_layout.addWidget(self.sunrise_label)

        sunset_layout = QHBoxLayout()
        self.layout.addLayout(sunset_layout)

        sunset_icon = QLabel()
        sunset_icon.setPixmap(QPixmap("qt icons/sunset.svg").scaled(30, 30))
        sunset_layout.addWidget(sunset_icon)

        self.sunset_label = QLabel()
        sunset_layout.addWidget(self.sunset_label)

        self.refresh_button = QPushButton("Refresh Weather")
        self.refresh_button.clicked.connect(self.refresh_weather)
        self.layout.addWidget(self.refresh_button)

        self.refresh_weather()

    def refresh_weather(self):
        self.refresh_button.setEnabled(False)
        try:
            url = f"{self.BASE_URL}?q={self.cityName}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            pressure = data['main']['pressure']
            sea_level = data['main'].get('sea_level', 'N/A')
            ground_level = data['main'].get('grnd_level', 'N/A')
            visibility = data.get('visibility', 'N/A')
            gust = data['wind'].get('gust', 'N/A')
            clouds = data['clouds']['all']
            country = data['sys']['country']
            sunrise = data['sys']['sunrise']
            sunset = data['sys']['sunset']

            icon_name = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_name}.png"
            icon_data = requests.get(icon_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data)

            weather_report = f"Weather: {weather_description}"
            self.weather_label.setText(weather_report)
            self.weather_icon_label.setPixmap(pixmap)

            self.temperature_label.setText(f"{temperature}°C")
            self.humidity_label.setText(f"{humidity}%")
            self.wind_speed_label.setText(f"{wind_speed} m/s")
            self.pressure_label.setText(f"{pressure} hPa")
            self.sea_level_label.setText(f"{sea_level} m")
            self.ground_level_label.setText(f"{ground_level} m")
            self.visibility_label.setText(f"{visibility} meters")
            self.gust_label.setText(f"{gust} m/s")
            self.clouds_label.setText(f"{clouds}%")
            self.country_label.setText(f"{country}")
            self.sunrise_label.setText(f"{datetime.utcfromtimestamp(sunrise).strftime('%Y-%m-%d %H:%M:%S')}")
            self.sunset_label.setText(f"{datetime.utcfromtimestamp(sunset).strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.refresh_button.setEnabled(True)


class Peers(QWidget):
    def __init__(self, interface):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        # Create the table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # Adjust the number of columns as needed
        self.table_widget.setHorizontalHeaderLabels(["Name", "Model", "Mac Address", "Last Heard", "SNR", "Battery Level"])

        # Populate the table with node information
        self.populate_table()

        # Add the table widget to the layout
        self.main_layout.addWidget(self.table_widget)

        # Set the layout for the widget
        self.setLayout(self.main_layout)

    def populate_table(self):
        if not interface.nodes:
            print("No nodes found in the mesh network.")
        else:
            # Iterate through each node
            for node_id, node_info in interface.nodes.items():
                # Extract node information
                user_info = node_info.get("user", {})
                long_name = user_info.get("longName", "")
                model = user_info.get("hwModel", "")
                mac_address = user_info.get("macaddr", "")
                last_heard = str(node_info.get("lastHeard", ""))
                snr = str(node_info.get("snr", ""))
                battery_level = str(node_info.get("deviceMetrics", {}).get("batteryLevel", ""))

                # Insert a new row in the table and set item data
                row_position = self.table_widget.rowCount()
                self.table_widget.insertRow(row_position)
                self.table_widget.setItem(row_position, 0, QTableWidgetItem(long_name))
                self.table_widget.setItem(row_position, 1, QTableWidgetItem(model))
                self.table_widget.setItem(row_position, 2, QTableWidgetItem(mac_address))
                self.table_widget.setItem(row_position, 3, QTableWidgetItem(last_heard))
                self.table_widget.setItem(row_position, 4, QTableWidgetItem(snr))
                self.table_widget.setItem(row_position, 5, QTableWidgetItem(battery_level))

        # Remove row numbers
        self.table_widget.verticalHeader().setVisible(False)

        # Set style for the table widget
        self.table_widget.setStyleSheet(
            """
            QTableWidget {
                gridline-color: transparent;
                border: none;
                font-size: inherit;
                font-weight: inherit;
            }
            """
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapDisplay()
    apply_stylesheet(app, theme='light_teal.xml')
    #apply_stylesheet(app, theme='dark_blue.xml')

    window.show()
    sys.exit(app.exec())







