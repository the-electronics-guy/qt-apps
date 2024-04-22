import sys
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vessel Map")

        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)

        # HTML content of the map
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
            var height="800";         // height in pixels
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

        # Load HTML content into the web view
        self.web_view.setHtml(html_content, QUrl("https://www.vesselfinder.com/"))

        self.resize(800, 600)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
