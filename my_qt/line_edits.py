import keyboard
from PySide2 import QtCore, QtGui, QtWidgets

from config import resources
from utils import resource_path


class ShortcutLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hook = None
        self.pressed_keys = set()

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 4, 0)
        self.button_clear = QtWidgets.QPushButton()
        self.button_clear.setFlat(True)
        self.button_clear.setFixedSize(QtCore.QSize(20, 20))
        self.button_clear.setIconSize(QtCore.QSize(16, 16))
        self.button_clear.setIcon(QtGui.QIcon(resource_path(resources['url_cross'])))
        layout.addWidget(self.button_clear, 0, QtCore.Qt.AlignRight)

        self.button_clear.hide()

        self.button_clear.clicked.connect(self.clear)
        self.textChanged.connect(lambda: self.button_clear.setVisible(bool(self.text())))

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.pressed_keys = set()
        self.hook = keyboard.hook(self._key_event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        keyboard.unhook(self.hook)

    def _key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            self.pressed_keys.add(keyboard.normalize_name(event.name).lower().replace('mayusculas', 'shift'))
            self.setText(keyboard.get_hotkey_name(self.pressed_keys))
        else:
            self.pressed_keys.discard(event.name.lower().replace('mayusculas', 'shift'))
