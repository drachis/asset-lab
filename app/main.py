import sys, subprocess, json, pathlib, os
import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore

ASSET_EXTS = {".fbx", ".obj", ".gltf", ".glb", ".usd", ".usda", ".usdc"}

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asset Lab")
        self.resize(800, 640)
        self.root = QtWidgets.QLineEdit()
        browse = QtWidgets.QPushButton("Select Directory")
        browse.clicked.connect(self.pick_dir)
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["File", "Type", "Size (KB)"])
        self.log = QtWidgets.QPlainTextEdit(); self.log.setReadOnly(True)
        btns = QtWidgets.QHBoxLayout()
        self.btn_validate = QtWidgets.QPushButton("Validate")
        self.btn_convert  = QtWidgets.QPushButton("Convert to USD")
        self.btn_stage    = QtWidgets.QPushButton("Assemble Stage.usd")
        self.btn_submit   = QtWidgets.QPushButton("Submit to OpenCue")
        for b in (self.btn_validate, self.btn_convert, self.btn_stage, self.btn_submit):
            btns.addWidget(b)
        self.btn_validate.clicked.connect(self.on_validate)
        self.btn_convert.clicked.connect(self.on_convert)
        self.btn_stage.clicked.connect(self.on_stage)
        self.btn_submit.clicked.connect(self.on_submit)

        top = QtWidgets.QHBoxLayout(); top.addWidget(self.root); top.addWidget(browse)
        lay = QtWidgets.QVBoxLayout(); lay.addLayout(top); lay.addWidget(self.table); lay.addLayout(btns); lay.addWidget(self.log)
        w = QtWidgets.QWidget(); w.setLayout(lay); self.setCentralWidget(w)

    def pick_dir(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Pick source folder")
        if d:
            self.root.setText(d)
            self.refresh()

    def refresh(self):
        root = pathlib.Path(self.root.text())
        files = [p for p in root.rglob("*") if p.suffix.lower() in ASSET_EXTS]
        self.table.setRowCount(0)
        for p in sorted(files):
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(p)))
            self.table.setItem(r, 1, QtWidgets.QTableWidgetItem(p.suffix.lower()))
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(f"{p.stat().st_size//1024}"))

    # Helper to run a subprocess and stream stdout
    def run(self, args, env=None):
        self.log.appendPlainText("$ " + " ".join(args))
        p = QtCore.QProcess(self)
        if env:
            e = QtCore.QProcessEnvironment.systemEnvironment()
            for k, v in env.items(): e.insert(k, v)
            p.setProcessEnvironment(e)
        p.setProgram(args[0]); p.setArguments(args[1:])
        p.readyReadStandardOutput.connect(lambda: self.log.appendPlainText(bytes(p.readAllStandardOutput()).decode(errors='ignore')))
        p.readyReadStandardError.connect(lambda: self.log.appendPlainText(bytes(p.readAllStandardError()).decode(errors='ignore')))
        p.start(); p.waitForFinished(-1)
        self.log.appendPlainText(f"[exit {p.exitCode()}]\n")
        return p.exitCode()

    def on_validate(self):
        root = self.root.text()
        self.run([sys.executable, "-m", "validate.gltf_meta", root])

    def on_convert(self):
        root = self.root.text()
        hython = os.environ.get("HYTHON", "hython")  # set HYTHON env to Houdini hython.exe
        self.run([hython, "worker/convert_to_usd.py", root, "out/usd"])  # writes per-asset USDs

    def on_stage(self):
        out = self.root.text()
        hython = os.environ.get("HYTHON", "hython")
        self.run([hython, "worker/assemble_stage.py", "out/usd", "out/stage.usd"])  # compose a root stage

    def on_submit(self):
        # Try OpenCue; fallback to mock
        if self.run([sys.executable, "farm/opencue_submit.py", "out/stage.usd"]) != 0:
            self.run([sys.executable, "farm/mock_submit.py", "out/stage.usd"])  # simulate farm

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    m = Main(); m.show()
    sys.exit(app.exec_())