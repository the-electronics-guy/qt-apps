import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout,
                               QPushButton, QStackedWidget, QHBoxLayout, QListWidget, QLineEdit,
                               QToolButton, QToolBar, QLabel,
                               QTabWidget,QTextEdit, QTreeWidget, QTreeWidgetItem, QGridLayout)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QMimeData, QPoint, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QImage, QDrag
from PySide6.QtWebEngineWidgets import QWebEngineView
import folium
from folium.plugins import Draw
import os



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

        #folium.TileLayer('stamenwatercolor').add_to(self.m)

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
                    icon = pixmap.scaled(500, 500)
                    child_item.setIcon(0, icon)
                    child_item.setToolTip(0, file)

    def handle_item_clicked(self, item, column):
        # Emit the image_clicked signal with the pixmap of the clicked item
        icon = item.icon(column)
        self.image_clicked.emit(icon.pixmap(icon.availableSizes()[0]))


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
