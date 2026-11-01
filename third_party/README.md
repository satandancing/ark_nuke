# third_party — 第三方 Nuke 插件管理

把第三方 Nuke 插件放在本目录下，由 `ark_nuke/init.py` 自动扫描并 `pluginAddPath`，无需再改 `.nuke/init.py`。

## 如何添加插件

1. **目录型仓库**：`third_party/<RepoName>/`（一个仓库一个文件夹，保持原有结构）。
2. **单文件脚本**：可直接放在 `third_party/<name>.py`（会挂载 `third_party` 根路径以便 `import`）。
3. **克隆示例**：
   ```bat
   cd D:\software_dev\ark_nuke
   git clone https://github.com/org/repo third_party\RepoName
   ```
4. **重启 Nuke**（或重新设置 `NUKE_PATH` 后启动）。若包内有 `init.py` / `menu.py`，或标准子目录 `gizmos` / `python` / `icons` / `nk_files` / `images`，会自动加入插件路径。

## 已挂载插件一览

| 名称 | 路径 | 来源 URL | 挂载说明 | Qt 兼容 |
|------|------|----------|----------|---------|
| WrapItUp | `third_party/WrapItUp/` | https://github.com/max-van-leeuwen/Nuke-WrapItUp | `pluginAddPath` 包目录；自带 `menu.py` 的顶栏 `Extra/Wrap It Up` **已抑制**（`_REGISTER_EXTRA_MENU=False`），统一走 Ark → WrapItUp | 上游已 PySide6→PySide2→PySide；无需再改 |
| tabtabtab | `third_party/tabtabtab/` | https://github.com/charlesangus/tabtabtab-nuke-fork | `pluginAddPath` 包目录；自带 `menu.py` 注册 Tab 快捷键 + Edit 偏好；Ark 菜单 `Tabtabtab` / `Tabtabtab Preferences...` | 核心已 PySide6→PySide2；`tabtabtab_prefs_dialog.py` 已补同样回退，并用 `qt_compat.dialog_exec` |
| dDot | `third_party/dDot.py` | https://www.nukepedia.com/tools/python/nodegraph/ddot/?tab=download | 松散模块：`pluginAddPath(third_party根)`；Ark 启动时 `import dDot`；**顶栏 `backpack` 已抑制**（`_REGISTER_NUKE_MENUBAR_BACKPACK=False`），Nodes 工具栏 backpack + 快捷键保留；Ark/`dDot` 子菜单转发各入口；菜单注册已包在 `if nuke.GUI` | 无 Qt（纯 nuke API） |
| Cryptomatte | `third_party/Cryptomatte/` | https://github.com/Psyop/Cryptomatte (`nuke/` @ `968d5e4`) | `pluginAddPath` 包目录（上游 nuke/ 扁平布局：gizmo + py + init/menu）；自带 `menu.py` → **Nodes** 工具栏 `Cryptomatte`（非 Nuke 顶栏）；Ark → Cryptomatte 镜像四项；`SOURCE.txt` 记录 commit | 无 Qt（纯 nuke API）；v1.4.0 |
| Stamps | `third_party/Stamps-1.2.0/` | Adrian Pueyo / Alexey Kuchinski (Nukepedia) | `pluginAddPath` 包目录（`init.py` 再挂 `stamps/`）；自带 `Edit/Stamps` + `Nodes/Other/Stamps`（F8）；Ark → Stamps 镜像；`Nodes → Ark → Stamps` 供 Tab | 已改 `stamps.py`：优先 `qt_compat`（PySide6→2），QDialog 用 `_dialog_exec` 兼容 `exec`/`exec_` |
| NukeSurvivalToolkit | `third_party/NukeSurvivalToolkit/` | https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease | 既有完整包，自带 menu；**本轮未改动** | 自带 `h_Qt` 等 |

## Qt 统一绑定（2026-11-01 更新）

- 共享模块：`ark_nuke/python/qt_compat.py`（已在 `init.py` 的 `python/` 路径上）。
- 策略：**优先 PySide6，失败则 PySide2**；提供 `dialog_exec()` 兼容 `exec` / `exec_`。
- 用法：
  ```python
  from qt_compat import QtCore, QtGui, QtWidgets, Qt, is_pyside6, QT_API, dialog_exec
  ```
- 本轮对 third_party 的最小改动：修补 `tabtabtab/tabtabtab_prefs_dialog.py`（原先硬编码 PySide6）；以及 `Stamps-1.2.0/stamps/stamps.py`（优先 `qt_compat`，QDialog `_dialog_exec`）。WrapItUp / tabtabtab 其余文件已自带回退。
- WrapItUp 自带 `menu.py` 补了 `import nuke`（原文件缺 import，在部分加载方式下会 NameError）。

## Loader 行为（`ark_nuke/init.py`）

- 跳过以 `.` 开头的名字、`README.md`、以及以 `_` 开头的目录。
- 对 `third_party` **根目录**执行 `pluginAddPath`（支持 `dDot.py` 等松散模块）。
- 对每个直接子目录：`pluginAddPath(abs)`，并追加存在的 `gizmos` / `python` / `icons` / `nk_files` / `images`。
- GUI 下各包自带 `menu.py` 仍会由 Nuke 加载；Ark 菜单额外提供统一入口与 `List third_party packages`。


## 顶栏菜单抑制（ark_nuke）

- **Extra**（WrapItUp）：`third_party/WrapItUp/menu.py` 中 `_REGISTER_EXTRA_MENU = False`。
- **backpack**（dDot）：`third_party/dDot.py` 中 `_REGISTER_NUKE_MENUBAR_BACKPACK = False`（仅抑制 Nuke 主菜单栏；Nodes 工具栏仍有 backpack）。
- 功能入口统一在 **Ark** 菜单；将对应 flag 设为 `True` 可恢复顶栏项。

## English (short)

1. Folder packages → `third_party/<RepoName>/`; loose scripts → `third_party/<name>.py`
2. Restart Nuke — auto `pluginAddPath` via `init.py`
3. Qt: use `python/qt_compat.py` (PySide6 then PySide2)
4. Do not flatten a whole repo into `third_party/` root unless it is a single-file tool like dDot

## Notes

- Ark → **List third_party packages** 可核对已发现包/松散模块。
- 旧的 `python/NukeSurvivalToolkit` 部分拷贝已挪到 `python/_legacy_nst_partial/`，不再被加载。
- 不要改动 `nuke_plugins` / license / NST，除非任务明确要求。