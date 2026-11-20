# ark_nuke

## 目录结构

```
ark_nuke/
  init.py             # 所有会话：为子目录 pluginAddPath
  menu.py             # 仅 GUI：顶栏菜单「Ark」
  install_nuke.cmd    # Windows：向 %UserProfile%\.nuke\init.py 追加路径（可重复执行、不重复写入）
  install_nuke.sh     # Linux / macOS：向 ~/.nuke/init.py 追加路径
  uninstall_nuke.cmd  # Windows：从 init.py 移除本工具包路径（可重复执行）
  uninstall_nuke.sh   # Linux / macOS：从 init.py 移除本工具包路径
  gizmos/             # .gizmo 插件
  python/             # Python 模块（经 init 加入路径）
  nk_files/           # .nk 片段 / ToolSets
  icons/              # 菜单 / 工具栏图标
  third_party/        # GitHub 开源插件（每仓库一文件夹，自动扫描加载）
```

## 安装（Windows）

1. 双击或运行 `install_nuke.cmd`（幂等：已存在则不会重复追加）。
2. 重启 Nuke。
3. 在 Script Editor / 终端应看到 `[ark_nuke] loaded`；GUI 顶栏出现 **Ark** 菜单。

写入示例（正斜杠）：

```python
nuke.pluginAddPath(r'D:/software_dev/ark_nuke')
```

## 卸载

只删除安装时写入的那一行 `nuke.pluginAddPath(r'<本目录>')`。其它插件路径，以及 `init.py` 里的其余内容，都会保留。脚本可重复执行。完成后重启 Nuke。

Windows：双击或运行 `uninstall_nuke.cmd`。

Linux / macOS：

```bash
bash uninstall_nuke.sh
```

## Nuke 16 说明

本机已验证：**Nuke 16.0v7**，可执行文件为  
`C:\Program Files\Nuke16.0v7\Nuke16.0.exe`  
（自带 **Python 3.11.7**、**PySide6**，不是 PySide2）。

`init.py` 仅按 `nuke.NUKE_VERSION_MAJOR` 打印 Qt 绑定提示，加载时不 import PySide，因此终端模式（`-t`）保持干净。

## 不永久安装时的终端测试

```bat
set NUKE_PATH=D:\software_dev\ark_nuke
"C:\Program Files\Nuke16.0v7\Nuke16.0.exe" -t D:\software_dev\ark_nuke\tests\probe_nuke_path.py
```

或使用延迟 `pluginAddPath` 探测：

```bat
"C:\Program Files\Nuke16.0v7\Nuke16.0.exe" -t D:\software_dev\ark_nuke\tests\probe_load.py
```

## 第三方开源插件（third_party）

将 GitHub 仓库克隆到 `third_party/<仓库名>/` 后重启 Nuke 即可；`init.py` 会自动 `pluginAddPath`。详见 `third_party/README.md`。

当前已纳入：`third_party/NukeSurvivalToolkit`（完整工具包；勿与 `gizmos`/`python` 下旧副本混放）。

## 从 nuke_plugins 导入（2026-11-01，再同步）

| 类型 | 目标合计 | 本次新增 | 替换 | 未变 | 目标位置 |
|------|----------:|----------:|------:|------:|----------|
| `*.gizmo` | 104 | 3 | 0 | 101 | `gizmos/`（含分类 / third_party 子目录） |
| 分类 `init.py` | 4 | 0 | 0 | 4 | `gizmos/init.py`、`Color/`、`third_party/`、`third_party/3D/` |
| `*.nk` ToolSets | 55（另有脚手架 demo） | 1 | 0 | 54 | `nk_files/ToolSets/`（`WLF/`、`WLF/FX\|Keyer\|MP/`、`third_party/`） |
| 实用 `*.py` | — | — | — | — | 现保留 `python/custom_cmd/` + `ark_nuke_demo.py`；完整 NST 走 `third_party/` |

**本次同步新增（gizmo/nk）：** `third_party/Draw/LYS_PreCompInfo.gizmo`、`third_party/Filter/ExpGlow.gizmo`、`third_party/Filter/MC_realGlow.gizmo`、`ToolSets/WLF/Texture_Projector.nk`。

**Python 布局（2026-11-01）：** 已从 `python/` **移除** Cryptomatte、tabtabtab-nuke、ddot、max-van-leeuwen（WrapItUp），便于自行从网络下载最新版替换；`init.py` 的 `_PYTHON_PLUGIN_SUBPATHS` 与 Ark 对应菜单项已清空。仍保留 `custom_cmd`（仅状态项）与 `ark_nuke_demo.py`。重新放入包后需再写回 `pluginAddPath` 与 Ark 命令。

**跳过（吾立方 Python）：** `wulifang/`（含 license.py 与 vendor）、`lib/`（与 vendor 耦合）、`Python/Startup*`、`scripts/` CI、typings、docs、fonts、NodePresets、`__pycache__`、`.git`、`install_*.cmd`。`plugins/` 下的分类 `init.py` 与 gizmo 同目录，不放在 `python/`。

**说明：** `wlf/wulifang` 内可用代码仍依赖许可证 / vendor 引导，未并入本包。上方实用 py 来自 `nuke_plugins` 中**其它**顶层包。

脚手架演示保留：`python/ark_nuke_demo.py`、`nk_files/ark_nuke_DemoGroup.nk`。

## Ark「编辑 / 工具」整合（2026-11-01）

| 来源 | 处理 |
| --- | --- |
| 吾立方 `wulifang` 专有项（多节点编辑、AOV 组装、Cryptomatte 修名、RotoPaint 摄影表、拆 EXR、按素材名组装、生成代理、拆分颜色/ColorReplace、重命名通道、匹配抽帧、运动扭曲等） | **未迁入**（license/vendor 或重型 Panel/采样链） |
| 与现有 Ark 重复 | **跳过**：打包→`WrapItUp`；Cryptomatte/dDot/Tabtabtab 用已有子菜单 |
| NukeToolSet `Multi Script Editor` / `Switch Shot` | **未迁入**（旧 PySide1） |
| NukeToolSet `PresetBackdrop` / `Single To Sequence` | **已迁入** |
| Glow width mask、Backdrop 内重命名 | **已迁入**（纯 Nuke API 重写） |

### Tab 搜索（Nodes 工具栏）

Nuke 自带 Tab / tabtabtab 主要索引 **Nodes** 工具栏。仅挂在顶栏 `Ark → 编辑|工具` 时 Tab 搜不到。
**每一项均已同步到 `Nodes → Ark → 编辑|工具`**（含「稍后启用」子菜单），并提供短别名：`拆分图层` / `拆分rgba` / `拆分 RGBA` / `正则拆分图层组` / `相对路径` / `序列路径` / `空文件夹` / `批量替换` / `预设Backdrop`。