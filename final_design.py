import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout,
                               QPushButton, QStackedWidget, QHBoxLayout, QListWidget, QLineEdit,
                               QToolButton, QToolBar, QLabel,QTabWidget,QTextEdit)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QMimeData, QPoint, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QImage, QDrag
from PySide6.QtWebEngineWidgets import QWebEngineView
import folium
from folium.plugins import Draw



class ImageListWidget(QListWidget):
    pass



class MapDisplay(QMainWindow):
    def __init__(self, icon_filenames):
        super().__init__()

        self.setWindowTitle("Map Application")
        self.setGeometry(100, 100, 800, 600)

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
        self.toolbar.addWidget(self.peers_button)

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
        self.chat_interface = ChatInterface()
        self.dock_widget.setWidget(self.chat_interface)

    def show_page2(self):
        self.page2 = Page2()
        self.dock_widget.setWidget(self.page2)

    def show_symbol_manager(self):
        self.symbol_manager = SymbolManager()
        self.dock_widget.setWidget(self.symbol_manager)


class ChatInterface(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout for the chat interface
        self.main_layout = QVBoxLayout(self)

        # Chat display
        self.chat_display = QListWidget()
        self.main_layout.addWidget(self.chat_display)

        # Message input area
        self.message_input = QLineEdit()
        #self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QToolButton()
        self.send_button.setIcon(QIcon('qt icons/send_icon.ico'))
        self.send_button.setStyleSheet("border: none;")
        #self.send_button.clicked.connect(self.send_message)

        self.upload_button = QToolButton()
        self.upload_button.setIcon(QIcon('qt icons/upload_files.ico'))
        self.upload_button.setStyleSheet("border: none;")

        # Input layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.upload_button)

        self.main_layout.addLayout(input_layout)



class Page2(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout for page 2
        self.main_layout = QVBoxLayout(self)
        self.label = QLabel("This is Page 2")
        self.main_layout.addWidget(self.label)


class SymbolManager(QWidget):
    def __init__(self):
        super().__init__()

        # Create the central widget for the dock
        self.tab_widget = QTabWidget()

        # Create widgets for each tab
        symbol_gallery_tab = QWidget()
        symbol_search_tab = QWidget()
        symbol_key_tab = QWidget()

        # Add tabs to the tab widget
        self.tab_widget.addTab(symbol_gallery_tab, "Symbol Gallery")
        self.tab_widget.addTab(symbol_search_tab, "Symbol Search")
        self.tab_widget.addTab(symbol_key_tab, "Symbol Key")

        # Set layout for each tab
        symbol_gallery_layout = QVBoxLayout(symbol_gallery_tab)
        symbol_search_layout = QVBoxLayout(symbol_search_tab)
        symbol_key_layout = QVBoxLayout(symbol_key_tab)

        # Gallery
        self.favourites = QToolButton()
        self.favourites.setIcon(QIcon("qt icons/favourite_icon.svg"))
        self.group1 = QHBoxLayout()
        self.group1.addWidget(self.favourites)
        symbol_gallery_layout.addLayout(self.group1)

        # Search bar
        self.search_label = QLabel("Search for symbol name:")
        self.search_bar = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("background-color:green;")
        symbol_search_layout.addWidget(self.search_label)
        symbol_search_layout.addWidget(self.search_bar)
        symbol_search_layout.addWidget(self.search_button)

        # Key buttons
        self.label = QLabel("Affiliation")
        self.btn_unknown = QPushButton("Unknown")
        self.btn_friend = QPushButton("Friend")
        self.btn_hostile = QPushButton("Hostile")
        self.btn_neutral = QPushButton("Neutral")

        self.key1 = QHBoxLayout()
        self.key1.addWidget(self.label)
        self.key1.addWidget(self.btn_unknown)
        self.key1.addWidget(self.btn_friend)
        self.key1.addWidget(self.btn_hostile)
        self.key1.addWidget(self.btn_neutral)

        self.label1 = QLabel("Status")
        self.btn_preset = QToolButton()
        self.btn_planned = QToolButton()
        self.key2 = QHBoxLayout()
        self.key2.addWidget(self.label1)
        self.key2.addWidget(self.btn_preset)
        self.key2.addWidget(self.btn_planned)

        symbol_key_layout.addLayout(self.key1)
        symbol_key_layout.addLayout(self.key2)

        # Main layout for the central widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Symbol Manager")
        self.setGeometry(100, 100, 800, 600)

        # Create the central widget for the dock
        self.symbol_manager = SymbolManager()

        # Create a dock widget for the symbol manager
        self.symbol_dock_widget = QDockWidget("Symbol Manager", self)
        self.symbol_dock_widget.setWidget(self.symbol_manager)
        self.addDockWidget(Qt.RightDockWidgetArea, self.symbol_dock_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapDisplay(["airborne.png", "icon2.png"])
    window.show()
    sys.exit(app.exec())
