from pathlib import Path

ERROR_LOG = Path("import_errors.txt")


def clear_error_log():
    """Delete the old error log before starting a new import."""

    if ERROR_LOG.exists():
        ERROR_LOG.unlink()


def log_error(url, error):
    """Append one failed import to the error log."""

    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"{url}\n")
        f.write(f"Reason: {error}\n")
        f.write("-" * 60 + "\n")