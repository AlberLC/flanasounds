from PySide2 import QtWidgets, QtCore, QtGui

import controller
from config import resources
from my_qt.line_edits import ShortcutLineEdit
from my_qt.tree_widgets import SoundTreeWidget
from my_qt.ui_loader import load_ui
from my_qt.utils import set_active_style
from utils import resource_path

ENTER_KEY = 16777220
INTRO_KEY = 16777221


class Gui(QtWidgets.QWidget):
    label_folder: QtWidgets.QLabel
    label_output: QtWidgets.QLabel
    label_talk_key: QtWidgets.QLabel
    label_volume_selected: QtWidgets.QLabel
    label_volume_speakers: QtWidgets.QLabel

    line_folder: QtWidgets.QLineEdit
    line_talk_key: QtWidgets.QLineEdit

    button_folder: QtWidgets.QPushButton
    button_pause: QtWidgets.QPushButton
    button_stop: QtWidgets.QPushButton

    check_play_on_speakers: QtWidgets.QCheckBox

    combo_output: QtWidgets.QComboBox

    spin_volume_selected: QtWidgets.QSpinBox
    spin_volume_speakers: QtWidgets.QSpinBox

    slider_volume_selected: QtWidgets.QSlider
    slider_volume_speakers: QtWidgets.QSlider

    group_volume: QtWidgets.QGroupBox

    tree_sounds: QtWidgets.QTreeWidget

    def __init__(self):
        super().__init__()

        self._setup_gui()

    def _setup_gui(self):
        load_ui(resource_path('gui.ui'), self, [SoundTreeWidget, ShortcutLineEdit])

        self.button_folder.setIconSize(QtCore.QSize(20, 20))
        self.button_folder.setIcon(QtGui.QIcon(resource_path(resources['url_folder'])))
        self.button_pause.setIconSize(QtCore.QSize(20, 20))
        self.button_pause.setIcon(QtGui.QIcon(resource_path(resources['url_play'])))
        self.button_stop.setIconSize(QtCore.QSize(20, 20))
        self.button_stop.setIcon(QtGui.QIcon(resource_path(resources['url_stop'])))

        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.set_stop_mode()
        set_active_style(self.slider_volume_selected)
        set_active_style(self.slider_volume_speakers)

        self.label_loading_gif = QtWidgets.QLabel(self)
        self.label_loading_gif.setAlignment(QtCore.Qt.AlignCenter)
        self.label_loading_gif.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.label_loading_gif.setGeometry(self.tree_sounds.geometry())

    def resizeEvent(self, event):
        self.resize_gif()

    def showEvent(self, event):
        super().showEvent(event)
        self.resize_gif()

    def resize_gif(self):
        margin = 11
        frame_width = 1
        x = self.tree_sounds.x() + margin + frame_width
        y = self.tree_sounds.y() + margin + frame_width
        w = self.tree_sounds.width() - frame_width * 2
        h = self.tree_sounds.height() - frame_width * 2
        self.label_loading_gif.setGeometry(x, y, w, h)

    def connect_signals(self, controller: 'controller.Controller'):
        self.button_folder.clicked.connect(controller.open_explorer)
        self.button_pause.clicked.connect(controller.pause)
        self.button_stop.clicked.connect(controller.stop)

        self.check_play_on_speakers.stateChanged.connect(controller.checked_play_on_speakers)

        self.line_talk_key.textChanged.connect(controller.changed_talk_key)

        self.combo_output.currentIndexChanged.connect(controller.set_output)

        self.spin_volume_selected.valueChanged.connect(controller.changed_slected_output_volume_spin)
        self.spin_volume_speakers.valueChanged.connect(controller.changed_speakers_volume_spin)

        self.slider_volume_selected.valueChanged.connect(controller.changed_selected_output_volume_slider)
        self.slider_volume_speakers.valueChanged.connect(controller.changed_speakers_volume_slider)

        self.tree_sounds.connect_signals(controller)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (ENTER_KEY, INTRO_KEY):
            if self.spin_volume_selected.hasFocus():
                self.spin_volume_selected.clearFocus()
            elif self.spin_volume_speakers.hasFocus():
                self.spin_volume_speakers.clearFocus()
            elif self.slider_volume_selected.hasFocus():
                self.slider_volume_selected.clearFocus()
            elif self.slider_volume_speakers.hasFocus():
                self.slider_volume_speakers.clearFocus()

    def set_pause_mode(self):
        self.button_pause.setIcon(QtGui.QIcon(resource_path(resources['url_play'])))

    def set_play_mode(self):
        self.button_pause.setIcon(QtGui.QIcon(resource_path(resources['url_pause'])))
        self.button_pause.setEnabled(True)
        self.button_stop.setEnabled(True)

    def set_stop_mode(self):
        self.set_pause_mode()
        self.button_pause.setEnabled(False)
        self.button_stop.setEnabled(False)
