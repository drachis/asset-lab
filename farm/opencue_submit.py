import sys, os, pathlib
import opencue
from outline import Outline
from outline.modules.shell import Shell

stage = pathlib.Path(sys.argv[1]).resolve()
job_name = f"AssetLab_{stage.stem}"

ol = Outline(job_name)
layer = Shell(
    "convert",
    command=f"hython worker/convert_to_usd.py {stage.parent} out/usd"
)
ol.add_layer(layer)

# Launch the job
import outline.cuerun
outline.cuerun.launch(ol)
print(f"SUBMITTED {job_name}")