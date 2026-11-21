"""Make `import src...` work when pytest is run from the project folder."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
