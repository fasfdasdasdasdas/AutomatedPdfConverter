from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QStyle,
    QFileDialog,
    QTextEdit
)
from PySide6.QtCore import QStandardPaths, QUrl, QFile, QSaveFile, QDir, Slot, QObject, Signal
from PySide6.QtGui import QTextCursor
import sys
from functions import getPdfFiles, mergePdfFiles

class MyStream(QObject):
    message = Signal(str)
    def __init__(self, parent=None):
        super(MyStream, self).__init__(parent)

    def write(self, message):
        self.message.emit(str(message))

class AppWidget(QWidget):
    """A widget to download a http file to a destination file"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Medicines Australia PDF Converter")

        self.link_box = QLineEdit()
        self.home_box = QLineEdit()
        self.dest_box = QLineEdit()
        self.filename_box = QLineEdit()
        self.start_button = QPushButton("Start")

        self.link_box.setPlaceholderText("Enter Extension of URL ...")

        self.home_box.setPlaceholderText("Enter Homepage URL ...")

        self.filename_box.setPlaceholderText("Enter Year ...")

        self._open_folder_action = self.dest_box.addAction(
            qApp.style().standardIcon(QStyle.SP_DirOpenIcon), QLineEdit.TrailingPosition
        )
        self._open_folder_action.triggered.connect(self.on_open_folder)

        self.textEdit = QTextEdit(self)
        #  Current QFile
        self.file = None

        #  Default destination dir
        self.dest_box.setText(
            QDir.fromNativeSeparators(
                QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
            )
        )

        # buttons bar layout
        hlayout = QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.start_button)

        # main layout
        vlayout = QVBoxLayout(self)
        vlayout.addWidget(self.home_box)
        vlayout.addWidget(self.link_box)
        vlayout.addWidget(self.dest_box)
        vlayout.addWidget(self.filename_box)
        vlayout.addStretch()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.textEdit)

        self.resize(400, 300)

        self.start_button.clicked.connect(self.start)

    def __del__(self):
        sys.stdout = sys.__stdout__

    @Slot()
    def on_open_folder(self):

        dir_path = QFileDialog.getExistingDirectory(
            self, "Open Directory", QDir.homePath(), QFileDialog.ShowDirsOnly
        )

        if dir_path:
            dest_dir = QDir(dir_path)
            self.dest_box.setText(QDir.fromNativeSeparators(dest_dir.path()))

    @Slot()
    def start(self):
        getPdfFiles(self.home_box.text(), self.link_box.text(), self.dest_box.text() + "/")
        mergePdfFiles(self.dest_box.text() + "/", self.filename_box.text())

    @Slot()
    def on_myStream_message(self, message):
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(message)

if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = AppWidget()
    w.show()

    myStream = MyStream()
    myStream.message.connect(w.on_myStream_message)

    sys.stdout = myStream  

    sys.exit(app.exec())