# -*- python-interpreter: "C:/Program Files/Side Effects Software/Houdini 19.0.720/bin/hython3.7.exe" -*-
"""
Convert 3D model files (FBX/OBJ) to USD format using Houdini.

This script takes a source directory containing .fbx or .obj files and converts them
to USD format using Houdini's Python API (hou). It preserves the original file structure
and handles both FBX and OBJ formats appropriately.

Usage:
    hython convert_to_usd.py <source_dir> <output_dir>
"""

import sys
from pathlib import Path
from typing import Set, Union
import hou

# Supported input formats
SUPPORTED_FORMATS: Set[str] = {".fbx", ".obj"}

def ensure_output_dir(path: Union[str, Path]) -> Path:
    """Create output directory if it doesn't exist."""
    out_path = Path(path)
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path

def convert_to_usd(src_path: Path, out_dir: Path) -> None:
    """Convert a single 3D model file to USD format.
    
    Args:
        src_path: Source file path (.fbx or .obj)
        out_dir: Output directory for USD files
    """
    ext = src_path.suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        return

    obj = hou.node("/obj")
    geo = obj.createNode("geo", node_name=f"imp_{src_path.stem}")
    
    try:
        # Import based on file type
        if ext == ".obj":
            file1 = geo.createNode("file")
            file1.parm("file").set(str(src_path))
        else:  # .fbx
            hou.hipFile.importFBX(str(src_path), merge_into_scene=True)
            fbxroot = obj.glob(f"{src_path.stem}*")
            if fbxroot:
                merge = geo.createNode("object_merge")
                merge.parm("objpath1").set(fbxroot[0].path())
                merge.parm("xformtype").set(1)

        # Export to USD
        usdpath = out_dir / f"{src_path.stem}.usd"
        lopnet = geo.createNode("lopnet", node_name="lop")
        rop = lopnet.createNode("rop_usd")
        rop.parm("lopoutput").set(str(usdpath))
        rop.render()
        print(f"WROTE {usdpath}")
    
    finally:
        # Clean up even if there's an error
        geo.destroy()

def main() -> None:
    """Main entry point for the conversion script."""
    if len(sys.argv) != 3:
        print("Usage: hython convert_to_usd.py <source_dir> <output_dir>")
        sys.exit(1)

    src_dir = Path(sys.argv[1])
    out_dir = ensure_output_dir(sys.argv[2])

    if not src_dir.is_dir():
        print(f"Error: Source directory '{src_dir}' does not exist")
        sys.exit(1)

    for src_file in sorted(src_dir.rglob("*")):
        convert_to_usd(src_file, out_dir)

if __name__ == "__main__":
    main()