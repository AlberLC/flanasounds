from PySide2 import QtGui, QtWidgets, QtCore

import controller as controller_module
from my_qt.utils import set_inative_style

KEY_0 = 48
KEY_9 = 57
KEY_APOSTROPHE = 39
KEY_EXCLAMATION = 161
KEY_PLUS = 43
KEY_MINUS = 45
KEY_PERIOD = 46

OFFSET_DICT_KEY = 49


class NoFocusDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index):
        if option.state & QtWidgets.QStyle.State_HasFocus:
            option.state = option.state ^ QtWidgets.QStyle.State_HasFocus
        super().paint(painter, option, index)


class CategoryTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, index, name):
        super().__init__()
        self.name = name

        prefix = controller_module.VK_TO_CATEGORY.get(index + OFFSET_DICT_KEY, '')
        self.setText(0, f'{prefix:>2} ----- {name} -----')


class SoundTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, index, name):
        super().__init__()
        self.name = name

        prefix = f"{f'{index + 1:>1}.' if index < 9 else ''}"
        self.setText(0, f'{prefix:>2} {name}')


class SoundTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = None

        set_inative_style(self)
        self.setItemDelegate(NoFocusDelegate())

    def _rename_item_prefixes(self, parent, sounds: dict):
        if parent is None:
            items = (self.topLevelItem(i) for i in range(self.topLevelItemCount()))
            sounds_aux = sounds.copy()
            sounds.clear()
            for i, item in enumerate(items, start=OFFSET_DICT_KEY):
                prefix = controller_module.VK_TO_CATEGORY.get(i, '')
                print(prefix)
                item.setText(0, f'{prefix:>2}{item.text(0)[2:]}')
                sounds[item.name] = sounds_aux[item.name]
        else:
            items = (parent.child(i) for i in range(parent.childCount()))
            category_aux = sounds[parent.name]
            sounds[parent.name] = {}
            for i, item in enumerate(items, start=1):
                prefix = f"{f'{i:>1}.' if i < 10 else ''}"
                item.setText(0, f'{prefix:>2}{item.text(0)[2:]}')
                sounds[parent.name][item.name] = category_aux[item.name]

    def connect_signals(self, controller: 'controller_module.Controller'):
        self.controller = controller

        self.currentItemChanged.connect(lambda: controller.changed_tree_selection(self.currentItem()),
                                        QtCore.Qt.QueuedConnection)
        self.itemActivated.connect(controller.activated_item)

    def focusInEvent(self, event):
        current_item = self.currentItem()
        super().focusInEvent(event)
        self.setCurrentItem(current_item)

    def dropEvent(self, event):
        item = self.currentItem()
        old_parent = item.parent()
        if old_parent is None:
            old_index = self.indexOfTopLevelItem(item)
        else:
            old_index = old_parent.indexOfChild(item)

        super().dropEvent(event)

        new_parent = item.parent()

        if new_parent is old_parent:
            self._rename_item_prefixes(old_parent, self.controller.sounds)
        else:
            if new_parent is None:
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            else:
                new_parent.takeChild(new_parent.indexOfChild(item))
            if old_parent is None:
                self.insertTopLevelItem(old_index, item)
            else:
                old_parent.insertChild(old_index, item)

        self.setCurrentItem(item)
        self.controller.save_sounds()

    def keyPressEvent(self, event):
        if (
                event.key() not in (*range(KEY_0, KEY_9 + 1),
                                    KEY_APOSTROPHE,
                                    KEY_EXCLAMATION,
                                    KEY_PLUS,
                                    KEY_MINUS,
                                    KEY_PERIOD)
                and
                self.controller.talk_key != event.text()
        ):
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if not self.itemAt(event.pos()):
            self.setCurrentItem(None)
        super().mousePressEvent(event)
