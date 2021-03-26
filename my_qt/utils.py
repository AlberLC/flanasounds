from PySide2 import QtGui


def set_active_style(widget):
    palette = widget.palette()
    palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight,
                     palette.color(QtGui.QPalette.Active, QtGui.QPalette.Highlight))
    palette.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText,
                     palette.color(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
    widget.setPalette(palette)


def set_inative_style(widget):
    palette = widget.palette()
    palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Highlight,
                     palette.color(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight))
    palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText,
                     palette.color(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText))
    widget.setPalette(palette)
