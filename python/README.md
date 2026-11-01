# python/

Nuke-facing Python modules. Root `init.py` does `pluginAddPath(.../python)` plus selected plugin subfolders so hyphenated dirs remain importable.

## Layout

| Path | Role |
|------|------|
| `ark_nuke_demo.py` | Scaffold demo |
| `custom_cmd/` | Optional platform startup scripts runner (not auto-loaded; Ark status only) |

## Removed (2026-11-01) — re-download later

Drop fresh copies under `python/`, then re-add to root `init.py` `_PYTHON_PLUGIN_SUBPATHS` and Ark `menu.py`:

- `Cryptomatte/` — Psyop Cryptomatte (https://github.com/Psyop/Cryptomatte)
- `tabtabtab-nuke/` — Tab node creator
- `ddot/` — dDot / backpack-style Dot tools
- `max-van-leeuwen/` — `WrapItUp.py` (https://www.nukepedia.com/tools/python/misc/wrapitup/)

## Ark menu

Root `menu.py` adds **Nuke > Ark** helpers (list python plugins, third_party packages, custom_cmd status). Gizmo/ToolSet toolbar registration is unchanged.

## Policy

- Do **not** merge `wulifang/` license/vendor stacks here.
- Do **not** overwrite `ark_nuke_demo.py` when re-importing plugins.
- Do **not** touch `third_party/NukeSurvivalToolkit`.
