# File Integrity Monitor (FIM)

A small Python tool that creates a SHA-256 baseline of the files in a folder, then checks the folder against that baseline and reports three kinds of change: **ADDED**, **MODIFIED** and **DELETED**.

Built for: *Practical Assignment, Session 3: Data Integrity & Cryptography Basics*

- **Student name:** Abdul Ghaffar
- **Offer Letter No.:** SPL-2026-3732
- **Operating system:** Kali Linux
- **Submission date:** 30-Oct-2026

---

## How it works

1. **Baseline mode** walks through `monitored/`, computes the SHA-256 hash of every file and saves `hash  path` lines to `baseline.txt`.
2. **Check mode** hashes the current files and compares them with the baseline:
   - path in current files but not in baseline → `[ADDED]`
   - path in both but hashes differ → `[MODIFIED]`
   - path in baseline but not in current files → `[DELETED]`
3. Each check prints the result to the terminal and appends it, with a timestamp, to `report.txt`.

A hash is a fixed-length fingerprint of file content. Changing even one character produces a completely different hash, which is why hashes are useful for integrity checks.

## Project structure

```
file-integrity-monitor/
├── README.md
├── fim.py                # the FIM script (baseline and check modes)
├── baseline.txt          # plain-text baseline (for inspection)
├── baseline.txt.gpg      # encrypted copy of the baseline (AES-256)
├── report.txt            # appended report from every check run
├── monitored/            # sample test files being monitored
│   ├── file1.txt
│   ├── file2.txt
│   └── file3.txt
└── screenshots/          # timestamped evidence for each test
```

## Requirements

- Kali Linux (or any Linux with Python 3)
- Python 3 (standard library only, no packages to install)
- GnuPG (`gpg`), preinstalled on Kali

## Setup

```bash
git clone https://github.com/YOUR-USERNAME/file-integrity-monitor.git
cd file-integrity-monitor
```

To build from scratch instead:

```bash
mkdir -p monitored
echo "This is file one"   > monitored/file1.txt
echo "This is file two"   > monitored/file2.txt
echo "This is file three" > monitored/file3.txt
```

## Usage

Run all commands from the project folder.

**1. Create the baseline (do this once, on a clean state)**

```bash
python3 fim.py baseline
cat baseline.txt
```

**2. Create the encrypted copy**

```bash
gpg --symmetric --cipher-algo AES256 -o baseline.txt.gpg baseline.txt
```

Enter the password at the hidden prompt. The password is **not** stored in this repository.

**3. Verify the encrypted copy decrypts correctly**

```bash
gpg --decrypt baseline.txt.gpg 2>/dev/null | diff - baseline.txt && echo "Decryption verified: identical"
```

**4. Check for changes**

```bash
python3 fim.py check
```

Exit code is `0` when nothing changed and `1` when changes were found.

> Do not re-run `baseline` between tests. The same original baseline must be used, otherwise the changes are no longer detected.

## Test procedure

| Test | Action | Expected output |
|------|--------|-----------------|
| ADDED | `echo "new content" > monitored/newfile.txt` | `[ADDED] monitored/newfile.txt` |
| MODIFIED | `echo "tampered" >> monitored/file1.txt` | `[MODIFIED] monitored/file1.txt` with expected and found hashes |
| DELETED | `rm monitored/file2.txt` | `[DELETED] monitored/file2.txt` |

Each test was followed by `date; python3 fim.py check`, so the timestamp is visible in every screenshot.

## Results and explanations

### ADDED
After creating the baseline, I created a new file called `newfile.txt` inside the `monitored/` folder. When I ran the checker, it printed `[ADDED] monitored/newfile.txt`. This means the file was not in the original baseline, so it appeared after the baseline was made. This matters for security because attackers often drop new files, such as malware or backdoors, on a system.

### MODIFIED
I added the word "tampered" to the end of `file1.txt`. The checker printed `[MODIFIED] monitored/file1.txt` and showed two different hashes, the expected one from the baseline and the one it found now. This means the file content changed, because even a one-character change gives a completely different SHA-256 hash. This matters because attackers can secretly change important files like configs or scripts, and a hash comparison catches it.

### DELETED
I removed `file2.txt` from the `monitored/` folder using `rm`. The checker printed `[DELETED] monitored/file2.txt`, because the file was listed in the baseline but could not be found anymore. This means a file that should exist is missing. This matters because attackers or accidents can delete important files, such as logs, to hide their activity or break a system.

## Evidence

| # | Screenshot | Description |
|---|-----------|-------------|
| 1 | `screenshots/01_project_folder.png` | Project folder with sample files |
| 2 | `screenshots/02_baseline.png` | Baseline command and plain-text baseline |
| 3 | `screenshots/03_encrypted_baseline.png` | Encrypted baseline file (no password shown) |
| 4 | `screenshots/04_clean_check.png` | Clean verification before changes |
| 5 | `screenshots/05_added.png` | ADDED test |
| 6 | `screenshots/06_modified.png` | MODIFIED test |
| 7 | `screenshots/07_deleted.png` | DELETED test |
| 8 | `screenshots/08_final_report.png` | Final report with all three detection types |


## Why encryption alone is not enough?

Encrypting the baseline keeps it **secret**. If someone steals `baseline.txt.gpg`, they cannot read the file names or hashes without the password.

But encryption does not prove the baseline is **genuine or unchanged**. An attacker who can write to the system could change a monitored file, create a new baseline that matches the changed files, and replace the old baseline with it. The checker would then say everything is fine, even though the files were tampered with.

To prevent this, we need a **digital signature** or an **HMAC** (a hash made with a secret key) to prove the baseline was not changed. We also need a **trusted backup** of the baseline stored in a safe place that the monitored system cannot modify.

## Known limitations

- Detects **content changes only**. Changes to permissions, ownership or timestamps are not detected.
- A **manual** check, not real-time monitoring. Changes are found only when `check` is run.
- The baseline is not signed or authenticated, so anyone who can modify it can hide changes (see above).
- A renamed or moved file is reported as one `[DELETED]` plus one `[ADDED]`.
- Only the `monitored/` folder is scanned. Unreadable files (permission errors) are not handled specially.
- The script's own files are kept outside `monitored/` so they are not scanned.

## Security notes

- The password for the encrypted baseline is **not** included in this repository, README or screenshots.
- Only my own test files were scanned. No one else's system was scanned or altered.
- A protected backup of the trusted baseline is kept separately.

## Tool and AI disclosure

| Tool / AI | Purpose / how it was used |
|-----------|---------------------------|
| Kali Linux terminal (Bash) | Running commands, creating test files, making changes for each test |
| Python 3 (`hashlib`, `os`, `sys`, `datetime`) | The FIM script: hashing, scanning, comparing, reporting |
| `nano` | Editing the script |
| GnuPG (`gpg`) | Creating and verifying the AES-256 encrypted baseline |
| Git / GitHub | Version control and hosting the project |
| Claude (Anthropic AI assistant) | planning the project steps, generating the initial version of `fim.py`, explaining how the code works and drafting the README structure |

## License

For educational use.
