# -*- coding: utf-8 -*-
"""Portable Edit/Tools actions for ark_nuke Ark menus.

Clean-room / community-style reimplementations of common workflows that
appeared under nuke_plugins 编辑/工具 and NukeToolSet ToolSet. Does NOT
import or ship wulifang license/vendor code.
"""
from __future__ import print_function

import os
import json
import re
import sys
import webbrowser

import nuke


def _selected_or_raise():
    nodes = nuke.selectedNodes()
    if not nodes:
        nuke.message("请先选择节点")
        raise RuntimeError("no selection")
    return nodes


def _one_or_raise():
    nodes = _selected_or_raise()
    if len(nodes) != 1:
        nuke.message("请只选择一个节点")
        raise RuntimeError("need one node")
    return nodes[0]


def _safe_call(fn):
    """Menu wrapper: swallow RuntimeError from selection helpers."""
    def _inner():
        try:
            fn()
        except RuntimeError:
            return
        except Exception as exc:
            nuke.message("%s 失败: %s" % (fn.__name__, exc))
    _inner.__name__ = fn.__name__
    return _inner


# ----- 编辑 -----

def show_max_bbox_node():
    biggest = None
    area = -1.0
    for n in nuke.allNodes():
        try:
            bbox = n.bbox()
            a = abs(float(bbox.w()) * float(bbox.h()))
        except Exception:
            continue
        if a > area:
            area = a
            biggest = n
    if biggest is None:
        nuke.message("未找到可用 BBox 的节点")
        return
    for n in nuke.allNodes():
        n.setSelected(False)
    biggest.setSelected(True)
    try:
        nuke.zoomToFitSelected()
    except Exception:
        pass
    nuke.message("最大 BBox: %s (area=%.0f)" % (biggest.name(), area))


def open_file_directory():
    nodes = _selected_or_raise()
    opened = []
    for n in nodes:
        knob = n.knob("file")
        if knob is None:
            continue
        path = nuke.callbacks.filenameFilter(knob.getValue())
        if not path:
            continue
        directory = os.path.dirname(path.replace("\\", "/"))
        if not directory:
            continue
        if os.path.isdir(directory):
            if sys.platform == "win32":
                os.startfile(directory)
            elif sys.platform == "darwin":
                os.system('open "%s"' % directory)
            else:
                webbrowser.open(directory)
            opened.append(directory)
        else:
            nuke.message("路径不存在:\n%s" % directory)
    if not opened:
        nuke.message("所选节点没有可用的 file 路径")


def replace_file_path_dialog(batch_all_reads=False):
    try:
        from qt_compat import QtWidgets, dialog_exec
    except Exception as exc:
        nuke.message("需要 Qt: %s" % exc)
        return

    class _Dlg(QtWidgets.QDialog):
        def __init__(self, parent=None):
            super(_Dlg, self).__init__(parent)
            self.setWindowTitle("批量替换文件路径" if batch_all_reads else "替换文件路径")
            self.resize(520, 120)
            lay = QtWidgets.QVBoxLayout(self)
            row1 = QtWidgets.QHBoxLayout()
            row1.addWidget(QtWidgets.QLabel("源路径"))
            self.src = QtWidgets.QLineEdit()
            row1.addWidget(self.src)
            row2 = QtWidgets.QHBoxLayout()
            row2.addWidget(QtWidgets.QLabel("目标路径"))
            self.dst = QtWidgets.QLineEdit()
            row2.addWidget(self.dst)
            btn = QtWidgets.QPushButton("替换")
            btn.clicked.connect(self._go)
            lay.addLayout(row1)
            lay.addLayout(row2)
            lay.addWidget(btn)

        def _go(self):
            src = str(self.src.text())
            dst = str(self.dst.text())
            if not src:
                nuke.message("源路径为空")
                return
            if batch_all_reads:
                nodes = list(nuke.allNodes("Read")) + list(nuke.allNodes("DeepRead"))
            else:
                nodes = [n for n in nuke.selectedNodes() if n.knob("file")]
                if not nodes:
                    nodes = list(nuke.allNodes("Read"))
            count = 0
            for n in nodes:
                knob = n.knob("file")
                if knob is None:
                    continue
                val = knob.getValue()
                if src in val:
                    knob.setValue(val.replace(src, dst))
                    count += 1
            nuke.message("已替换 %d 个节点" % count)
            self.accept()

    app = QtWidgets.QApplication.instance()
    parent = app.activeWindow() if app else None
    dialog_exec(_Dlg(parent))


def convert_to_sequence_path():
    nodes = [n for n in nuke.selectedNodes() if n.Class() in ("Read", "DeepRead")]
    if not nodes:
        nodes = list(nuke.allNodes("Read"))
    changed = 0
    frame_re = re.compile(r"^(?P<pre>.*)\.(?P<num>\d{4})\.(?P<ext>[^.]+)$")
    for node in nodes:
        file_name = node["file"].getValue().replace("\\", "/")
        folder = os.path.dirname(file_name)
        if not os.path.isdir(folder):
            continue
        frames = [
            f
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and f.lower() != "thumbs.db"
        ]
        matched = [frame_re.match(f) for f in frames]
        matched = [m for m in matched if m]
        if len(matched) < 2:
            continue
        # group by pre+ext
        groups = {}
        for m in matched:
            key = (m.group("pre"), m.group("ext"))
            groups.setdefault(key, []).append(int(m.group("num")))
        # pick group matching current file if possible
        base = os.path.basename(file_name)
        mb = frame_re.match(base)
        if mb:
            key = (mb.group("pre"), mb.group("ext"))
            nums = groups.get(key)
        else:
            key, nums = max(groups.items(), key=lambda kv: len(kv[1]))
        if not nums or max(nums) <= min(nums):
            continue
        seq = os.path.join(folder, "%s.%%04d.%s" % (key[0], key[1])).replace("\\", "/")
        node["file"].setValue(seq)
        first, last = min(nums), max(nums)
        for k, v in (("first", first), ("last", last), ("origfirst", first), ("origlast", last)):
            if node.knob(k):
                node[k].setValue(v)
        changed += 1
    nuke.message("已转换 %d 个 Read" % changed)


def convert_to_relative_path():
    script = nuke.root().name()
    if not script or script == "Root":
        nuke.message("请先保存工程脚本")
        return
    root_dir = os.path.dirname(script.replace("\\", "/"))
    count = 0
    for n in _selected_or_raise():
        knob = n.knob("file")
        if knob is None:
            continue
        path = knob.getValue().replace("\\", "/")
        if not path or not os.path.isabs(path):
            continue
        try:
            rel = os.path.relpath(path, root_dir).replace("\\", "/")
        except Exception:
            continue
        knob.setValue(rel)
        count += 1
    nuke.message("已转换 %d 个路径为相对路径" % count)


def auto_place_vertical():
    nodes = sorted(_selected_or_raise(), key=lambda n: n.ypos())
    x0 = nodes[0].xpos()
    y = nodes[0].ypos()
    gap = 80
    for n in nodes:
        n.setXpos(x0)
        n.setYpos(y)
        try:
            h = n.screenHeight()
        except Exception:
            h = 40
        y += max(h, 30) + gap


_ENABLE_LATER_KNOB = "ark_enable_later_names"


def _root_name_list():
    root = nuke.root()
    if root.knob(_ENABLE_LATER_KNOB) is None:
        root.addKnob(nuke.String_Knob(_ENABLE_LATER_KNOB, "Ark enable-later"))
        root[_ENABLE_LATER_KNOB].setVisible(False)
    raw = root[_ENABLE_LATER_KNOB].getValue() or ""
    return [x for x in raw.split("\n") if x]


def _save_name_list(names):
    nuke.root()[_ENABLE_LATER_KNOB].setValue("\n".join(sorted(set(names))))


def enable_later_mark():
    names = _root_name_list()
    sel = _selected_or_raise()
    for n in sel:
        names.append(n.name())
    _save_name_list(names)
    nuke.message("已标记 %d 个（合计 %d）" % (len(sel), len(_root_name_list())))


def enable_later_disable():
    for name in _root_name_list():
        n = nuke.toNode(name)
        if n is not None and n.knob("disable"):
            n["disable"].setValue(True)


def enable_later_enable():
    for name in _root_name_list():
        n = nuke.toNode(name)
        if n is not None and n.knob("disable"):
            n["disable"].setValue(False)


def enable_later_select():
    for n in nuke.allNodes():
        n.setSelected(False)
    for name in _root_name_list():
        n = nuke.toNode(name)
        if n:
            n.setSelected(True)


def fix_error_reads():
    exts = {".mov", ".jpg", ".tga", ".exr", ".jpeg", ".iff", ".tiff", ".png", ".dpx", ".mxf"}
    fixed = 0
    deleted = 0
    for node in list(nuke.allNodes("Read")):
        file_name = node["file"].getValue().replace("\\", "/")
        if os.path.isfile(file_name):
            if os.path.splitext(file_name)[-1].lower() not in exts:
                nuke.delete(node)
                deleted += 1
                continue
        token = None
        if "####" in file_name:
            token = "####"
        elif "%04d" in file_name:
            token = "%04d"
        if token:
            folder = os.path.dirname(file_name)
            if os.path.isdir(folder):
                prefix, _, suffix = file_name.partition(token)
                nums = []
                for fr in os.listdir(folder):
                    full = os.path.join(folder, fr).replace("\\", "/")
                    if not full.startswith(prefix):
                        continue
                    if suffix and not full.endswith(suffix):
                        continue
                    mid = full[len(prefix) : len(full) - len(suffix) if suffix else None]
                    if re.match(r"^\d{4}$", mid or ""):
                        nums.append(int(mid))
                if nums:
                    nums.sort()
                    for k, v in (
                        ("first", nums[0]),
                        ("last", nums[-1]),
                        ("origfirst", nums[0]),
                        ("origlast", nums[-1]),
                    ):
                        if node.knob(k):
                            node[k].setValue(v)
                    fixed += 1
        try:
            node.forceValidate()
        except Exception:
            pass
    nuke.message("修复帧范围 %d；删除异常 %d" % (fixed, deleted))


def split_layers_shuffle():
    for selected_node in _selected_or_raise():
        layers = sorted(set(ch.split(".")[0] for ch in selected_node.channels()))
        for channel in layers:
            sh = nuke.createNode("Shuffle", inpanel=False)
            sh["name"].setValue("%s_%s" % (channel, selected_node.name()))
            try:
                sh["in"].setValue(channel)
            except Exception:
                pass
            sh.setInput(0, selected_node)
            if sh.knob("postage_stamp"):
                sh["postage_stamp"].setValue(True)


def split_rgba():
    node = _one_or_raise()
    for label in ("red", "green", "blue", "alpha"):
        sh = nuke.createNode("Shuffle", inpanel=False)
        sh["name"].setValue("%s_%s" % (label, node.name()))
        try:
            sh["in"].setValue("rgba")
            for pipe in ("red", "green", "blue", "alpha"):
                if sh.knob(pipe):
                    sh[pipe].setValue(label if pipe != "alpha" or label == "alpha" else "black")
            # force mono preview of selected channel
            if sh.knob("red"):
                sh["red"].setValue(label)
                sh["green"].setValue(label)
                sh["blue"].setValue(label)
                sh["alpha"].setValue("alpha" if label == "alpha" else "black")
        except Exception:
            pass
        sh.setInput(0, node)


def gizmo_to_group():
    count = 0
    for n in list(_selected_or_raise()):
        try:
            if n.Class() == "Gizmo":
                # Nuke API: copy as group via execute
                group = n.makeGroup() if hasattr(n, "makeGroup") else None
                if group is None:
                    # alternate: expand then enclose — use nukescripts if present
                    try:
                        import nukescripts  # noqa: F401
                    except Exception:
                        pass
                    n["selected"].setValue(True)
                    # Foundry: Edit > Node > Convert Gizmo to Group is nukescripts
                    cmd = getattr(nuke, "convertSelectedGizmosToGroups", None)
                    if callable(cmd):
                        cmd()
                        count += 1
                        continue
                else:
                    count += 1
                    continue
            # try universal
            if hasattr(n, "makeGroup"):
                n.makeGroup()
                count += 1
        except Exception as exc:
            nuke.tprint("gizmo_to_group: %s" % exc)
    if count == 0:
        # last resort message with tip
        nuke.message("未能转换。请确认选中的是 Gizmo（部分版本可用 Edit > Node > Convert Gizmo to Group）。")
    else:
        nuke.message("已转换 %d 个" % count)


def render_current_frame_png():
    node = _one_or_raise()
    script = nuke.root().name()
    if script and script != "Root":
        out_dir = os.path.join(os.path.dirname(script), "_ark_png")
    else:
        out_dir = os.path.join(os.path.expanduser("~"), "nuke_ark_png")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    frame = int(nuke.frame())
    out = os.path.join(out_dir, "%s_%d.png" % (node.name(), frame)).replace("\\", "/")
    w = nuke.nodes.Write(file=out, file_type="png")
    w.setInput(0, node)
    try:
        nuke.execute(w, frame, frame)
    finally:
        nuke.delete(w)
    if sys.platform == "win32":
        os.startfile(out_dir)
    else:
        webbrowser.open(out_dir)
    nuke.message("已输出:\n%s" % out)


def add_dot_on_inputs_90():
    for n in _selected_or_raise():
        for i in range(n.inputs()):
            src = n.input(i)
            if src is None:
                continue
            dot = nuke.nodes.Dot()
            dot.setXYpos(int(src.xpos() + max(src.screenWidth(), 40) / 2), int(n.ypos() - 50))
            dot.setInput(0, src)
            n.setInput(i, dot)


def toggle_postage_stamp():
    sel = nuke.selectedNodes() or nuke.allNodes()
    knobs = [n.knob("postage_stamp") for n in sel if n.knob("postage_stamp") is not None]
    if not knobs:
        return
    val = not bool(knobs[0].getValue())
    for k in knobs:
        k.setValue(val)


def toggle_hide_input():
    sel = nuke.selectedNodes() or nuke.allNodes()
    knobs = [n.knob("hide_input") for n in sel if n.knob("hide_input") is not None]
    if not knobs:
        return
    val = not bool(knobs[0].getValue())
    for k in knobs:
        k.setValue(val)


def autocrop_selected():
    try:
        import nukescripts
        nukescripts.autocrop()
    except Exception as exc:
        nuke.message("AutoCrop 失败: %s" % exc)


def find_empty_dirs_dialog():
    start = nuke.getFilename("选择要扫描的根目录（选其中任意文件也可）")
    if not start:
        return
    if os.path.isfile(start):
        start = os.path.dirname(start)
    if not os.path.isdir(start):
        nuke.message("无效目录")
        return
    empties = []
    for root, dirs, files in os.walk(start):
        if not dirs and not files:
            empties.append(root)
    msg = "空文件夹 %d 个:\n%s" % (len(empties), "\n".join(empties[:80]))
    if len(empties) > 80:
        msg += "\n..."
    nuke.message(msg if empties else "未找到空文件夹")


# ----- Shuffle: 正则拆分图层组（吾立方同名能力的可移植重写，无 wulifang 依赖）-----

_SPLIT_RE_PREF = os.path.join(os.path.expanduser("~"), ".nuke", "ark_split_layer_group_byre.json")
_SPLIT_RE_DEFAULT = "(?i)_col$\n(?i)_sdw$"


def _load_split_re_pattern():
    try:
        with open(_SPLIT_RE_PREF, "r", encoding="utf-8") as f:
            data = json.load(f)
        p = data.get("pattern")
        if isinstance(p, str) and p.strip():
            return p
    except Exception:
        pass
    # migrate legacy wulifang prefs if present (read-only; do not require wulifang)
    legacy = os.path.expanduser("~/.nuke/wlf.shuffle_layers_byre.json")
    try:
        if os.path.isfile(legacy):
            with open(legacy, "r", encoding="utf-8") as f:
                data = json.load(f)
            p = data.get("pattern")
            if isinstance(p, str) and p.strip():
                return p
    except Exception:
        pass
    return _SPLIT_RE_DEFAULT


def _save_split_re_pattern(pattern):
    try:
        folder = os.path.dirname(_SPLIT_RE_PREF)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        with open(_SPLIT_RE_PREF, "w", encoding="utf-8") as f:
            json.dump({"pattern": pattern}, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        nuke.tprint("ark_edit_tools: save pattern failed: %s" % exc)


def _create_shuffle_for_layer(src, layer):
    sh = nuke.createNode("Shuffle", "in %s" % layer, False)
    sh.setInput(0, src)
    try:
        sh["label"].setValue(layer)
    except Exception:
        pass
    sh.setSelected(False)
    return sh


def _merge_plus_chain(shuffles, pattern_text):
    """Chain Merge2(operation=plus) for 2+ shuffles; return merge or single shuffle."""
    if not shuffles:
        return None
    if len(shuffles) == 1:
        return shuffles[0]
    label = "正则图层分组\n/%s/" % pattern_text
    current = shuffles[0]
    for nxt in shuffles[1:]:
        m = nuke.createNode("Merge2", "operation plus", False)
        m.setInput(0, current)
        m.setInput(1, nxt)
        try:
            m["label"].setValue(label)
        except Exception:
            pass
        m.setSelected(False)
        current = m
    return current


def split_layers_by_regex(nodes, pattern):
    """For each node, create Shuffles for layers matching pattern; plus-merge them.

    Returns list of created nodes (shuffles + merges).
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    created = []
    for node in nodes:
        matched = []
        try:
            layers = list(nuke.layers(node))
        except Exception:
            layers = []
        for layer in layers:
            if not pattern.search(layer):
                continue
            matched.append(_create_shuffle_for_layer(node, layer))
        created.extend(matched)
        if matched:
            merged = _merge_plus_chain(matched, pattern.pattern)
            if merged is not None and merged not in matched:
                created.append(merged)
            elif merged is not None and len(matched) == 1:
                pass
    return created


def split_layer_group_by_re_dialog(nodes=None):
    """Dialog: multiline regex (one per line) → split layer groups on selected nodes."""
    if nodes is None:
        nodes = list(nuke.selectedNodes())
    else:
        nodes = list(nodes)
    if not nodes:
        nuke.message("请先选择节点")
        return

    try:
        import nukescripts
    except Exception as exc:
        nuke.message("需要 nukescripts.PythonPanel: %s" % exc)
        return

    class _Panel(nukescripts.PythonPanel):
        def __init__(self):
            nukescripts.PythonPanel.__init__(self, "正则分离图层组")
            self.pattern_knob = nuke.Multiline_Eval_String_Knob("pattern", "正则匹配规则")
            self.addKnob(self.pattern_knob)
            self.pattern_knob.setValue(_load_split_re_pattern())
            self.addKnob(nuke.Text_Knob("hint", "", "每行一条正则；匹配到的图层各建 Shuffle，再 plus 合并。"))

    panel = _Panel()
    if not panel.showModalDialog():
        return
    raw_pattern = panel.pattern_knob.value() or ""
    _save_split_re_pattern(raw_pattern)
    lines = [ln for ln in raw_pattern.splitlines() if ln.strip()]
    if not lines:
        nuke.message("正则规则为空")
        return

    all_created = []
    errors = []
    for n in nodes:
        for raw in lines:
            try:
                pat = re.compile(raw)
            except re.error as exc:
                errors.append("%s → %s" % (raw, exc))
                continue
            all_created.extend(split_layers_by_regex([n], pat))

    # simple vertical place of created nodes next to first selection
    if all_created:
        base = nodes[0]
        x = base.xpos() + 200
        y = base.ypos()
        for i, cn in enumerate(all_created):
            try:
                cn.setXYpos(x + (i % 4) * 120, y + (i // 4) * 80)
            except Exception:
                pass
        for n in nuke.allNodes():
            n.setSelected(False)
        for cn in all_created:
            cn.setSelected(True)

    msg = "已创建 %d 个节点" % len(all_created)
    if errors:
        msg += "\n无效正则:\n" + "\n".join(errors[:10])
    nuke.message(msg)


def batch_replace_file_path_dialog():
    """Replace path substring on all Read/DeepRead (Ark 工具)."""
    replace_file_path_dialog(batch_all_reads=True)


def preset_backdrop_dialog():
    """NukeToolSet-style preset Backdrop (pure nuke.Panel; no wulifang)."""
    import colorsys
    import operator

    presets = ["Main", "CG", "Key", "Output", "Roto"]
    meta = {
        "Main": ("Main", "Glint.png", colorsys.hsv_to_rgb(0, 1, 0.5)),
        "CG": ("CG", "Shader.png", colorsys.hsv_to_rgb(0.062, 1, 0.5)),
        "Key": ("Key", "Keyer.png", colorsys.hsv_to_rgb(0.333, 1, 0.5)),
        "Output": ("Output", "Write.png", colorsys.hsv_to_rgb(0.167, 1, 0.373)),
        "Roto": ("Roto", "Roto.png", colorsys.hsv_to_rgb(0.333, 0.430, 0.384)),
    }
    p = nuke.Panel("预设 Backdrop")
    p.addEnumerationPulldown("Preset", " ".join(presets))
    p.addSingleLineInput("Custom Label", "")
    if not p.show():
        return
    custom_preset = p.value("Preset")
    custom_label = p.value("Custom Label") or ""
    if custom_preset not in meta:
        return
    preset_label, preset_icon, rgb = meta[custom_preset]
    r, g, b = rgb
    hex_colour = int("%02x%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255), 1), 16)
    icon = '<img src="%s"> ' % preset_icon if preset_icon else ""
    label = "<center>%s%s" % (icon, custom_label or preset_label)
    sel = list(nuke.selectedNodes())
    if not sel:
        nuke.nodes.BackdropNode(label=label, tile_color=hex_colour, note_font_size=30)
        return
    positions = [(i.xpos(), i.ypos()) for i in sel]
    x_pos = sorted(positions, key=operator.itemgetter(0))
    y_pos = sorted(positions, key=operator.itemgetter(1))
    x_min, x_max = x_pos[0][0], x_pos[-1][0]
    y_min, y_max = y_pos[0][1], y_pos[-1][1]
    n = nuke.nodes.BackdropNode(
        xpos=x_min - 10,
        bdwidth=x_max - x_min + 110,
        ypos=y_min - 85,
        bdheight=y_max - y_min + 160,
        label=label,
        tile_color=hex_colour,
        note_font_size=30,
    )
    n["selected"].setValue(False)
    for i in sel:
        i["selected"].setValue(True)
    return n


def single_frame_reads_to_sequence():
    """NukeToolSet Single To Sequence: expand single-frame Reads to %%04d sequences."""
    import re as _re

    def _frames(folder):
        try:
            names = os.listdir(folder)
        except Exception:
            return None
        names = [f for f in names if f != "Thumb.db" and os.path.isfile(os.path.join(folder, f))]
        return names if len(names) > 1 else None

    def _range(all_frames):
        pat = _re.compile(r".*\.(\d{4})\.[A-Za-z0-9]+$")
        nums = []
        for frame in all_frames:
            m = pat.match(frame)
            if m:
                nums.append(int(m.group(1)))
        if not nums:
            return None
        start, end = min(nums), max(nums)
        return (start, end) if end > start else None

    changed = 0
    for read_node in nuke.allNodes("Read"):
        file_name = read_node["file"].getValue().replace("\\", "/")
        folder = os.path.dirname(file_name)
        all_frames = _frames(folder)
        if not all_frames:
            continue
        replaced = _re.sub(r"\.\d{4}", ".%04d", all_frames[0])
        frame_ext = os.path.join(folder, replaced).replace("\\", "/")
        if file_name == frame_ext:
            continue
        read_node["file"].setValue(frame_ext)
        fr = _range(all_frames)
        if fr:
            start, end = fr
            read_node["first"].setValue(start)
            read_node["last"].setValue(end)
            read_node["origfirst"].setValue(start)
            read_node["origlast"].setValue(end)
        changed += 1
    nuke.message("已转换 %d 个 Read 为序列路径" % changed)


def rename_nodes_by_backdrop():
    """Rename nodes inside each Backdrop using the backdrop title (portable rewrite)."""
    count = 0
    for backdrop in nuke.allNodes("BackdropNode"):
        try:
            nodes = backdrop.getNodes()
        except Exception:
            continue
        title = (backdrop["label"].value() or "").split("\n")[0].split(" ")[0]
        # strip simple HTML img tags from preset backdrops
        if "<" in title:
            import re as _re
            title = _re.sub(r"<[^>]+>", "", title).strip()
        if not title:
            continue
        for node in nodes:
            name = node.name()
            if "_" in name:
                continue
            try:
                if node.knob("disable") and node["disable"].value():
                    continue
            except Exception:
                pass
            if node.Class() == "Group":
                base = name.rstrip("0123456789")
                new_name = "%s_%s_1" % (base, title)
            else:
                new_name = "%s_%s_1" % (node.Class(), title)
            try:
                node.setName(new_name, updateExpressions=True)
                count += 1
            except Exception:
                pass
    nuke.message("已重命名 %d 个节点" % count)


def replace_glow_mask_with_width():
    """Glow2: move mask channel into width (mask.a) via Copy — portable rewrite."""
    changed = []
    for n in nuke.allNodes("Glow2"):
        try:
            mask_knob = n["maskChannelMask"] if n.input(1) else n["maskChannelInput"]
            mask_channel = mask_knob.value()
        except Exception:
            continue
        if not mask_channel or mask_channel == "none":
            continue
        copy_node = nuke.createNode("Copy", "from0 %s\nto0 mask.a" % mask_channel, False)
        copy_node.setInput(0, n.input(0))
        copy_node.setInput(1, n.input(1))
        copy_node.setXYpos(n.xpos(), n.ypos() - max(copy_node.screenHeight(), 32) - 10)
        try:
            width_channel = n["W"].value()
        except Exception:
            width_channel = "none"
        if width_channel and width_channel != "none":
            input0 = nuke.createNode(
                "ChannelMerge",
                "A mask.a\nB %s\noperation in" % mask_channel,
                False,
            )
            input0.setInput(0, copy_node)
            input0.setInput(1, copy_node)
        else:
            input0 = copy_node
        n.setInput(0, input0)
        n.setInput(1, None)
        try:
            n["maskChannelMask"].setValue("none")
            n["maskChannelInput"].setValue("none")
            n["W"].setValue("mask.a")
        except Exception:
            pass
        changed.append(n.name())
    if changed:
        nuke.message("将 %d 个 Glow 的 mask 改为 width:\n%s" % (len(changed), ", ".join(changed)))
    else:
        nuke.message("没有发现使用了 mask 的 Glow 节点")
