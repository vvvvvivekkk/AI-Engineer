"""Make `import src...` work, and point the queue at a throw-away database during tests."""
import os
import sys
import tempfile
from pathlib import Path

os.environ["QUEUE_DB"] = str(Path(tempfile.mkdtemp()) / "test_queue.db")   # must be set before src is imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
