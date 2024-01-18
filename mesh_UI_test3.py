from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget,
    QTextEdit, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QDockWidget,
    QToolBar, QStackedWidget, QComboBox,
    QLabel, QSizePolicy, QToolButton, QCheckBox,
    QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QMdiArea, QMdiSubWindow, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
import sys
import io
from gmplot import gmplot
import serial
from serial.tools.list_ports import comports
import meshtastic
import meshtastic.serial_interface
from pubsub import pub


class MeshtasticThread(QThread):
    message_received = Signal(str)

    def __init__(self, interface):
        super().__init__()
        self.interface = interface

    def run(self):
        try:
            while True:
                self.interface.run_forever()
        except KeyboardInterrupt:
            print("Receive thread interrupted.")


class ChatInterface(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout for the chat interface
        self.main_layout = QHBoxLayout(self)

        # Sidebar layout
        self.sidebar_layout = QHBoxLayout()
        self.toolbar = QToolBar()
        self.stacked_widget = QStackedWidget()
        self.setup_toolbar()
        self.setup_stacked_widget()

        # Add toolbar and stacked widget to sidebar layout
        self.sidebar_layout.addWidget(self.toolbar)
        self.sidebar_layout.addWidget(self.stacked_widget)

        # Chat display
        self.chat_display = QListWidget()

        # Message input area
        self.message_input = QLineEdit()
        self.send_button = QToolButton()
        self.send_button.setIcon(QIcon('qt icons/send_icon.ico'))
        self.send_button.setStyleSheet("border: none;")
        self.send_button.clicked.connect(self.send_message)
        
        self.upload_button = QToolButton()
        self.upload_button.setIcon(QIcon('qt icons/upload_files.ico'))
        self.upload_button.setStyleSheet("border: none;")
        
        # Input layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.upload_button)

        # Chat layout
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(input_layout)

        # Add sidebar and chat layouts to main layout
        self.main_layout.addLayout(self.sidebar_layout, 2.7)
        self.main_layout.addLayout(chat_layout, 2.5)
        
        # Connect to Meshtastic events
        pub.subscribe(self.on_receive_message, "meshtastic.receive")
        pub.subscribe(self.on_connection_established, "meshtastic.connection.established")

        # Start Meshtastic thread
        self.interface = meshtastic.serial_interface.SerialInterface()
        self.meshtastic_thread = MeshtasticThread(self.interface)
        self.meshtastic_thread.message_received.connect(self.on_receive_message)
        self.meshtastic_thread.start()

        
    def on_receive_message(self, packet, interface):
        if packet['decoded']['text']:
            sender_id = packet['from']
            message_text = packet['decoded']['text']
            self.chat_display.addItem(f"Received message from {sender_id}: {message_text}")
        else:
            self.chat_display.addItem(f"Received packet with no text content: {packet}")
    

    def on_connection_established(self, interface, topic=pub.AUTO_TOPIC):
        interface.sendText("Connected to desktop")
        self.chat_display.addItem(f"Node Connected")

    def send_message(self):
        message = self.message_input.text()
        self.interface.sendText(message)
        self.chat_display.addItem(f"You: {message}")
        self.message_input.clear()

    def gps(self):
        interface = meshtastic.serial_interface.SerialInterface()
        node_ids = list(interface.nodes.keys())
        #print("Available node IDs:", node_ids)

        # Check if there are any nodes in the network
        if not node_ids:
            self.text_edit.append("No nodes found in the mesh network.")
        else:
            # Iterate through all available nodes
            for node_id in node_ids:
                if node_id in interface.nodes:
                    current_node = interface.nodes[node_id]
                    position_data = current_node.get("position", {})

                    latitude = position_data.get("latitude")
                    longitude = position_data.get("longitude")
                    altitude = position_data.get("altitude")

                    self.text_edit.append(f"\nNode ID: {node_id}")
                    if latitude is not None and longitude is not None and altitude is not None:
                        self.text_edit.append(f"Latitude:  '{latitude}'")
                        self.text_edit.append(f"Longitude:  '{longitude}'")
                        self.text_edit.append(f"Altitude:  '{altitude}'")
                    else:
                        self.text_edit.append(f"No position information available for this node.")
                        self.text_edit.append(str(current_node))
                else:
                    self.text_edit.append(f"Node with ID '{node_id}' not found in the mesh network.")



        
    def list_usb_devices(self):
        ports = [port.device for port in comports()]

        if not ports:
            self.text_edit.append("No USB devices found.")
        else:
            self.text_edit.append("Available USB devices:")
            for port in ports:
                self.text_edit.append(f"  {port}")
     

    def setup_toolbar(self):
        # Set the style sheet for the toolbar to have a background color of #808080
        self.toolbar.setStyleSheet("QToolBar { background-color: #808080; }")
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setFixedWidth(80)
    
        icon_size = QSize(100, 100)

        # Create buttons and add them to the toolbar
        button1 = QToolButton()
        button1.setIcon(QIcon("qt icons/menu.ico"))
        button1.setToolButtonStyle(Qt.ToolButtonIconOnly)  # Initially only show the icon
        button1.setStyleSheet("padding: 9px;")
        button1.setIconSize(icon_size)
    
        # Other buttons
        button2 = self.create_tool_button("qt icons/map_icon.ico", "Map")
        button3 = self.create_tool_button("qt icons/settings_icon.ico", "Config")
        button4 = self.create_tool_button("qt icons/layer_icon.ico", "Channels")
        button5 = self.create_tool_button("qt icons/group_icon.svg", "Peers")
        button6 = self.create_tool_button("qt icons/plus_icon.ico", "New")
        
        self.toolbar.addWidget(button1)
        self.toolbar.addWidget(button2)
        self.toolbar.addWidget(button3)
        self.toolbar.addWidget(button4)
        self.toolbar.addWidget(button5)
        self.toolbar.addWidget(button6)
        
        # Connect buttons to change the stacked widget index or other actions
        #button1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        button2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        button3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))  
        button4.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        button5.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        button6.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))

    
    # Connect button1 to toggle the visibility of button names
        button1.clicked.connect(self.toggle_button_names)

    def create_tool_button(self, icon_path, text):
        button = QToolButton()
        button.setIcon(QIcon(icon_path))
        button.setText(text)
        button.setIconSize(QSize(50, 50))
        button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        return button
    
    def toggle_button_names(self):
    # Toggle between showing and hiding the text of buttons
        for button in self.toolbar.children():
            if isinstance(button, QToolButton) and button.toolButtonStyle() == Qt.ToolButtonIconOnly:
                self.toolbar.setFixedWidth(100)
                button.setIconSize(QSize(50, 50))
                button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            elif isinstance(button, QToolButton):
                self.toolbar.setFixedWidth(50)
                button.setToolButtonStyle(Qt.ToolButtonIconOnly)

       
    def setup_stacked_widget(self):
        widget1 = QWidget()
        #widget1.setStyleSheet("background-color: #0d0a03;")
        widget1_layout = QVBoxLayout()
        #widget1_layout.addWidget(QLineEdit())
        widget1.setLayout(widget1_layout)
        
        widget2 = QWidget()
        widget2_layout = QVBoxLayout()
        gmap = gmplot.GoogleMapPlotter(5.590039, -0.156270, 18)
        gmap.apikey = "AIzaSyDkw3a_XLgmpbUFB1yuuNj3o5cFlhP7HCo"
        gmap.enable_marker_dropping('orange')
        map_html = gmap.get()
        # Display the map with QWebEngineView
        #web_view = QtWebEngineWidgets.QWebEngineView()
        web_view = QWebEngineView()
        web_view.setHtml(map_html)
        widget2_layout.addWidget(web_view)
        widget2.setLayout(widget2_layout)
        
        widget3 = QWidget()
        widget3.setStyleSheet("background-color: #bcbec2;")
        widget3_layout = QVBoxLayout()
        self.text_edit1 = QTextEdit()
        self.text_edit1.setReadOnly(True)
        widget3_layout.addWidget(self.text_edit1)
        gps_button = QPushButton("Device")
        gps_button.clicked.connect(self.gps)
        widget3_layout.addWidget(gps_button)
        widget3.setLayout(widget3_layout)

        widget4 = QWidget()
        widget4.setStyleSheet("background-color: #828282; opacity: 0.5;")
        widget4_layout = QVBoxLayout()
        widget4_layout.addWidget(QLabel("Widget 4"))
        #widget2_layout.addWidget(QComboBox())
        #widget2_layout.addWidget(QPushButton())
        widget4.setLayout(widget4_layout)
        
        widget5 = QWidget()
        widget5.setStyleSheet("background-color: white;")
        widget5_layout = QVBoxLayout()
        data = {
            "Sigtrack S1": ["TBEAM", "08:F9:F0:D0:48:49", "Never", "9.5db/97.5%"],
            "Sigtrack S1": ["TBEAM", "08:F9:F0:D0:48:49", "Never", "9.5db/97.5%"],
            "Sigtrack S1": ["TBEAM", "08:F9:F0:D0:48:49", "Never", "9.5db/97.5%"]
            # Add more entries as needed
        }

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Name", "Model", "MAC Address", "Last Heard", "SNR"])

        row_position = 0

        for key, values in data.items():
            table.insertRow(row_position)
            table.setItem(row_position, 0, QTableWidgetItem(key))
            for col_position, value in enumerate(values):
                table.setItem(row_position, col_position + 1, QTableWidgetItem(value))
            row_position += 1

        widget5_layout.addWidget(table)
        widget5.setLayout(widget5_layout)   
        
        widget6 = QWidget()
        widget6.setStyleSheet("background-color: #bcbec5;")
        widget6_layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        widget6_layout.addWidget(self.text_edit)
        usb_button = QPushButton("Connect New Device")
        #usb_button.clicked.connect(self.list_usb_devices)
        widget6_layout.addWidget(usb_button)
        widget6.setLayout(widget6_layout)
          
        # Add the widgets to the stacked widget
        self.stacked_widget.addWidget(widget1)
        self.stacked_widget.addWidget(widget2)
        self.stacked_widget.addWidget(widget3)
        self.stacked_widget.addWidget(widget4)
        self.stacked_widget.addWidget(widget5)
        self.stacked_widget.addWidget(widget6)
           

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create the dock widget to contain the chat interface
        self.chat_dock_widget = QDockWidget("Chat Application", self)
        self.chat_interface = ChatInterface()
        self.chat_dock_widget.setWidget(self.chat_interface)

        # Add the dock widget to the main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.chat_dock_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()




