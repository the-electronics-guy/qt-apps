from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget,
    QTextEdit, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QDockWidget,
    QToolBar, QStackedWidget, QComboBox,
    QLabel, QSizePolicy, QToolButton, QCheckBox,
    QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QMdiArea, QMdiSubWindow, QTableWidget, QTableWidgetItem,
    QGridLayout, QDialog, QRadioButton
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
from meshtastic.util import findPorts


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


class EmojiSelector(QDialog):
    def __init__(self, message_input: QLineEdit, parent=None):
        super(EmojiSelector, self).__init__(parent)
        self.setWindowTitle("Emoji Selector")

        self.message_input = message_input
        layout = QVBoxLayout()
        emoji_grid = QGridLayout()
        emojis = ["🤣", "😂", "😊", "❤", "😍", "😒", "👌", "😘", "😁", "👍", "🙌", "✌🤞", "😎", "😉", "👏", "😜", "👏", "😆", "🤔", "🎁"]

        for row in range(4):
            for col in range(5):
                index = row * 5 + col
                if index < len(emojis):
                    emoji_label = QLabel(emojis[index])
                    emoji_label.setStyleSheet("font-size: 20px;")
                    emoji_label.mousePressEvent = lambda event, emoji=emojis[index]: self.select_emoji(emoji)
                    emoji_grid.addWidget(emoji_label, row, col)
                layout.addLayout(emoji_grid)

                self.setLayout(layout)
                # self.chat_display = list_widget
                # self.message_input = message_input

    def select_emoji(self, emoji):
        # item = QListWidgetItem(emoji)
        # self.chat_display.addItem(item)
        self.message_input.setText(self.message_input.text() + emoji)
        # self.accept()



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
        self.chat_display.setStyleSheet("background-color: #808080")
        

        # Message input area
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QToolButton()
        self.send_button.setIcon(QIcon('qt icons/send_icon.ico'))
        self.send_button.setStyleSheet("border: none;")
        self.send_button.clicked.connect(self.send_message)
        
        self.emoji_button = QToolButton()
        self.emoji_button = QToolButton()
        self.emoji_button.setIcon(QIcon('icons/smile.svg'))
        self.emoji_button.setStyleSheet("background-color: #bcbec2; border: none;")
        self.emoji_button.setIconSize(QSize(24, 24))
        self.emoji_button.clicked.connect(self.show_emoji_selector)
        
        
        # Input layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.emoji_button)

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
        
        self.current_node_id = None
        self.selected_node_id = None
        

        
    def on_receive_message(self, packet, interface):
        if packet['decoded']['text']:
            sender_id = packet['from']
            message_text = packet['decoded']['text']
            self.chat_display.addItem(f"{sender_id}: {message_text}")
        else:
            self.chat_display.addItem(f"Received packet with no text content: {packet}")
    
        
    def show_broadcast_message(self):
        self.chat_display.clear()
        self.chat_display.addItem("Broadcast")
        
    
    def on_connection_established(self, interface, topic=pub.AUTO_TOPIC):
        self.current_node = "Desktop"
        self.chat_display.addItem(f"Node Connected: {self.current_node}")    

    def show_direct_message(self, node_name):
        # Update the selected node ID
        if node_name == "Sigtrack S1":
            self.selected_node_id = "!fa5769ec"  # Replace with the correct node ID for S8
        elif node_name == "Sigtrack S2":
            self.selected_node_id = "!e2e18c0c"  # Replace with the correct node ID for S2
        # Add similar conditions for other nodes

        if self.current_node:
            self.chat_display.clear()
            self.chat_display.addItem(f"Direct message to {node_name} from {self.current_node}")
        else:
            self.chat_display.addItem(f"No node connected. Cannot send direct message.")

    def send_message(self):
        message = self.message_input.text()

        # Check if S1 is selected and send message only to S8
        if self.current_node == "Sigtrack S1" and self.selected_node_id:
            self.interface.sendText(message, to=self.selected_node_id)
            self.chat_display.addItem(f"Desktop (S1 to {self.selected_node_id}): {message}")
        else:
            # Send message normally
            self.interface.sendText(message)
            self.chat_display.addItem(f"Desktop: {message}")

        self.message_input.clear()
        self.selected_node_id = None  # Reset selected node ID

    def gps(self):
        pass

        
    def list_usb_devices(self):
        pass

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
        button7 = self.create_tool_button("qt icons/message_icon.ico", "Messages")
        
        
        self.toolbar.addWidget(button1)
        self.toolbar.addWidget(button2)
        self.toolbar.addWidget(button3)
        self.toolbar.addWidget(button4)
        self.toolbar.addWidget(button5)
        self.toolbar.addWidget(button6)
        self.toolbar.addWidget(button7)
        
        # Connect buttons to change the stacked widget index or other actions
        #button1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        button2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        button3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))  
        button4.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        button5.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        button6.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))
        button7.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(6))

    
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
        widget4.setLayout(widget4_layout)
        
        widget5 = QWidget()
        widget5.setStyleSheet("background-color: white;")
        widget5_layout = QVBoxLayout()
        widget5_layout.addWidget(QLabel("Widget 5"))
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
        
        widget7 = QWidget()
        widget7.setStyleSheet("background-color: #bcbec5;")
        widget7_layout = QVBoxLayout()
        
        broadcast = QRadioButton("Broadcast", self)
        node_1 = QRadioButton("Sigtrack S1", self)
        node_2 = QRadioButton("Sigtrack S2", self)
        node_3 = QRadioButton("Sigtrack S3", self)
        node_4 = QRadioButton("Sigtrack S4", self)
        node_5 = QRadioButton("Sigtrack S5", self)
        node_6 = QRadioButton("Sigtrack S6", self)
        node_7 = QRadioButton("Sigtrack S7", self)
        node_8 = QRadioButton("Sigtrack S8", self)
        
        widget7_layout.addWidget(broadcast)
        widget7_layout.addWidget(node_1)
        widget7_layout.addWidget(node_2)
        widget7_layout.addWidget(node_3)
        widget7_layout.addWidget(node_4)
        widget7_layout.addWidget(node_5)
        widget7_layout.addWidget(node_6)
        widget7_layout.addWidget(node_7)
        widget7_layout.addWidget(node_8)
        
        self.current_node = None  # Variable to store the selected node

        # Connect radio buttons to their respective slots
        broadcast.clicked.connect(self.show_broadcast_message)
        node_1.clicked.connect(lambda: self.show_direct_message("Sigtrack S1"))
        node_2.clicked.connect(lambda: self.show_direct_message("Sigtrack S2"))
        node_3.clicked.connect(lambda: self.show_direct_message("Sigtrack S3"))
        node_4.clicked.connect(lambda: self.show_direct_message("Sigtrack S4"))
        node_5.clicked.connect(lambda: self.show_direct_message("Sigtrack S5"))
        node_6.clicked.connect(lambda: self.show_direct_message("Sigtrack S6"))
        node_7.clicked.connect(lambda: self.show_direct_message("Sigtrack S7"))
        node_8.clicked.connect(lambda: self.show_direct_message("Sigtrack S8"))

        widget7.setLayout(widget7_layout)
          
        # Add the widgets to the stacked widget
        self.stacked_widget.addWidget(widget1)
        self.stacked_widget.addWidget(widget2)
        self.stacked_widget.addWidget(widget3)
        self.stacked_widget.addWidget(widget4)
        self.stacked_widget.addWidget(widget5)
        self.stacked_widget.addWidget(widget6)
        self.stacked_widget.addWidget(widget7)
         
    def show_emoji_selector(self):
        emoji_selector = EmojiSelector(self.message_input, self)
        emoji_selector.exec() 

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







