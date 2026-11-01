# -*- coding: utf-8 -*-
"""ark_nuke root init — runs for every Nuke session (GUI and -t)."""
from __future__ import print_function

import os
import nuke

_ROOT = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

_ROOT_SUBPATHS = (
    "gizmos",
    "python",
    # nk_files intentionally NOT on pluginPath: Nuke auto-indexes */ToolSets
    # and would duplicate Ark toolbar entries (e.g. ContactSheetPro_v1.1).
    # ToolSets are registered only via menu.py _add_nk_commands -> Nodes/Ark.
    "icons",
)

for _sub in _ROOT_SUBPATHS:
    nuke.pluginAddPath("%s/%s" % (_ROOT, _sub))

# Practical Python plugin folders under python/ (hyphen names need their own
# pluginAddPath so modules import without package wrappers). custom_cmd is
# intentionally omitted: its menu.py is a platform-startup runner, not a safe
# auto-load UI module. NukeSurvivalToolkit lives in third_party/ — do not list
# it here.
# Cryptomatte / tabtabtab-nuke / max-van-leeuwen (WrapItUp) / ddot removed
# 2026-11-01 so fresh downloads can be dropped in later; re-add paths then.
_PYTHON_PLUGIN_SUBPATHS = ()

for _sub in _PYTHON_PLUGIN_SUBPATHS:
    nuke.pluginAddPath("%s/python/%s" % (_ROOT, _sub))

# ---------------------------------------------------------------------------
# third_party/: one GitHub repo per subdirectory (see third_party/README.md)
# Also mounts the third_party root so loose modules (e.g. dDot.py) import.
# ---------------------------------------------------------------------------
_THIRD_PARTY_ROOT = os.path.join(_ROOT.replace("/", os.sep), "third_party")
_THIRD_PARTY_SUBDIRS = ("gizmos", "python", "icons", "nk_files", "images")
_loaded_packages = []
_loose_modules = []

if os.path.isdir(_THIRD_PARTY_ROOT):
    # Root path: enables `import dDot` for third_party/dDot.py and similar.
    nuke.pluginAddPath(_THIRD_PARTY_ROOT.replace("\\", "/"))
    for _name in sorted(os.listdir(_THIRD_PARTY_ROOT)):
        if _name.startswith(".") or _name == "README.md":
            continue
        _pkg = os.path.join(_THIRD_PARTY_ROOT, _name)
        if os.path.isfile(_pkg) and _name.endswith(".py") and not _name.startswith("_"):
            _loose_modules.append(_name[:-3])
            continue
        if not os.path.isdir(_pkg):
            continue
        if _name.startswith("_"):
            continue
        _pkg_posix = _pkg.replace("\\", "/")
        nuke.pluginAddPath(_pkg_posix)
        for _sub in _THIRD_PARTY_SUBDIRS:
            _sub_abs = os.path.join(_pkg, _sub)
            if os.path.isdir(_sub_abs):
                nuke.pluginAddPath(_sub_abs.replace("\\", "/"))
        _loaded_packages.append(_name)

print(
    "[ark_nuke] third_party: loaded %d packages: %s | loose modules: %s"
    % (
        len(_loaded_packages),
        ", ".join(_loaded_packages) if _loaded_packages else "(none)",
        ", ".join(_loose_modules) if _loose_modules else "(none)",
    )
)

_major = int(nuke.NUKE_VERSION_MAJOR)
_minor = int(nuke.NUKE_VERSION_MINOR)
_full = "%s.%s" % (_major, _minor)

# Light version gating (no third-party imports at load time).
# Nuke < 13 typically used PySide2; Nuke 13+ / 16 use Qt6 / PySide6 when GUI.
if _major < 13:
    _qt_note = "PySide2 era (Nuke < 13)"
else:
    _qt_note = "PySide6 / Qt6-capable (Nuke >= 13); Nuke16 uses PySide6"

print("[ark_nuke] loaded | Nuke %s | %s | root=%s" % (_full, _qt_note, _ROOT))