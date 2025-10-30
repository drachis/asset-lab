import sys, json, pathlib, re
from typing import cast
from .policy import NAME_RULE, ALLOWED_EXTS


from pygltflib import GLTF2
import assimp_py

process_flags = (
    assimp_py.Process_Triangulate | assimp_py.Process_CalcTangentSpace
)

def scan(root):
    root = pathlib.Path(root)
    issues = []
    name_pattern = re.compile(NAME_RULE)

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext not in ALLOWED_EXTS:
            continue
        if not name_pattern.fullmatch(p.stem):
            issues.append((p, f"invalid name: '{p.name}'"))
            continue
        try:
            if ext in (".gltf", ".glb"):
                gltf = GLTF2.load(str(p))
                if not gltf.scenes:
                    issues.append((p, "no scenes"))
                if not gltf.nodes:
                    issues.append((p, "no nodes"))
            else:
                try:
                    scene = assimp_py.ImportFile(str(p),process_flags)
                except Exception as e:
                    issues.append((p, f"parse error: {e}"))
                    continue
                if not scene.meshes:
                    issues.append((p, "no meshes"))
                assimp_py.release(scene)
        except Exception as e:
            issues.append((p, f"parse error: {e}"))
    return issues

if __name__ == "__main__":
    root = sys.argv[1]
    for path, msg in scan(root):
        ext = path.suffix.lstrip('.').upper()
        print(f"[{ext}] {path}: {msg}")
