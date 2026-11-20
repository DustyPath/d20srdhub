#!/usr/bin/env python3
"""Upload a built Forgotten Realms archive to the private-library R2 bucket."""

import argparse
import mimetypes
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PREFIX = "forgotten-realms"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--bucket", default="d20srdhub-private-library")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    files = [path for path in args.archive.rglob("*") if path.is_file()]
    def upload(path: Path) -> None:
        key = f"{PREFIX}/{path.relative_to(args.archive).as_posix()}"
        command = ["npx", "wrangler", "r2", "object", "put", f"{args.bucket}/{key}", f"--file={path}", "--remote"]
        content_type = mimetypes.guess_type(path.name)[0]
        if content_type:
            command.append(f"--content-type={content_type}")
        if args.dry_run:
            print(" ".join(command))
        else:
            for attempt in range(5):
                result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    break
                if attempt == 4:
                    raise RuntimeError(f"Upload failed for {key}: {result.stderr[-1000:]}")
                time.sleep(2 ** attempt)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        for index, _ in enumerate(executor.map(upload, files), 1):
            if index % 100 == 0 or index == len(files):
                print(f"Uploaded {index:,}/{len(files):,}")


if __name__ == "__main__":
    main()
