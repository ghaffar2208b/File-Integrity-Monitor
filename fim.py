"""Simple File Integrity Monitor: baseline and check modes."""
import hashlib
import os
import sys
from datetime import datetime

MONITORED_DIR = "monitored"
BASELINE_FILE = "baseline.txt"
REPORT_FILE = "report.txt"


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sha256_file(path):
    """Hash a file in chunks so large files don't fill memory."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scan(directory):
    """Return {file_path: sha256} for every file under directory."""
    result = {}
    for root, _, files in os.walk(directory):
        for name in sorted(files):
            path = os.path.join(root, name)
            result[path] = sha256_file(path)
    return result


def create_baseline():
    hashes = scan(MONITORED_DIR)
    with open(BASELINE_FILE, "w") as f:
        for path, digest in sorted(hashes.items()):
            f.write(f"{digest}  {path}\n")
    print(f"[{now()}] Baseline created: {len(hashes)} files -> {BASELINE_FILE}")


def load_baseline():
    baseline = {}
    with open(BASELINE_FILE) as f:
        for line in f:
            line = line.rstrip("\n")
            if line:
                digest, path = line.split("  ", 1)
                baseline[path] = digest
    return baseline


def check():
    baseline = load_baseline()
    current = scan(MONITORED_DIR)
    lines = [f"=== FIM Check Report | {now()} ==="]

    for path in sorted(current):
        if path not in baseline:
            lines.append(f"[ADDED]    {path}")
        elif current[path] != baseline[path]:
            lines.append(f"[MODIFIED] {path}")
            lines.append(f"           expected: {baseline[path]}")
            lines.append(f"           found:    {current[path]}")
    for path in sorted(baseline):
        if path not in current:
            lines.append(f"[DELETED]  {path}")

    changes = len(lines) - 1
    if changes == 0:
        lines.append("OK: all files match the baseline. No changes detected.")
    lines.append("=" * 40)

    report = "\n".join(lines)
    print(report)
    with open(REPORT_FILE, "a") as f: 
        f.write(report + "\n\n")
    return changes


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("baseline", "check"):
        print("Usage: python3 fim.py [baseline|check]")
        sys.exit(2)
    if sys.argv[1] == "baseline":
        create_baseline()
    else:
        sys.exit(1 if check() else 0)
