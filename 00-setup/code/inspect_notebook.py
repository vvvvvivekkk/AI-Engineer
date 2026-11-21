"""
inspect_notebook.py - show that a .ipynb notebook is really a JSON text file.

Run it with the path to any notebook:
    python code/inspect_notebook.py notebooks/01-environment-check.ipynb

It prints how many cells the notebook has, what type each one is,
the first line of each cell, and whether outputs are saved inside the file.
"""

import json                                  # json turns JSON text into Python dicts and lists
import sys                                   # sys.argv holds the words typed after the script name
from pathlib import Path                     # Path makes working with file paths easy


def main():
    if len(sys.argv) < 2:                    # the user forgot to give a file name
        print("Usage: python code/inspect_notebook.py PATH/TO/notebook.ipynb")
        return
    path = Path(sys.argv[1])                 # the first word after the script name
    data = json.loads(path.read_text(encoding="utf-8"))   # read the file and parse the JSON

    print(f"File: {path.name}")
    print(f"Top-level keys: {list(data.keys())}")         # usually cells, metadata, nbformat...
    print(f"Notebook format version: {data['nbformat']}.{data['nbformat_minor']}")
    cells = data["cells"]                    # the list of cells, in page order
    print(f"Number of cells: {len(cells)}\n")

    for i, cell in enumerate(cells):         # enumerate gives a counter i plus each cell
        source = "".join(cell["source"])     # the cell's text may be stored as a list of lines
        first_line = source.split("\n")[0][:60]           # first line, cut to 60 characters
        outputs = len(cell.get("outputs", []))            # markdown cells have no outputs
        print(f"[{i:2}] {cell['cell_type']:<8} outputs={outputs}  {first_line}")


if __name__ == "__main__":
    main()
