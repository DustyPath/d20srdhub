from pathlib import Path

QUEUE_FILE = Path("import_queue.txt")


def save_queue(urls):
    """Save discovered URLs."""

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        for url in sorted(urls):
            f.write(url + "\n")


def load_queue():
    """Load URLs from the queue."""

    if not QUEUE_FILE.exists():
        return []

    with open(QUEUE_FILE, encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip()
        ]