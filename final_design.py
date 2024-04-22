import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout,
                               QPushButton, QStackedWidget, QHBoxLayout, QListWidget, QLineEdit,
                               QToolButton, QToolBar, QLabel,QTabWidget,QTextEdit, QDialog)
from PySide6.QtCore import Qt, QSize, QThread, Signal, QMimeData, QPoint, QByteArray
from PySide6.QtGui import QIcon, QPixmap, QImage, QDrag, QFont
from PySide6.QtWebEngineWidgets import QWebEngineView
import folium
from folium.plugins import Draw
import requests


class ImageListWidget(QListWidget):
    pass


class MapDisplay(QMainWindow):
    def __init__(self):
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

        # Weather button
        self.weather_button = self.create_tool_button("qt icons/weather_icon.svg", "Weather")
        self.weather_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.weather_button.setToolTip("Weather")
        self.weather_button.clicked.connect(self.toggle_weather_widget)
        self.toolbar.addWidget(self.weather_button)

        # maps button
        self.maps_button = self.create_tool_button("qt icons/map_icon.ico", "Maps")
        self.maps_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.maps_button.setToolTip("Maps")
        self.toolbar.addWidget(self.maps_button)

        # Toggle dock button
        self.toggle_dock_button = QToolButton()
        self.toggle_dock_button.setIcon(QIcon("qt icons/toggle_icon.svg"))
        self.toggle_dock_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.toggle_dock_button.setToolTip("Toggle Dock Widget")
        self.toggle_dock_button.clicked.connect(self.toggle_dock_widget)
        self.toolbar.addWidget(self.toggle_dock_button)

        # Create the map
        self.m = folium.Map([5.590039, -0.156270], zoom_start=10).add_child(
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

        # Add Weather Widget
        self.weather_widget = WeatherApp()
        self.weather_widget.move(200, 500)  # Move to desired position
        self.weather_widget.hide()

        # Create a dock widget for stacking interfaces
        self.dock_widget = QDockWidget("Interfaces", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        self.dock_widget.hide()

    def toggle_weather_widget(self):
        if self.weather_widget.isHidden():
            self.weather_widget.show()
        else:
            self.weather_widget.hide()

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


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")
        # Set background color
        self.setStyleSheet("background-color: #f0f0f0;")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.cityName = "Accra"
        self.api_key = 'd2ed8137acc17a02bcd284b4548d5b88'
        self.BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

        # Create weather label
        self.weather_label = QLabel()
        self.weather_label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.weather_label)

        # Create weather icon
        self.weather_icon_label = QLabel()
        self.layout.addWidget(self.weather_icon_label)

        # Create layouts for temperature, humidity, and wind speed
        temperature_layout = QHBoxLayout()
        self.layout.addLayout(temperature_layout)

        humidity_layout = QHBoxLayout()
        self.layout.addLayout(humidity_layout)

        wind_speed_layout = QHBoxLayout()
        self.layout.addLayout(wind_speed_layout)

        # Set up temperature label and icon
        temperature_icon = QLabel()
        temperature_icon.setPixmap(QPixmap("qt icons/temperature_icon.svg").scaled(30, 30))
        temperature_layout.addWidget(temperature_icon)

        self.temperature_label = QLabel()
        temperature_layout.addWidget(self.temperature_label)

        # Set up humidity label and icon
        humidity_icon = QLabel()
        humidity_icon.setPixmap(QPixmap("qt icons/humidity_icon.svg").scaled(30, 30))
        humidity_layout.addWidget(humidity_icon)

        self.humidity_label = QLabel()
        humidity_layout.addWidget(self.humidity_label)

        # Set up wind speed label and icon
        wind_speed_icon = QLabel()
        wind_speed_icon.setPixmap(QPixmap("qt icons/wind_speed_icon.svg").scaled(30, 30))
        wind_speed_layout.addWidget(wind_speed_icon)

        self.wind_speed_label = QLabel()
        wind_speed_layout.addWidget(self.wind_speed_label)

        # Create refresh button
        self.refresh_button = QPushButton("Refresh Weather")
        self.refresh_button.clicked.connect(self.refresh_weather)
        self.layout.addWidget(self.refresh_button)

        # Set initial weather
        self.refresh_weather()

        # Make the widget draggable
        self.setMouseTracking(True)
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def refresh_weather(self):
        self.refresh_button.setEnabled(False)  # Disable refresh button during update
        try:
            url = f"{self.BASE_URL}?q={self.cityName}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad responses
            data = response.json()

            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            icon_name = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_name}.png"
            icon_data = requests.get(icon_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data)

            # Display weather information
            weather_report = f"Weather: {weather_description}"
            self.weather_label.setText(weather_report)
            self.weather_icon_label.setPixmap(pixmap)

            # Display temperature, humidity, and wind speed
            self.temperature_label.setText(f"{temperature}°C")
            self.humidity_label.setText(f"{humidity}%")
            self.wind_speed_label.setText(f"{wind_speed} m/s")
        except Exception as e:
            print(f"Error: {e}")  # Handle errors gracefully
        finally:
            self.refresh_button.setEnabled(True)  # Enable refresh button after update


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
    window = MapDisplay()
    window.show()
    sys.exit(app.exec())
