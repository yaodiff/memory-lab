"""Populate an experiment-local FastEmbed cache with the frozen revisions."""

import os
from pathlib import Path

from huggingface_hub import snapshot_download


ASSETS = {
    "Qdrant/bge-small-en-v1.5-onnx-Q": "aa8f8b060edb",
    "Qdrant/bm25": "22b8d2af71a7",
}


if __name__ == "__main__":
    cache = Path(os.environ["FASTEMBED_CACHE_PATH"])
    for repository, revision in ASSETS.items():
        snapshot = Path(snapshot_download(repository, revision=revision, cache_dir=cache))
        ref = snapshot.parents[1] / "refs" / "main"
        ref.parent.mkdir(exist_ok=True)
        ref.write_text(snapshot.name)
        print(f"{repository} {revision}", flush=True)
