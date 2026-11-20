#!/usr/bin/env python3
"""Upload a built Forgotten Realms archive to the private-library R2 bucket."""

import argparse
import mimetypes
import subprocess
from pathlib import Path

PREFIX = "forgotten-realms"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--bucket", default="d20srdhub-private-library")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    files = [path for path in args.archive.rglob("*") if path.is_file()]
    for index, path in enumerate(files, 1):
        key = f"{PREFIX}/{path.relative_to(args.archive).as_posix()}"
        command = ["npx", "wrangler", "r2", "object", "put", f"{args.bucket}/{key}", f"--file={path}"]
        content_type = mimetypes.guess_type(path.name)[0]
        if content_type:
            command.append(f"--content-type={content_type}")
        if args.dry_run:
            print(" ".join(command))
        else:
            subprocess.run(command, check=True)
        if index % 500 == 0:
            print(f"Uploaded {index:,}/{len(files):,}")


if __name__ == "__main__":
    main()
