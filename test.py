from PySide6.QtWebEngineWidgets import QWebEngineView
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout,
                               QPushButton, QHBoxLayout, QListWidget, QLineEdit, QToolButton,
                               QToolBar, QLabel, QTabWidget,
                               QTableWidget, QRadioButton, QCheckBox,
                               QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QGridLayout
                               )
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
import folium
from folium.plugins import Draw
import meshtastic.serial_interface
from PySide6.QtCore import Signal
from pubsub import pub
import os
from qt_material import apply_stylesheet

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


class MapDisplay(QMainWindow):
    def __init__(self, icon_filenames):
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

        # Peers button
        self.page2_button = self.create_tool_button("qt icons/plus_icon.ico", "New")
        self.page2_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.page2_button.setToolTip("New Device")
        self.page2_button.clicked.connect(self.show_page2)
        self.toolbar.addWidget(self.page2_button)

        # Symbol button
        self.symbol_button = self.create_tool_button("qt icons/box_icon.svg", "Symbols")
        self.symbol_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.symbol_button.setToolTip("Symbols")
        self.symbol_button.clicked.connect(self.show_symbol_manager)
        self.toolbar.addWidget(self.symbol_button)

        # Peers button
        self.peers_button = self.create_tool_button("qt icons/people_icon.svg", "Peers")
        self.peers_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.peers_button.setToolTip("Peers")
        self.peers_button.clicked.connect(self.show_peers)
        self.toolbar.addWidget(self.peers_button)

        # Toggle dock button
        self.toggle_dock_button = QToolButton()
        self.toggle_dock_button.setIcon(QIcon("qt icons/toggle_icon.svg"))
        self.toggle_dock_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.toggle_dock_button.setToolTip("Toggle Dock Widget")
        self.toggle_dock_button.clicked.connect(self.toggle_dock_widget)
        self.toolbar.addWidget(self.toggle_dock_button)

        # Create the map
        #attr = (
        #    'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'

        #)
        #tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

        self.m = folium.Map([5.590039, -0.156270], zoom_start=14).add_child(
            folium.ClickForMarker(popup="Select Icon"))

        draw = Draw(export=True)
        draw.add_to(self.m)
        folium.LatLngPopup().add_to(self.m)
        #folium.TileLayer('openstreetmap').add_to(self.m)
        #folium.TileLayer('mapquestopen').add_to(self.m)2
        folium.TileLayer(
            'MapQuest Open Aerial',
            attr="'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'").add_to(self.m)


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

        # Create a dock widget for stacking interfaces
        self.dock_widget = QDockWidget("Interfaces", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        self.icon_filenames = icon_filenames

        self.dock_widget.hide()

        self.symbol_manager = SymbolManager()
        self.symbol_manager.image_clicked.connect(self.add_custom_marker)

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

    def show_page2(self):
        self.page2 = Page2()
        self.dock_widget.setWidget(self.page2)

    def show_symbol_manager(self):
        self.symbol_manager = SymbolManager()
        self.dock_widget.setWidget(self.symbol_manager)

    def show_peers(self):
        self.peer_table = Peers(self)
        self.dock_widget.setWidget(self.peer_table)


class Page2(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout for page 2
        self.main_layout = QVBoxLayout(self)
        self.label = QLabel("This is Page 2")
        self.main_layout.addWidget(self.label)


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

class SymbolManager(QWidget):
    image_clicked = Signal(QPixmap)

    def __init__(self):
        super().__init__()
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Images")
        self.layout = QGridLayout()
        self.layout.addWidget(self.tree_widget)
        self.setLayout(self.layout)

        self.populate_tree()

        # Connect the itemClicked signal to the slot
        self.tree_widget.itemClicked.connect(self.handle_item_clicked)

    def populate_tree(self):
        main_folder = "Nato Icons"

        for root, dirs, files in os.walk(main_folder):
            parent_item = QTreeWidgetItem(self.tree_widget, [os.path.basename(root)])
            self.tree_widget.addTopLevelItem(parent_item)

            for file in files:
                if file.endswith(".jpg") or file.endswith(".png"):
                    child_item = QTreeWidgetItem(parent_item)
                    parent_item.addChild(child_item)
                    image_path = os.path.join(root, file)
                    pixmap = QPixmap(image_path)
                    icon = pixmap.scaled(100, 100)
                    child_item.setIcon(0, icon)
                    child_item.setToolTip(0, file)

    def handle_item_clicked(self, item, column):
        # Emit the image_clicked signal with the pixmap of the clicked item
        icon = item.icon(column)
        self.image_clicked.emit(icon.pixmap(icon.availableSizes()[0]))




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapDisplay(["airborne.png", "icon2.png"])
    #apply_stylesheet(app, theme='light_teal.xml')
    apply_stylesheet(app, theme='dark_blue.xml')

    window.show()
    sys.exit(app.exec())







