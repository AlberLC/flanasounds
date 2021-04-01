from PySide2 import QtCore, QtGui, QtWidgets
from pynput import keyboard

from config import resources
from utils import resource_path


class ShortcutLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listener = None
        self.pressed_keys = set()
        self.sorted_pressed_keys = []

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
        self.listener = keyboard.Listener(on_press=self._pressed_key, on_release=self._release_key)
        self.listener.start()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.listener.stop()

    def _pressed_key(self, key):
        self.pressed_keys.add(self._normalize_key_name(self.listener.canonical(key)))
        self.set_pressed_keys(self.pressed_keys)

    def _normalize_key_name(self, key):
        if type(key) is keyboard.Key:
            return key.name
        else:
            return str(key).replace('Key.', '').replace("'", "")

    def _release_key(self, key):
        self.pressed_keys.discard(self._normalize_key_name(self.listener.canonical(key)))

    def set_pressed_keys(self, pressed_keys_):
        pressed_keys = pressed_keys_.copy()
        modifiers_in_order = ('ctrl', 'alt', 'alt_gr', 'shift')

        self.sorted_pressed_keys = [modifier for modifier in modifiers_in_order if modifier in pressed_keys]
        pressed_keys.difference_update(modifiers_in_order)
        self.sorted_pressed_keys.extend(pressed_keys)

        self.setText('+'.join(self.sorted_pressed_keys))
