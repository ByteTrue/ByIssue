"""Only mechanical checks; content quality is judged in review.md."""
from pathlib import Path
import sys

project = Path(sys.argv[1])
assert sys.argv[2] == "1"
assert (project / "byissue/work").is_dir()
assert list((project / "byissue/memory").glob("*.md")), "the explicit durable decision needs a Memory record"
assert (project / "config.json").read_bytes() == (Path(__file__).parent / "project/config.json").read_bytes()
print("PASS: workspace and Memory exist, config preserved; semantic review still required")
