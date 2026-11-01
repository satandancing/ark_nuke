# -*- coding: utf-8 -*-
"""Unified Qt bindings for ark_nuke / third_party scripts.

Prefer PySide6 (Nuke 13+ / Nuke 16), fall back to PySide2 (Nuke < 13).
Import::

    from qt_compat import QtCore, QtGui, QtWidgets, Qt, is_pyside6, QT_API
    from qt_compat import dialog_exec

Do not edit third_party plugin sources to hard-require one binding; use this
shim or the same try/except order when a minimal local patch is needed.
"""
from __future__ import print_function

QT_API = None
is_pyside6 = False

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Qt

    QT_API = "PySide6"
    is_pyside6 = True
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import Qt

    QT_API = "PySide2"
    is_pyside6 = False


def dialog_exec(dialog):
    """Run QDialog.exec (PySide6) or exec_ (PySide2)."""
    if hasattr(dialog, "exec"):
        return dialog.exec()
    return dialog.exec_()
