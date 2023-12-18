from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QTextEdit, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QDockWidget, QToolBar, QStackedWidget, QComboBox,
    QLabel, QSizePolicy, QToolButton
)

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

class ChatInterface(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout for the chat interface
        self.main_layout = QHBoxLayout(self)

        # Sidebar divided into two parts
        self.sidebar_layout = QHBoxLayout()
        self.toolbar = QToolBar()
        self.stacked_widget = QStackedWidget()

        # Set up the toolbar with buttons
        self.setup_toolbar()

        # stack widgets linked to push buttons
        self.setup_stacked_widget()

        # Add the toolbar and the stacked widget to the sidebar layout
        self.sidebar_layout.addWidget(self.toolbar)
        self.sidebar_layout.addWidget(self.stacked_widget)

        # Chat display
        self.chat_display = QListWidget()
        

        # Message input area
        self.message_input = QLineEdit()
        #self.message_input.setFixedHeight(50)
        
        
        self.send_button = QToolButton()
        self.send_button.setIcon(QIcon('qt icons/send_icon.ico'))
        self.send_button.setStyleSheet("border: none;")
        #self.send_button.setFixedWidth(100)
        self.send_button.clicked.connect(self.send_message)
        
        self.upload_button = QToolButton()
        self.upload_button.setIcon(QIcon('qt icons/upload_files.ico'))
        self.upload_button.setStyleSheet("border: none;")
        

        # Layout for the message input area
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.upload_button)

        # Layout for the chat area
        chat_layout = QVBoxLayout()
        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(input_layout)

        # Add sidebar and chat layouts to the main layout
        self.main_layout.addLayout(self.sidebar_layout, 1)  # Sidebar takes up 1 part of the space
        self.main_layout.addLayout(chat_layout, 3)  # Chat area takes up 3 parts of the space
    
    def send_message(self):
        message = self.message_input.text()
        self.message_input.append("You: " + message)
    
    def setup_toolbar(self):
    # Set the style sheet for the toolbar to have a background color of #808080
        self.toolbar.setStyleSheet("QToolBar { background-color: #808080; }")
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setFixedWidth(53)
    
        icon_size = QSize(100, 100)

    # Create buttons and add them to the toolbar
        button1 = QToolButton()
        button1.setIcon(QIcon("qt icons/menu.ico"))
        button1.setToolButtonStyle(Qt.ToolButtonIconOnly)  # Initially only show the icon
        button1.setStyleSheet("padding: 9px;")
        button1.setIconSize(icon_size)
    
    # Other buttons
        button2 = self.create_tool_button("qt icons/captain.ico", "Profile")
        button3 = self.create_tool_button("qt icons/walkie_talkie_icon.ico", "Radio")
        button4 = self.create_tool_button("qt icons/network.ico", "Broadcast")
        button5 = self.create_tool_button("qt icons/drone_icon.svg", "Stream")
        button6 = self.create_tool_button("qt icons/group_icon.svg", "Teams")
        button7 = self.create_tool_button("qt icons/settings.ico", "Settings")

    
        self.toolbar.addWidget(button1)
        self.toolbar.addWidget(button2)
        self.toolbar.addWidget(button3)
        self.toolbar.addWidget(button4)
        self.toolbar.addWidget(button5)
        self.toolbar.addWidget(button6)
        self.toolbar.addWidget(button7)
        
        # Connect buttons to change the stacked widget index or other actions
        button1.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        button2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        button3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))  
        button4.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
    
    # Connect button1 to toggle the visibility of button names
        button1.clicked.connect(self.toggle_button_names)

    def create_tool_button(self, icon_path, text):
    # Helper function to create a tool button
        button = QToolButton()
        button.setIcon(QIcon(icon_path))
        button.setText(text)
        button.setIconSize(QSize(50, 50))
        button.setToolButtonStyle(Qt.ToolButtonIconOnly)  # Initially only show the icon
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
        # Create different content widgets for the stack
        widget1 = QWidget()
        widget1.setStyleSheet("background-color: #0d0a03;")
        widget1_layout = QVBoxLayout()
        widget1_layout.addWidget(QLineEdit())
        widget1.setLayout(widget1_layout)

        widget2 = QWidget()
        widget2.setStyleSheet("background-color: #828282; opacity: 0.5;")
        widget2_layout = QVBoxLayout()
        widget2_layout.addWidget(QLabel("IP Adress"))
        widget2_layout.addWidget(QComboBox())
        widget2_layout.addWidget(QPushButton())
        widget2.setLayout(widget2_layout)
        
        widget3 = QWidget()
        widget3.setStyleSheet("background-color: #1b1c1b;")
        widget3_layout = QVBoxLayout()
        widget3_layout.addWidget(QPushButton())
        widget3.setLayout(widget3_layout)
        
        widget4 = QWidget()
        widget4.setStyleSheet("background-color: #bcbec2;")
        widget4_layout = QVBoxLayout()
        widget4_layout.addWidget(QPushButton())
        widget4.setLayout(widget4_layout)
        
        widget5 = QWidget()
        widget5.setStyleSheet("background-color: #bcbec5;")
        widget5_layout = QVBoxLayout()
        widget5_layout.addWidget(QPushButton())
        widget5.setLayout(widget5_layout)
        
        # Add the widgets to the stacked widget
        self.stacked_widget.addWidget(widget1)
        self.stacked_widget.addWidget(widget2)
        self.stacked_widget.addWidget(widget3)
        self.stacked_widget.addWidget(widget4)
        self.stacked_widget.addWidget(widget5)
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create the dock widget to contain the chat interface
        self.chat_dock_widget = QDockWidget("Chat Application", self)
        self.chat_interface = ChatInterface()
        self.chat_dock_widget.setWidget(self.chat_interface)

        # Add the dock widget to the main window
        self.addDockWidget(Qt.RightDockWidgetArea, self.chat_dock_widget)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

