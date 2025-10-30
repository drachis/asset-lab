# Asset Lab

A tiny asset‑processing pipeline:
- PySide2 UI (standalone or inside Houdini)
- Hython worker converts FBX/OBJ → USD
- USD stage assembler
- Validators (glTF metadata, naming policy)
- OpenCue job spec (or mock submitter)

## Quickstart

# 1) Point HYTHON to Houdini 19.0 hython
$ set HYTHON="C:\\Program Files\\Side Effects Software\\Houdini 19.0.xxx\\bin\\hython.exe"

# 2) Run the UI
$ python app/main.py

# 3) Pick `sample_assets/` and click Convert → USD, then Assemble Stage, then Submit

## Notes
- If OpenCue client isn’t installed, Submit falls back to a mock threaded job.
- All worker scripts can be run headless via hython.