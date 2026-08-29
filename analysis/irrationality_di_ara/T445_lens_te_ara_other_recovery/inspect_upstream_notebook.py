import json
import re
import sys
from pathlib import Path


path = Path(sys.argv[1])
notebook = json.loads(path.read_text(encoding="utf-8"))
pattern = re.compile(
    sys.argv[2] if len(sys.argv) > 2 else r"fermat|potential|source|beta|shear|delta_phi|dphi|ra_image|dec_image",
    re.IGNORECASE,
)

for index, cell in enumerate(notebook["cells"]):
    source = "".join(cell.get("source", []))
    outputs = []
    for output in cell.get("outputs", []):
        if "text" in output:
            outputs.append("".join(output["text"]))
        elif "data" in output:
            outputs.append(json.dumps(output["data"]))
    rendered = "\n".join(outputs)
    if pattern.search(source):
        print(f"--- CELL {index} {cell['cell_type']} ---")
        print(source[:6000])
        if rendered:
            print("OUTPUT:", rendered[:6000])
