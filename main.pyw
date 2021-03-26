import multiprocessing
import sys

from PySide2 import QtCore, QtWidgets

from controller import Controller
from gui import Gui
from my_qt.windows import MyWindow
from utils import resource_path

if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QtWidgets.QApplication([])
    app.setStyle('fusion')

    translator = QtCore.QTranslator(app)
    translator.load(resource_path(f'translations/{QtCore.QLocale().system().name()[:2]}_ES.qm'))
    app.installTranslator(translator)

    window = MyWindow()
    gui = Gui()
    window.setCentralWidget(gui)
    controller = Controller(gui)
    gui.connect_signals(controller)

    sys.exit(app.exec_())
