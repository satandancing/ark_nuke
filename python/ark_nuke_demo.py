# -*- coding: utf-8 -*-
"""Tiny demo module safe on Nuke 16 / Python 3.11."""
from __future__ import print_function


def hello():
    """Return a short greeting for Script Editor / nuke.message."""
    return "[ark_nuke] hello from ark_nuke_demo (Py3-safe)"


def ping():
    """Return True so probe scripts can assert load."""
    return True
