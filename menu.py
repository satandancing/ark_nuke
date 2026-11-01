# -*- coding: utf-8 -*-
"""ark_nuke GUI menu — only interpreted when nuke.GUI is true."""
from __future__ import print_function

import os
import nuke

_ROOT = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
_PY = _ROOT + "/python"
_THIRD_PARTY = _ROOT + "/third_party"


def _wrapitup_run():
    try:
        import WrapItUp
    except ImportError as exc:
        nuke.message("[Ark] WrapItUp import failed: %s" % exc)
        return
    try:
        WrapItUp.WrapItUp()
    except Exception as exc:
        nuke.message("[Ark] WrapItUp() error: %s" % exc)


def _tabtabtab_run():
    """Launch Tabtabtab palette (also registered on Tab via its own menu.py)."""
    try:
        import tabtabtab_nuke
        from tabtabtab_nuke_core import launch
    except ImportError as exc:
        nuke.message("[Ark] tabtabtab import failed: %s" % exc)
        return
    try:
        tabtabtab_nuke.registerNukeAction()
        launch(tabtabtab_nuke._plugin)
    except Exception as exc:
        nuke.message("[Ark] tabtabtab launch error: %s" % exc)


def _tabtabtab_prefs():
    try:
        import tabtabtab_prefs_dialog
    except ImportError as exc:
        nuke.message("[Ark] tabtabtab prefs import failed: %s" % exc)
        return
    try:
        tabtabtab_prefs_dialog.show_prefs_dialog()
    except Exception as exc:
        nuke.message("[Ark] tabtabtab prefs error: %s" % exc)


def _ddot_import():
    """Import dDot (Nodes toolbar backpack + hotkeys; Nuke menubar backpack suppressed)."""
    try:
        import dDot  # noqa: F401
        return True
    except Exception as exc:
        nuke.message("[Ark] dDot import failed: %s" % exc)
        return False


def _ddot_call(fn_name):
    try:
        import dDot as ddot
    except ImportError as exc:
        nuke.message("[Ark] dDot import failed: %s" % exc)
        return
    fn = getattr(ddot, fn_name, None)
    if fn is None:
        nuke.message("[Ark] dDot missing %s" % fn_name)
        return
    try:
        fn()
    except Exception as exc:
        nuke.message("[Ark] dDot.%s error: %s" % (fn_name, exc))


def _custom_cmd_status():
    import sys
    base = os.path.join(_PY.replace("/", os.sep), "custom_cmd")
    plat = os.path.join(base, sys.platform)
    exists = os.path.isdir(plat)
    msg = "[Ark] custom_cmd | dir=%s | platform scripts (%s) exist=%s | not auto-run (no license/startup side effects)" % (
        base, sys.platform, exists)
    print(msg)
    nuke.message(msg)


def _list_python_plugins():
    entries = []
    py_fs = _PY.replace("/", os.sep)
    if os.path.isdir(py_fs):
        for name in sorted(os.listdir(py_fs)):
            if name.startswith(".") or name == "__pycache__":
                continue
            path = os.path.join(py_fs, name)
            kind = "dir" if os.path.isdir(path) else "file"
            entries.append("%s (%s)" % (name, kind))
    msg = "[Ark] python/ contents:\n- " + "\n- ".join(entries)
    print(msg)
    nuke.message(msg)


def _list_third_party_packages():
    """Discover third_party packages (same rules as init.py loader)."""
    tp_fs = _THIRD_PARTY.replace("/", os.sep)
    entries = []
    if not os.path.isdir(tp_fs):
        msg = "[Ark] third_party/ missing: %s" % tp_fs
        print(msg)
        nuke.message(msg)
        return
    std = ("gizmos", "python", "icons", "nk_files", "images")
    for name in sorted(os.listdir(tp_fs)):
        if name.startswith(".") or name == "README.md":
            continue
        path = os.path.join(tp_fs, name)
        if os.path.isfile(path) and name.endswith(".py") and not name.startswith("_"):
            entries.append("%s | loose module (.py at third_party root)" % name)
            continue
        if not os.path.isdir(path):
            continue
        if name.startswith("_"):
            continue
        has_init = os.path.isfile(os.path.join(path, "init.py"))
        has_menu = os.path.isfile(os.path.join(path, "menu.py"))
        subs = [s for s in std if os.path.isdir(os.path.join(path, s))]
        entries.append(
            "%s | init=%s menu=%s subdirs=[%s]"
            % (name, has_init, has_menu, ", ".join(subs) if subs else "-")
        )
    if not entries:
        msg = "[Ark] third_party: no packages found under %s" % tp_fs
    else:
        msg = "[Ark] third_party packages (%d):\n- %s" % (len(entries), "\n- ".join(entries))
    print(msg)
    nuke.message(msg)



def _crypto_call(fn_name):
    """Call a cryptomatte_utilities entry (package menu.py also registers Nodes toolbar)."""
    try:
        import cryptomatte_utilities as cu
    except ImportError as exc:
        nuke.message("[Ark] cryptomatte_utilities import failed: %s" % exc)
        return
    fn = getattr(cu, fn_name, None)
    if fn is None:
        nuke.message("[Ark] cryptomatte_utilities missing %s" % fn_name)
        return
    try:
        fn()
    except Exception as exc:
        nuke.message("[Ark] cryptomatte_utilities.%s error: %s" % (fn_name, exc))


def _ark_edit_batch_replace():
    try:
        from ark_edit_tools import actions as _aea
        _aea.replace_file_path_dialog(batch_all_reads=True)
    except Exception as exc:
        nuke.message("[Ark] batch replace failed: %s" % exc)


def _ark_edit(fn_name):
    """Run ark_edit_tools.actions helper; selection errors already messaged."""
    try:
        from ark_edit_tools import actions as _aea
    except ImportError as exc:
        nuke.message("[Ark] ark_edit_tools import failed: %s" % exc)
        return
    fn = getattr(_aea, fn_name, None)
    if fn is None:
        nuke.message("[Ark] ark_edit_tools missing %s" % fn_name)
        return
    try:
        fn()
    except RuntimeError:
        return
    except Exception as exc:
        nuke.message("[Ark] %s error: %s" % (fn_name, exc))



# Stamps (third_party/Stamps-1.2.0): package registers Edit/Stamps + Nodes/Other/Stamps;
# Ark mirrors primary actions. Qt via qt_compat / stamps.py local fallback.
def _stamps_import():
    try:
        import stamps as _stamps_mod
        return _stamps_mod
    except Exception as exc:
        nuke.message("[Ark] stamps import failed: %s" % exc)
        return None

def _stamps_call(fn_name, *args, **kwargs):
    mod = _stamps_import()
    if mod is None:
        return
    fn = getattr(mod, fn_name, None)
    if fn is None:
        nuke.message("[Ark] stamps missing %s" % fn_name)
        return
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        nuke.message("[Ark] stamps.%s error: %s" % (fn_name, exc))


menubar = nuke.menu("Nuke")
m = menubar.addMenu("Ark", icon="Ark.png")
m.addSeparator()
m.addCommand("List python plugins", _list_python_plugins)
m.addCommand("List third_party packages", _list_third_party_packages)
m.addSeparator()

# third_party mounts (paths from init.py; package menu.py also auto-loads)
m.addCommand("WrapItUp", _wrapitup_run)
m.addCommand("Tabtabtab", _tabtabtab_run)
m.addCommand("Tabtabtab Preferences...", _tabtabtab_prefs)

sm = m.addMenu("Stamps", icon="stamps.png")
sm.addCommand("Make Stamp", lambda: _stamps_call("goStamp"), "F8", icon="stamps.png")
sm.addCommand("Add tag/s to selected nodes", lambda: _stamps_call("addTags"))
sm.addCommand("Rename Stamp tag", lambda: _stamps_call("renameTag"))
sm.addCommand("Refresh all Stamps", lambda: _stamps_call("refreshStamps"))
sm.addSeparator()
_sms = sm.addMenu("Selected")
_sms.addCommand("Reconnect by Name", lambda: _stamps_call("selectedReconnectByName"))
_sms.addCommand("Reconnect by Title", lambda: _stamps_call("selectedReconnectByTitle"))
_sms.addCommand("Reconnect by Selection", lambda: _stamps_call("selectedReconnectBySelection"))
_sms.addCommand("Refresh", lambda: _stamps_call("refreshStamps", __import__("nuke").selectedNodes()))
_sms.addCommand("Select Similar", lambda: _stamps_call("selectedSelectSimilar"))
_sms.addCommand("Toggle auto-rec by title", lambda: _stamps_call("selectedToggleAutorec"))
_sma = sm.addMenu("Advanced")
_sma.addCommand("Convert all Stamps to NoOp", lambda: _stamps_call("allToNoOp"))
sm.addSeparator()
sm.addCommand("Documentation (.pdf)", lambda: _stamps_call("showHelp"))
sm.addCommand("Video tutorials", lambda: _stamps_call("showVideo"))
sm.addCommand("GitHub", lambda: _stamps_call("showInGithub"))
sm.addCommand("Nukepedia", lambda: _stamps_call("showInNukepedia"))

# Cryptomatte: package menu.py registers Nodes/Cryptomatte; Ark mirrors create/decrypt helpers.
cm = m.addMenu("Cryptomatte")
cm.addCommand("Cryptomatte", lambda: _crypto_call("cryptomatte_create_gizmo"))
cm.addCommand("Decryptomatte All", lambda: _crypto_call("decryptomatte_all"))
cm.addCommand("Decryptomatte Selection", lambda: _crypto_call("decryptomatte_selected"))
cm.addCommand("Encryptomatte", lambda: _crypto_call("encryptomatte_create_gizmo"))

dd = m.addMenu("dDot")
dd.addCommand("Import dDot module", _ddot_import)
dd.addCommand("dDotParent", lambda: _ddot_call("dDotParent"))
dd.addCommand("dDotConnect", lambda: _ddot_call("dDotConnect"))
dd.addCommand("dDotConnectSelected", lambda: _ddot_call("dDotConnectSelected"))
dd.addCommand("dDotCheckInput", lambda: _ddot_call("dDotCheckInput"))
dd.addCommand("dDotAutoConnect", lambda: _ddot_call("dDotAutoConnect"))
dd.addCommand("dDotShowChildren", lambda: _ddot_call("dDotShowChildren"))
dd.addCommand("dDotToggleConnectionsVisibility", lambda: _ddot_call("dDotToggleConnectionsVisibility"))
dd.addCommand("dDotRollDownNameChange", lambda: _ddot_call("dDotRollDownNameChange"))
dd.addCommand("dDotGrabParentName", lambda: _ddot_call("dDotGrabParentName"))
dd.addCommand("dDotSelectChildren", lambda: _ddot_call("dDotSelectChildren"))

# Eager-import dDot so Nodes/hotkeys register; Nuke menubar backpack stays off.
_ddot_import()

# ----- 编辑 / 工具（自 nuke_plugins 对应菜单整合；吾立方专有项未迁入）-----
# 已有 Ark 能力不重复：WrapItUp≈打包、Cryptomatte/dDot/Tabtabtab 各用其子菜单。
_edit = m.addMenu("编辑")
_edit.addCommand("查找最大 BBox", lambda: _ark_edit("show_max_bbox_node"))
_edit.addCommand("替换文件路径...", lambda: _ark_edit("replace_file_path_dialog"))
_edit.addCommand("转换为序列路径", lambda: _ark_edit("convert_to_sequence_path"))
_edit.addCommand("转换为相对路径", lambda: _ark_edit("convert_to_relative_path"))
_edit.addCommand("打开文件所在目录", lambda: _ark_edit("open_file_directory"), "shift+b")
_edit.addCommand("自动摆放(竖式)", lambda: _ark_edit("auto_place_vertical"))
_el = _edit.addMenu("稍后启用")
_el.addCommand("标记", lambda: _ark_edit("enable_later_mark"), "shift+d")
_el.addCommand("禁用已标记", lambda: _ark_edit("enable_later_disable"), "ctrl+shift+d")
_el.addCommand("启用已标记", lambda: _ark_edit("enable_later_enable"))
_el.addCommand("选择已标记", lambda: _ark_edit("enable_later_select"))
_edit.addSeparator()
_edit.addCommand("Read: 修复错误", lambda: _ark_edit("fix_error_reads"), icon="Read.png")
_edit.addCommand("Shuffle: 拆分图层", lambda: _ark_edit("split_layers_shuffle"), icon="Shuffle.png")
_edit.addCommand("Shuffle: 拆分 rgba", lambda: _ark_edit("split_rgba"), icon="Shuffle.png")
_edit.addCommand("Shuffle: 正则拆分图层组...", lambda: _ark_edit("split_layer_group_by_re_dialog"), icon="Shuffle.png")
_edit.addCommand("Gizmo: 转为 Group", lambda: _ark_edit("gizmo_to_group"), icon="Group.png")
_edit.addCommand("Write: 输出当前帧 PNG", lambda: _ark_edit("render_current_frame_png"), icon="Write.png")
_edit.addCommand("Dot: 输入连线加 Dot", lambda: _ark_edit("add_dot_on_inputs_90"), icon="Dot.png")
_edit.addCommand("切换 postage stamp", lambda: _ark_edit("toggle_postage_stamp"))
_edit.addCommand("切换 hide input", lambda: _ark_edit("toggle_hide_input"))
_edit.addCommand("AutoCrop", lambda: _ark_edit("autocrop_selected"))
_edit.addCommand("Glow: 用 width 代替 mask", lambda: _ark_edit("replace_glow_mask_with_width"), icon="Glow.png")
_edit.addCommand("Backdrop: 重命名内部节点", lambda: _ark_edit("rename_nodes_by_backdrop"), icon="Backdrop.png")

_tools = m.addMenu("工具")
_tools.addCommand("查找空文件夹...", lambda: _ark_edit("find_empty_dirs_dialog"))
_tools.addCommand(
    "批量替换文件路径...",
    lambda: _ark_edit_batch_replace(),
)


_tools.addCommand("预设 Backdrop...", lambda: _ark_edit("preset_backdrop_dialog"), icon="Backdrop.png")
_tools.addCommand("单帧转序列", lambda: _ark_edit("single_frame_reads_to_sequence"), icon="Read.png")
# NST: full toolkit lives in third_party/NukeSurvivalToolkit and provides its own menu.py.
# Old Ark NST helpers (partial python/NukeSurvivalToolkit) removed.

# custom_cmd — status only
m.addCommand("custom_cmd status", _custom_cmd_status)

# ---------------------------------------------------------------------------
# Nodes side toolbar: Ark — gizmos under gizmos/ including gizmos/third_party/
# as submenu Ark/third_party (folder-mirrored). Skips Obsolete/. Does NOT touch
# third_party/NukeSurvivalToolkit (separate NST menu). Icons from icons/.
# ---------------------------------------------------------------------------
_GIZMO_ROOT = os.path.join(_ROOT.replace("/", os.sep), "gizmos")
_ICON_ROOT = os.path.join(_ROOT.replace("/", os.sep), "icons")
_TOOLSETS_ROOT = os.path.join(_ROOT.replace("/", os.sep), "nk_files", "ToolSets")
_GIZMO_DIR_IGNORE = frozenset(("Obsolete", "__pycache__"))  # third_party under Ark/third_party


def _resolve_icon(name):
    """Return icon filename if present under icons/ (on Nuke plugin path)."""
    for ext in (".png", ".svg"):
        candidate = os.path.join(_ICON_ROOT, name + ext)
        if os.path.isfile(candidate):
            return name + ext
    return None


def _add_gizmo_commands(menu, directory):
    """Recursively register .gizmo commands; subdirectories become submenus."""
    try:
        entries = os.listdir(directory)
    except OSError:
        return

    def _order(name):
        path = os.path.join(directory, name)
        return (not os.path.isdir(path), name.lower())

    for entry in sorted(entries, key=_order):
        if entry.startswith("."):
            continue
        path = os.path.join(directory, entry)
        if os.path.isdir(path):
            if entry in _GIZMO_DIR_IGNORE:
                continue
            icon = _resolve_icon(entry)
            if icon:
                sub = menu.addMenu(entry, icon=icon)
            else:
                sub = menu.addMenu(entry)
            _add_gizmo_commands(sub, path)
            continue
        base, ext = os.path.splitext(entry)
        if ext.lower() != ".gizmo":
            continue
        icon = _resolve_icon(base)
        cmd = "nuke.createNode(%r)" % base
        if icon:
            menu.addCommand(base, cmd, icon=icon)
        else:
            menu.addCommand(base, cmd)


# ---------------------------------------------------------------------------
# ToolSets (.nk): mount nk_files/ToolSets/* onto the same Ark toolbar by folder
# category (Foundry ToolSet pattern: nuke.nodePaste with forward-slash paths).
_NK_DIR_IGNORE = frozenset(("__pycache__",))


def _add_nk_commands(menu, directory, counts=None):
    """Recursively register .nk paste commands; subdirectories become submenus.

    Uses Foundry ToolSet pattern: nuke.nodePaste(forward_slash_path).
    Icons resolved from icons/ when basename matches.
    """
    if counts is None:
        counts = {}
    try:
        entries = os.listdir(directory)
    except OSError:
        return counts

    def _order(name):
        path = os.path.join(directory, name)
        return (not os.path.isdir(path), name.lower())

    for entry in sorted(entries, key=_order):
        if entry.startswith("."):
            continue
        path = os.path.join(directory, entry)
        if os.path.isdir(path):
            if entry in _NK_DIR_IGNORE:
                continue
            icon = _resolve_icon(entry)
            if icon:
                sub = menu.addMenu(entry, icon=icon)
            else:
                sub = menu.addMenu(entry)
            _add_nk_commands(sub, path, counts)
            continue
        base, ext = os.path.splitext(entry)
        if ext.lower() != ".nk":
            continue
        path_posix = path.replace("\\", "/")
        icon = _resolve_icon(base)
        cmd = "nuke.nodePaste(%r)" % path_posix
        if icon:
            menu.addCommand(base, cmd, icon=icon)
        else:
            menu.addCommand(base, cmd)
        try:
            rel_dir = os.path.relpath(directory, _TOOLSETS_ROOT).replace("\\", "/")
        except Exception:
            rel_dir = directory
        if rel_dir in (".", ""):
            rel_dir = "(ToolSets root)"
        counts[rel_dir] = counts.get(rel_dir, 0) + 1
    return counts


toolbar = nuke.toolbar("Nodes")
_ark_toolbar = toolbar.addMenu("Ark", icon="Ark.png")
if os.path.isdir(_GIZMO_ROOT):
    _add_gizmo_commands(_ark_toolbar, _GIZMO_ROOT)

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Nodes Tab: ark_edit_tools on Nodes toolbar (吾立方曾挂 Nodes/吾立方/命令).
# Ark 顶栏 alone is NOT indexed by Nuke Tab; Nodes toolbar commands are.
# Every Ark → 编辑 / 工具 entry must appear here (plus short aliases).
# ---------------------------------------------------------------------------
_nodes_stamps = _ark_toolbar.addMenu("Stamps", icon="stamps.png")
_nodes_stamps.addCommand(
    "Make Stamp",
    "import stamps; stamps.goStamp()",
    icon="stamps.png",
)
_nodes_stamps.addCommand(
    "Stamps",
    "import stamps; stamps.goStamp()",
    icon="stamps.png",
)
_nodes_stamps.addCommand(
    "Refresh all Stamps",
    "import stamps; stamps.refreshStamps()",
)

_nodes_edit = _ark_toolbar.addMenu("编辑")
_nodes_tools = _ark_toolbar.addMenu("工具")

_TAB_EDIT_COMMANDS = (
    ("查找最大 BBox", "show_max_bbox_node", None),
    ("替换文件路径...", "replace_file_path_dialog", "Read.png"),
    ("转换为序列路径", "convert_to_sequence_path", None),
    ("转换为相对路径", "convert_to_relative_path", None),
    ("打开文件所在目录", "open_file_directory", None),
    ("自动摆放(竖式)", "auto_place_vertical", None),
    ("Read: 修复错误", "fix_error_reads", "Read.png"),
    ("Shuffle: 拆分图层", "split_layers_shuffle", "Shuffle.png"),
    ("Shuffle: 拆分 rgba", "split_rgba", "Shuffle.png"),
    ("Shuffle: 正则拆分图层组...", "split_layer_group_by_re_dialog", "Shuffle.png"),
    ("Gizmo: 转为 Group", "gizmo_to_group", "Group.png"),
    ("Write: 输出当前帧 PNG", "render_current_frame_png", "Write.png"),
    ("Dot: 输入连线加 Dot", "add_dot_on_inputs_90", "Dot.png"),
    ("切换 postage stamp", "toggle_postage_stamp", None),
    ("切换 hide input", "toggle_hide_input", None),
    ("AutoCrop", "autocrop_selected", None),
    ("Glow: 用 width 代替 mask", "replace_glow_mask_with_width", "Glow.png"),
    ("Backdrop: 重命名内部节点", "rename_nodes_by_backdrop", "Backdrop.png"),
)
for _label, _fn, _icon in _TAB_EDIT_COMMANDS:
    _cmd = "from ark_edit_tools import actions as _aea; getattr(_aea, %r)()" % _fn
    if _icon:
        _nodes_edit.addCommand(_label, _cmd, icon=_icon)
    else:
        _nodes_edit.addCommand(_label, _cmd)

_nodes_el = _nodes_edit.addMenu("稍后启用")
for _label, _fn in (
    ("标记", "enable_later_mark"),
    ("禁用已标记", "enable_later_disable"),
    ("启用已标记", "enable_later_enable"),
    ("选择已标记", "enable_later_select"),
):
    _nodes_el.addCommand(
        _label,
        "from ark_edit_tools import actions as _aea; getattr(_aea, %r)()" % _fn,
    )

_TAB_TOOLS_COMMANDS = (
    ("查找空文件夹...", "find_empty_dirs_dialog", None),
    ("批量替换文件路径...", "batch_replace_file_path_dialog", "Read.png"),
    ("预设 Backdrop...", "preset_backdrop_dialog", "Backdrop.png"),
    ("单帧转序列", "single_frame_reads_to_sequence", "Read.png"),
)
for _label, _fn, _icon in _TAB_TOOLS_COMMANDS:
    _cmd = "from ark_edit_tools import actions as _aea; getattr(_aea, %r)()" % _fn
    if _icon:
        _nodes_tools.addCommand(_label, _cmd, icon=_icon)
    else:
        _nodes_tools.addCommand(_label, _cmd)

# Short Chinese aliases for Tab search (吾立方风格)
_TAB_ALIASES = (
    (_nodes_edit, "拆分图层", "split_layers_shuffle", "Shuffle.png"),
    (_nodes_edit, "拆分rgba", "split_rgba", "Shuffle.png"),
    (_nodes_edit, "拆分 RGBA", "split_rgba", "Shuffle.png"),
    (_nodes_edit, "正则拆分图层组", "split_layer_group_by_re_dialog", "Shuffle.png"),
    (_nodes_edit, "相对路径", "convert_to_relative_path", None),
    (_nodes_edit, "序列路径", "convert_to_sequence_path", None),
    (_nodes_tools, "空文件夹", "find_empty_dirs_dialog", None),
    (_nodes_tools, "批量替换", "batch_replace_file_path_dialog", "Read.png"),
    (_nodes_tools, "预设Backdrop", "preset_backdrop_dialog", "Backdrop.png"),
)
for _menu, _label, _fn, _icon in _TAB_ALIASES:
    _cmd = "from ark_edit_tools import actions as _aea; getattr(_aea, %r)()" % _fn
    if _icon:
        _menu.addCommand(_label, _cmd, icon=_icon)
    else:
        _menu.addCommand(_label, _cmd)

_nk_counts = {}
if os.path.isdir(_TOOLSETS_ROOT):
    _ark_toolbar.addSeparator()
    _nk_counts = _add_nk_commands(_ark_toolbar, _TOOLSETS_ROOT)

_nk_summary = ", ".join("%s=%s" % (k, _nk_counts[k]) for k in sorted(_nk_counts)) or "none"
_tab_total = len(_TAB_EDIT_COMMANDS) + 4 + len(_TAB_TOOLS_COMMANDS) + len(_TAB_ALIASES)
print(
    "[Ark] Nodes toolbar menu registered | gizmos=%s | toolsets=%s | nk_counts={%s} | tab_edit=%d"
    % (_GIZMO_ROOT, _TOOLSETS_ROOT, _nk_summary, _tab_total)
)
