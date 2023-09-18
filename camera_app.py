import sys
import cv2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTabWidget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QtCore.QSize(1300, 500))
        self.setWindowTitle('PyQt Camera Feed')

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('world_map.jpeg'))
        self.setWindowIcon(icon)

        # Create a splitter for left and right sections
        splitter = QtWidgets.QSplitter(self)
        splitter.setGeometry(QtCore.QRect(0, 0, 1300, 400))

        # Create the left tab widget
        left_tab_widget = QtWidgets.QTabWidget(splitter)
        left_tab_widget.setGeometry(QtCore.QRect(25, 400, 250, 450))

        left_settings_tab = QtWidgets.QWidget()
        left_settings_tab_1 = QtWidgets.QWidget()
        left_tab_widget.addTab(left_settings_tab, "Still Capture")
        left_tab_widget.addTab(left_settings_tab_1, "Video")

        # Create the camera widget in the middle
        self.camera_widget = QtWidgets.QWidget(splitter)
        self.camera_widget.setGeometry(QtCore.QRect(250, 0, 500, 500))
        self.label = QtWidgets.QLabel("Camera Feed", self.camera_widget)
        self.label.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), QtCore.QSize(700, 400)))
        self.label.setScaledContents(True)
        self.initCamera()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateCamera)
        self.timer.start(50)  # Update the camera feed every 50 milliseconds



        # Create the right tab widget
        right_tab_widget = QtWidgets.QTabWidget(splitter)
        right_tab_widget.setGeometry(QtCore.QRect(1500, 0, 250, 450))

        # Add tabs to left and right tab widgets


        right_settings_tab = QtWidgets.QWidget()
        right_settings_tab_1 = QtWidgets.QWidget()
        right_settings_tab_2 = QtWidgets.QWidget()
        right_settings_tab_3 = QtWidgets.QWidget()

        # Add tabs to the left and right tab widgets and populate them
        #left_tab_widget = QtWidgets.QTabWidget(splitter)
        #left_tab_widget.setGeometry(QtCore.QRect(25, 400, 250, 450))
        #left_tab_widget.addTab(left_settings_tab, "Still Capture")
        #left_tab_widget.addTab(left_settings_tab_1, "Video")


        right_tab_widget.addTab(right_settings_tab, "Image Tuning")
        right_tab_widget.addTab(right_settings_tab_1, "Pan/Zoom")
        right_tab_widget.addTab(right_settings_tab_2, "AEC/AWB")
        right_tab_widget.addTab(right_settings_tab_3, "Info")

        self.populateStillCaptureTab(left_settings_tab)
        self.populateVideoTab(left_settings_tab_1)
        self.populateImageTuningTab(right_settings_tab)
        self.populatePanZoomTab(right_settings_tab_1)
        self.populateAEC_AWBTab(right_settings_tab_2)
        self.populateInfoTab(right_settings_tab_3)

    def populateStillCaptureTab(self, tab):

        # left side
        self.label_name = QtWidgets.QLabel("Name", self)
        self.label_name.setGeometry(QtCore.QRect(20, 25, 135, 20))
        self.textbox = QtWidgets.QTextEdit(self)
        self.textbox.setGeometry(QtCore.QRect(180, 25, 115, 20))

        self.label_file = QtWidgets.QLabel("File Type", self)
        self.label_file.setGeometry(QtCore.QRect(20, 50, 135, 20))
        self.combo_box_file = QtWidgets.QComboBox(self)
        self.combo_box_file.setGeometry(QtCore.QRect(180, 50, 115, 20))
        file_options = ["jpg", "png", "jpeg"]
        self.combo_box_file.addItems(file_options)

        self.label_resolution = QtWidgets.QLabel("Resolution", self)
        self.label_resolution.setGeometry(QtCore.QRect(20, 75, 135, 20))
        self.double_spin_box_resolution = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_resolution.setGeometry(QtCore.QRect(180, 75, 50, 20))
        self.label_resolution_1 = QtWidgets.QLabel("X", self)
        self.label_resolution_1.setGeometry(QtCore.QRect(235, 75, 135, 20))
        self.double_spin_box_resolution_2 = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_resolution_2.setGeometry(QtCore.QRect(245, 75, 50, 20))

        self.label_sensor = QtWidgets.QLabel("Sensor Mode", self)
        self.label_sensor.setGeometry(QtCore.QRect(20, 100, 135, 20))
        self.combo_box_sensor_mode = QtWidgets.QComboBox(self)
        self.combo_box_sensor_mode.setGeometry(QtCore.QRect(180, 100, 115, 20))
        sensor_options = ["Option A", "Option B", "Option C"]
        self.combo_box_sensor_mode.addItems(sensor_options)

        self.label_enable_preview = QtWidgets.QLabel('Enable Preview Mode', self)
        self.label_enable_preview.setGeometry(QtCore.QRect(20, 125, 110, 20))
        self.checkbox_enable = QtWidgets.QCheckBox(self)
        self.checkbox_enable.setGeometry(QtCore.QRect(180, 125, 110, 20))

        self.label_preview = QtWidgets.QLabel("Preview Mode", self)
        self.label_preview.setGeometry(QtCore.QRect(20, 150, 135, 20))
        self.combo_box_preview = QtWidgets.QComboBox(self)
        self.combo_box_preview.setGeometry(QtCore.QRect(180, 150, 115, 20))
        preview_options = ["Option A", "Option B", "Option C"]
        self.combo_box_preview.addItems(preview_options)

        self.label_HDR = QtWidgets.QLabel('HDR', self)
        self.label_HDR.setGeometry(QtCore.QRect(20, 175, 110, 20))
        self.checkbox = QtWidgets.QCheckBox(self)
        self.checkbox.setGeometry(QtCore.QRect(180, 175, 110, 20))

        self.label_number_of_HDR = QtWidgets.QLabel("Number of HDR frames", self)
        # self.label_number_of_HDR.setStyleSheet('background-color:red')
        self.label_number_of_HDR.setGeometry(QtCore.QRect(20, 200, 110, 20))
        self.double_spin_box_HDR = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_HDR.setGeometry(QtCore.QRect(180, 200, 115, 20))

        self.label_HDR_above = QtWidgets.QLabel("Number of HDR stops above", self)
        self.label_HDR_above.setGeometry(QtCore.QRect(20, 230, 135, 20))
        self.double_spin_box_HDR_stops_above = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_HDR_stops_above.setGeometry(QtCore.QRect(180, 225, 115, 20))

        self.label_HDR_below = QtWidgets.QLabel("Number of HDR stops below", self)
        self.label_HDR_below.setGeometry(QtCore.QRect(20, 250, 135, 20))
        self.double_spin_box_HDR_stops_below = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_HDR_stops_below.setGeometry(QtCore.QRect(180, 250, 115, 20))

        self.label_HDR_gamma = QtWidgets.QLabel("HDR Gamma Setting", self)
        self.label_HDR_gamma.setGeometry(QtCore.QRect(20, 275, 135, 20))
        self.double_spin_box_HDR_gamma_settings = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_HDR_gamma_settings.setGeometry(QtCore.QRect(180, 275, 115, 20))

        self.push_button_apply = QtWidgets.QPushButton('Apply', self)
        self.push_button_apply.setGeometry(QtCore.QRect(20, 300, 270, 30))

    def populateVideoTab(self, tab):
        # video tab
        # Example widgets for Video tab
        label_framerate = QtWidgets.QLabel("Frame Rate:", tab)
        label_framerate.setGeometry(QtCore.QRect(20, 25, 135, 20))
        spin_framerate = QtWidgets.QSpinBox(tab)
        spin_framerate.setGeometry(QtCore.QRect(160, 25, 80, 20))
        spin_framerate.setRange(1, 60)

        checkbox_audio = QtWidgets.QCheckBox("Include Audio", tab)
        checkbox_audio.setGeometry(QtCore.QRect(20, 50, 135, 20))


        # capture image button
        self.picture_button = QtWidgets.QPushButton("Take photo", self)
        self.picture_button.setGeometry(QtCore.QRect(20, 400, 300, 30))
        self.picture_button.clicked.connect(self.capture_photo)


    def populateImageTuningTab(self, tab):
        # right side

        self.label_saturation = QtWidgets.QLabel("Saturation", self)
        self.label_saturation.setGeometry(QtCore.QRect(1000, 30, 50, 20))
        self.spin_box_saturation = QtWidgets.QDoubleSpinBox(self)
        self.spin_box_saturation.setGeometry(QtCore.QRect(1100, 30, 70, 20))

        self.slider_1 = QtWidgets.QSlider(self)
        self.slider_1.setOrientation(QtCore.Qt.Horizontal)
        self.slider_1.setGeometry(QtCore.QRect(1200, 30, 70, 20))
        self.slider_1.valueChanged.connect(lambda value: self.updateSpinBox(value, self.double_spin_box_saturation))

        self.label_contrast = QtWidgets.QLabel("Contrast", self)
        self.label_contrast.setGeometry(QtCore.QRect(1000, 60, 50, 20))
        self.double_spin_box_contrast = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_contrast.setGeometry(QtCore.QRect(1100, 60, 70, 20))

        self.slider_2 = QtWidgets.QSlider(self)
        self.slider_2.setOrientation(QtCore.Qt.Horizontal)
        self.slider_2.setGeometry(QtCore.QRect(1200, 60, 70, 20))
        self.slider_2.valueChanged.connect(lambda value: self.updateSpinBox(value, self.double_spin_box_contrast))

        self.label_sharpness = QtWidgets.QLabel("Sharpness", self)
        self.label_sharpness.setGeometry(QtCore.QRect(1000, 90, 50, 20))
        self.double_spin_box_sharpness = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_sharpness.setGeometry(QtCore.QRect(1100, 90, 70, 20))

        self.slider_3 = QtWidgets.QSlider(self)
        self.slider_3.setOrientation(QtCore.Qt.Horizontal)
        self.slider_3.setGeometry(QtCore.QRect(1200, 90, 70, 20))
        self.slider_3.valueChanged.connect(lambda value: self.updateSpinBox(value, self.double_spin_box_sharpness))

        self.label_brightness = QtWidgets.QLabel("Brightness", self)
        self.label_brightness.setGeometry(QtCore.QRect(1000, 120, 50, 20))
        self.double_spin_box_brightness = QtWidgets.QDoubleSpinBox(self)
        self.double_spin_box_brightness.setGeometry(QtCore.QRect(1100, 120, 70, 20))

        self.slider_4 = QtWidgets.QSlider(self)
        self.slider_4.setOrientation(QtCore.Qt.Horizontal)
        self.slider_4.setGeometry(QtCore.QRect(1200, 120, 70, 20))
        self.slider_4.valueChanged.connect(lambda value: self.updateSpinBox(value, self.double_spin_box_brightness))

        self.reset_button = QtWidgets.QPushButton("Reset", self)
        self.reset_button.setGeometry(QtCore.QRect(990, 160, 300, 30))
        self.reset_button.clicked.connect(self.resetValues)

        #self.push_button_next = QtWidgets.QPushButton('>', self)
        #self.push_button_next.setGeometry(QtCore.QRect(920, 90, 50, 170))


    def populatePanZoomTab(self, tab):
        # Example widgets for Pan/Zoom tab
        label_pan = QtWidgets.QLabel("Pan:", tab)
        label_pan.setGeometry(QtCore.QRect(20, 25, 135, 20))
        slider_pan = QtWidgets.QSlider(QtCore.Qt.Horizontal, tab)
        slider_pan.setGeometry(QtCore.QRect(160, 25, 115, 20))

        label_zoom = QtWidgets.QLabel("Zoom:", tab)
        label_zoom.setGeometry(QtCore.QRect(20, 50, 135, 20))
        slider_zoom = QtWidgets.QSlider(QtCore.Qt.Horizontal, tab)
        slider_zoom.setGeometry(QtCore.QRect(160, 50, 115, 20))

        # Add more widgets as needed for Pan/Zoom tab

    def populateAEC_AWBTab(self, tab):
        # Example widgets for AEC/AWB tab
        label_aec = QtWidgets.QLabel("Auto Exposure Control:", tab)
        label_aec.setGeometry(QtCore.QRect(20, 25, 135, 20))
        checkbox_aec = QtWidgets.QCheckBox(tab)
        checkbox_aec.setGeometry(QtCore.QRect(160, 25, 115, 20))

        label_awb = QtWidgets.QLabel("Auto White Balance:", tab)
        label_awb.setGeometry(QtCore.QRect(20, 50, 135, 20))
        checkbox_awb = QtWidgets.QCheckBox(tab)
        checkbox_awb.setGeometry(QtCore.QRect(160, 50, 115, 20))

        # Add more widgets as needed for AEC/AWB tab

    def populateInfoTab(self, tab):
        # Example widgets for Info tab
        label_info = QtWidgets.QLabel("Camera Info:", tab)
        label_info.setGeometry(QtCore.QRect(20, 25, 135, 20))
        text_info = QtWidgets.QTextEdit(tab)
        text_info.setGeometry(QtCore.QRect(160, 25, 200, 100))
        text_info.setReadOnly(True)

        # Add more widgets as needed for Info tab



    def initCamera(self):
        self.cap = cv2.VideoCapture(0)  # 0 for default camera, you can change it to the camera index you want
        if not self.cap.isOpened():
            print("Error: Camera not found")
            sys.exit()

    def updateCamera(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)

    def updateSpinBox(self, value, spin_box):
        # Update the spin box value when the slider value changes
        spin_box.setValue(value / 10.0)

    def resetValues(self):
        # Reset the values of the spin boxes and sliders to 0
        self.double_spin_box_saturation.setValue(0)
        self.slider_1.setValue(0)
        self.double_spin_box_contrast.setValue(0)
        self.slider_2.setValue(0)
        self.double_spin_box_sharpness.setValue(0)
        self.slider_3.setValue(0)
        self.double_spin_box_brightness.setValue(0)
        self.slider_4.setValue(0)

    def capture_photo(self):
        print("Capturing a photo...")
        camera = cv2.VideoCapture(0)  # Open the default camera (index 0)

        _, frame = camera.read()  # Capture a frame from the camera

        # Save the captured frame as an image file
        cv2.imwrite("captured_image.jpg", frame)

        camera.release()  # Release the camera resource

        # Display the captured photo in the QLabel
        #pixmap = QPixmap("captured_image.jpg")
        #self.camera_label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        print("Picture captured")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationDisplayName("Camera")
    ui = MainWindow()
    ui.show()
    app.exec_()
