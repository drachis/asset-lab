import sys, json, pathlib, re
from typing import cast
from .policy import NAME_RULE, ALLOWED_EXTS

from pygltflib import GLTF2

def scan(root):
    root = pathlib.Path(root)
    issues = []
    for p in root.rglob("*.gltf"):
        try:
            gltf =  GLTF2.load(str(p))
            gltf = cast(GLTF2, gltf)
            if not gltf.scenes:
                issues.append((p, "no scenes"))
            if not gltf.nodes:
                issues.append((p, "no nodes"))
        except Exception as e:
            issues.append((p, f"parse error: {e}"))
    return issues

if __name__ == "__main__":
    root = sys.argv[1]
    for path, msg in scan(root):
        print(f"[GLTF] {path}: {msg}")