"""Fetch and verify the public dataset and model outside the checkout."""

import argparse
import base64
import hashlib
import json
import subprocess
from pathlib import Path

CONFIG = json.loads(Path(__file__).with_name("config.json").read_text())


def digest(path):
    with path.open("rb") as stream:
        return base64.b64encode(hashlib.file_digest(stream, "sha256").digest()).decode("ascii")


def fetch(asset, directory):
    target = directory / asset["file"]
    expected = asset["sha256_base64"]
    if target.is_file() and digest(target) == expected:
        return target
    revision = asset["revision"]
    url = f'https://huggingface.co/{asset["repo"]}/resolve/{revision}/{asset["file"]}'
    partial = target.with_suffix(target.suffix + ".partial")
    subprocess.run(
        ["curl", "--fail", "--location", "--retry", "2", "--silent", "--show-error",
         "--output", str(partial), url + "?download=1"],
        check=True,
    )
    if digest(partial) != expected:
        raise ValueError(f"Checksum mismatch for {asset['file']}")
    partial.replace(target)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    checkout = Path(__file__).resolve().parents[2]
    if args.directory.resolve().is_relative_to(checkout):
        parser.error("Choose a directory outside the repository.")
    args.directory.mkdir(parents=True, exist_ok=True)
    for name in ("dataset", "model"):
        print(fetch(CONFIG[name], args.directory))
