# -*- python-interpreter: "C:/Program Files/Side Effects Software/Houdini 19.0.720/bin/hython3.7.exe" -*-

import hou
net = hou.node("/tasks").createNode("topnet", "asset_lab")
filepat = net.createNode("filepattern"); filepat.parm("pattern").set("$JOB/out/usd/*.usd")
py = net.createNode("pythonprocessor"); py.parm("onCook").set("""
for item in work_items:
    print(item.inputFiles[0].path)
""")
filepat.setNextInput(py)
net.layoutChildren(); net.cook(force=True)
print("PDG COOKED")