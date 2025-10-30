import sys, subprocess, json, pathlib, os
import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
from PySide2.QtCore import Qt

ASSET_EXTS = {".fbx", ".obj", ".gltf", ".glb", ".usd", ".usda", ".usdc"}

def set_application_font():
    app = QtWidgets.QApplication.instance()
    font = app.font()
    font.setPointSize(8)  # Increase base font size
    app.setFont(font)

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asset Lab")
        self.resize(1000, 640)
        
        # Set fonts for better readability
        font = QtGui.QFont()
        font.setPointSize(11)
        button_font = QtGui.QFont()
        button_font.setPointSize(8)
        table_font = QtGui.QFont()
        table_font.setPointSize(8)
        
        self.root = QtWidgets.QLineEdit()
        self.root.setFont(font)
        
        browse = QtWidgets.QPushButton("Select Directory")
        browse.setFont(button_font)
        browse.clicked.connect(self.pick_dir)
        
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setFont(table_font)
        self.table.horizontalHeader().setFont(font)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Size (KB)", "Path"])
        
        # Setup column resize modes
        header = self.table.horizontalHeader()
        INTERACTIVE = QtWidgets.QHeaderView.ResizeMode.Interactive
        STRETCH = QtWidgets.QHeaderView.ResizeMode.Stretch
        
        # Set resize modes for columns
        for col in range(4):
            if col < 3:
                header.setSectionResizeMode(col, INTERACTIVE)
            else:
                header.setSectionResizeMode(col, STRETCH)
                
        # Set initial column widths
        self.table.setColumnWidth(0, 200)  # Name
        self.table.setColumnWidth(1, 80)   # Type
        self.table.setColumnWidth(2, 80)   # Size

        # Initialize log widget
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setFont(table_font)
        self.log.setReadOnly(True)
        
        btns = QtWidgets.QHBoxLayout()
        self.btn_validate = QtWidgets.QPushButton("Validate")
        self.btn_convert  = QtWidgets.QPushButton("Convert to USD")
        self.btn_stage    = QtWidgets.QPushButton("Assemble Stage.usd")
        self.btn_submit   = QtWidgets.QPushButton("Submit to OpenCue")
        
        # Set larger font for all buttons
        for btn in (self.btn_validate, self.btn_convert, self.btn_stage, self.btn_submit):
            btn.setFont(button_font)
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
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select asset folder")
        if d:
            self.root.setText(d)
            self.refresh()

    def refresh(self):
        root = pathlib.Path(self.root.text())
        root_str = str(root)
        files = [p for p in root.rglob("*") if p.suffix.lower() in ASSET_EXTS]
        
        # Clear table
        self.table.setRowCount(0)
        
        # Reset fixed column sizes
        self.table.setColumnWidth(1, 80)   # Type
        self.table.setColumnWidth(2, 80)   # Size
        
        for p in sorted(files):
            r = self.table.rowCount()
            self.table.insertRow(r)
            
            # Name without extension
            name_item = QtWidgets.QTableWidgetItem(p.stem)
            self.table.setItem(r, 0, name_item)
            
            # Type (file extension)
            type_item = QtWidgets.QTableWidgetItem(p.suffix.lower())
            self.table.setItem(r, 1, type_item)
            
            # Size in KB
            size_item = QtWidgets.QTableWidgetItem(f"{p.stat().st_size//1024}")
            size_item.setTextAlignment(0x0002 | 0x0080)  # Qt.AlignRight | Qt.AlignVCenter
            self.table.setItem(r, 2, size_item)
            
            # Just the containing folder path (excluding the file name and root directory)
            rel_path = p.relative_to(root)
            folder_path = str(rel_path.parent) if rel_path.parent != pathlib.Path(".") else "/"
            path_item = QtWidgets.QTableWidgetItem(folder_path)
            self.table.setItem(r, 3, path_item)
            
        # After populating data, resize the Name column to fit content
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.resizeColumnToContents(2)

    
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
        self.run([sys.executable, "-m", "validate.validator", root])

    def on_convert(self):
        root = self.root.text()
        hython = os.environ.get("HYTHON", "hython")  
        self.run([hython, "-m", "worker.convert_to_usd", root, "out/usd"])  

    def on_stage(self):
        out = self.root.text()
        hython = os.environ.get("HYTHON", "hython")
        self.run([hython, "-m", "worker.assemble_stage", "out/usd", "out/stage.usd"])  

    def on_submit(self):
        
        if self.run([sys.executable, "-m", "farm.opencue_submit", "out/stage.usd"]) != 0:
            self.run([sys.executable, "-m", "farm.mock_submit", "out/stage.usd"])  

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Apply application-wide font settings
    font = app.font()
    font.setPointSize(11)
    app.setFont(font)
    
    m = Main()
    m.show()
    sys.exit(app.exec_())