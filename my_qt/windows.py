from PySide2 import QtCore, QtGui, QtWidgets

from config import resources
from utils import resource_path

translate = QtWidgets.QApplication.translate


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.icon = QtGui.QIcon(resource_path(resources['url_logo']))

        self.setWindowTitle('FlanaSounds')
        self.setWindowIcon(self.icon)
        self.show()

    def sizeHint(self):
        return QtCore.QSize(800, 500)
