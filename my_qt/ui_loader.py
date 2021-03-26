import re
from typing import Iterable

from PySide2 import QtCore
from PySide2.QtUiTools import QUiLoader


class UiLoader(QUiLoader):
    """
    Subclass :class:`~PySide.QtUiTools.QUiLoader` to create the user interface
    in a base instance.
    Unlike :class:`~PySide.QtUiTools.QUiLoader` itself this class does not
    create a new instance of the top-level widget, but creates the user
    interface in an existing instance of the top-level class.
    This mimics the behaviour of :func:`PyQt4.uic.loadUi`.
    """

    def __init__(self, base_instance, custom_widgets: Iterable):
        """
        Create a loader for the given ``baseinstance``.
        The user interface is created in ``baseinstance``, which must be an
        instance of the top-level class in the user interface to load, or a
        subclass thereof.
        ``customWidgets`` is a dictionary mapping from class name to class object
        for widgets that you've promoted in the Qt Designer interface. Usually,
        this should be done by calling registerCustomWidget on the QUiLoader, but
        with PySide 1.1.2 on Ubuntu 12.04 x86_64 this causes a segfault.
        ``parent`` is the parent object of this loader.
        """

        super().__init__(base_instance)
        self.base_instance = base_instance
        self.custom_widgets = {re.search("\.(\w+)'", str(cw)).groups()[0]: cw for cw in custom_widgets}

    def createWidget(self, class_name, parent=None, name=''):
        """
        Function that is called for each widget defined in ui file,
        overridden here to populate baseinstance instead.
        """

        if parent is None and self.base_instance:
            # supposed to create the top-level widget, return the base instance
            # instead
            return self.base_instance
        else:
            if class_name in self.availableWidgets():
                # create a new widget for child widgets
                widget = super().createWidget(class_name, parent, name)
            else:
                # if not in the list of availableWidgets, must be a custom widget
                # this will raise KeyError if the user has not supplied the
                # relevant class_name in the dictionary, or TypeError, if
                # customWidgets is None
                try:
                    widget = self.custom_widgets[class_name](parent)
                except (TypeError, KeyError) as e:
                    raise Exception(f'No custom widget {class_name} found in customWidgets param of UiLoader __init__.')

            if self.base_instance:
                # set an attribute for the new child widget on the base
                # instance, just like PyQt4.uic.loadUi does.
                setattr(self.base_instance, name, widget)

                # this outputs the various widget names, e.g.
                # sampleGraphicsView, dockWidget, samplesTableView etc.
                # print(name)

            return widget


def load_ui(ui_file, base_instance=None, custom_widgets=(), working_directory=None):
    """
    Dynamically load a user interface from the given ``uifile``.
    ``uifile`` is a string containing a file name of the UI file to load.
    If ``baseinstance`` is ``None``, the a new instance of the top-level widget
    will be created.  Otherwise, the user interface is created within the given
    ``baseinstance``.  In this case ``baseinstance`` must be an instance of the
    top-level widget class in the UI file to load, or a subclass thereof.  In
    other words, if you've created a ``QMainWindow`` interface in the designer,
    ``baseinstance`` must be a ``QMainWindow`` or a subclass thereof, too.  You
    cannot load a ``QMainWindow`` UI file with a plain
    :class:`~PySide.QtGui.QWidget` as ``baseinstance``.
    ``customWidgets`` is a dictionary mapping from class name to class object
    for widgets that you've promoted in the Qt Designer interface. Usually,
    this should be done by calling registerCustomWidget on the QUiLoader, but
    with PySide 1.1.2 on Ubuntu 12.04 x86_64 this causes a segfault.
    :method:`~PySide.QtCore.QMetaObject.connectSlotsByName()` is called on the
    created user interface, so you can implemented your slots according to its
    conventions in your widget class.
    Return ``baseinstance``, if ``baseinstance`` is not ``None``.  Otherwise
    return the newly created instance of the user interface.
    """

    loader = UiLoader(base_instance, custom_widgets)

    if working_directory is not None:
        loader.setWorkingDirectory(working_directory)

    widget = loader.load(ui_file)
    QtCore.QMetaObject.connectSlotsByName(widget)

    return widget
