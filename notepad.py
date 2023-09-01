import os, sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, \
    QPushButton, QLabel, QPlainTextEdit, QStatusBar, QToolBar, \
    QVBoxLayout, QAction, QFileDialog, QMessageBox

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontDatabase, QIcon, QKeySequence
from PyQt5.QtPrintSupport import QPrintDialog

class AppDemo(QMainWindow):
    def __init__(self):
        super(). __init__()
        self.setWindowTitle('Notepad')
        self.setWindowIcon(QIcon('./qt icons/notepad.ico'))
        self.screen_width, self.screen_height = self.geometry().width(), self.geometry().height()
        self.resize(self.screen_width, self.screen_height)

        self.filterTypes = 'Text Document (*.txt);; Python (*.py);; Markdown (*.md)'
        self.path = None

        fixedFont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedFont.setPointSize(12)

        mainLayout = QVBoxLayout()

        # editor
        self.editor = QPlainTextEdit()
        self.editor.setFont(fixedFont)
        mainLayout.addWidget(self.editor)

        # status bar
        self.statusbar = self.statusBar()

        # app container
        container = QWidget()
        container.setLayout(mainLayout)
        self.setCentralWidget(container)

        #-----------------------
        # File menu
        #-----------------------
        file_menu = self.menuBar().addMenu('&File')

        # -----------------------
        # File Toolbar
        # -----------------------
        file_toolbar = QToolBar('File')
        file_toolbar.setIconSize(QSize(40, 40))
        self.addToolBar(Qt.BottomToolBarArea, file_toolbar)

        # -----------------------
        # open, save,saveAs
        # -----------------------
        open_file_action = QAction(QIcon('./qt icons/file_open_icon.ico'), 'Open File...', self)
        open_file_action.setStatusTip('Open File')
        open_file_action.setShortcut(QKeySequence.Open)
        open_file_action.triggered.connect(self.file_open)

        save_file_action = self.create_action(self, './qt icons/save.ico', 'Save File', 'Save File', self.file_save)
        save_file_action.setShortcut(QKeySequence.Save)

        save_fileAs_action = self.create_action(self, './qt icons/save_as.ico', 'SaveAs', 'SaveAs', self.file_saveAs)
        save_fileAs_action.setShortcut(QKeySequence.SaveAs)

        file_menu.addActions([open_file_action, save_file_action, save_fileAs_action])
        file_toolbar.addActions([open_file_action, save_file_action, save_fileAs_action])

        #------------------
        # print action
        print_action = self.create_action(self, './qt icons/printer.ico', 'Print File', 'Print File', self.print_file)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        # -----------------------
        # Edit menu
        # -----------------------
        edit_menu = self.menuBar().addMenu('&Edit')

        # -----------------------
        # Edit toolbar
        # -----------------------
        edit_toolbar = QToolBar('Edit')
        edit_toolbar.setIconSize(QSize(40, 40))
        self.addToolBar(Qt.BottomToolBarArea, edit_toolbar)

        # undo and redo
        undo_action = self.create_action(self, './qt icons/undo.ico', 'Undo', 'Undo', self.editor.undo)
        undo_action.setShortcut(QKeySequence.Undo)

        redo_action = self.create_action(self, './qt icons/redo.ico', 'Redo', 'Redo', self.editor.redo)
        redo_action.setShortcut(QKeySequence.Redo)

        edit_menu.addActions([undo_action, redo_action])
        edit_toolbar.addActions([undo_action, redo_action])

        # clear action
        clear_action = self.create_action(self, './qt icons/delete.ico', 'Clear', 'Clear', self.clear_content)
        edit_menu.addAction(clear_action)
        edit_toolbar.addAction(clear_action)

        edit_menu.addSeparator()
        edit_toolbar.addSeparator()


        self.update_title()

    def clear_content(self):
        self.editor.setPlainText('')


    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Open file',
            directory='',
            filter=self.filterTypes
        )

        if path:
            try:
                with open(path, 'r') as f:
                    text = f.read()
                    f.close()
            except Exception as e:
                self.dialog_message(str(e))
            else:
                self.path = path
                self.editor.setPlainText(text)
                self.update_title()

    def file_save(self):
        if self.path is None:
            self.file_saveAs()
        else:
            try:
                text = self.editor.toPlainText()
                with open(self.path, 'w')as f:
                    f.write(text)
                    f.close()
            except Exception as e:
                self.dialog_message(str(e))


    def file_saveAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            'Save file',
            '',
            self.filterTypes
        )

        text = self.editor.toPlainText()

        if not path:
            return
        else:
            try:
                with open(path, 'w')as f:
                    f.write(text)
                    f.close()
            except Exception as e:
                self.dialog_message(str(e))
            else:
                self.path = path
                self.update_title()

    def print_file(self):
        printDialog = QPrintDialog()
        if printDialog.exec_():
            self.editor.print_(printDialog.printer())

    def update_title(self):
        self.setWindowTitle('{0} - Notepad'.format(os.path.basename(self.path) if self.path else 'Untitled'))


    def dialog_message(self, message):
        dialog = QMessageBox(self)
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Critical)
        dialog.show()



    def create_action(self, parent, icon_path, action_name, set_status_tip, triggered_method):
        action = QAction(QIcon(icon_path), action_name, parent)
        action.setStatusTip(set_status_tip)
        action.triggered.connect(triggered_method)
        return action



app = QApplication(sys.argv)
note_pad = AppDemo()
note_pad.show()
sys.exit(app.exec_())
