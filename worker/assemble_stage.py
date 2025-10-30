# -*- python-interpreter: "C:/Program Files/Side Effects Software/Houdini 19.0.720/bin/hython3.7.exe" -*-

# hython worker/assemble_stage.py <usd_dir> <out_stage>
import sys, pathlib
from pxr import Sdf, Usd

indir = pathlib.Path(sys.argv[1])
out   = pathlib.Path(sys.argv[2])

layer = Sdf.Layer.CreateNew(str(out))
stage = Usd.Stage.Open(layer)

# Compose each asset under /Assets
p = Sdf.Path("/Assets")
stage.DefinePrim(p)
for usd in sorted(indir.glob("*.usd")):
    name = usd.stem
    prim = stage.OverridePrim(p.AppendChild(name))
    prim.GetReferences().AddReference(str(usd))

stage.GetDefaultPrim() or stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
stage.GetRootLayer().Save()
print(f"STAGE {out} with {len(list(indir.glob('*.usd')))} refs")