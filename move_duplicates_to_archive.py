#!/usr/bin/env python3
"""
move_duplicates_to_archive.py
Find duplicate files by content (SHA256) and move duplicates to a central archive folder,
keeping the first (lexicographically) file in place.

Usage:
  python move_duplicates_to_archive.py
  python move_duplicates_to_archive.py --dry-run  # show actions without moving
"""
import os
import sys
import hashlib
import shutil
from collections import defaultdict

root = os.path.dirname(__file__)
archive_root = os.path.join(root, 'duplicates_archive')
exclude_dirs = {'.git', 'node_modules', '__pycache__'}

def sha256(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

files_by_hash = defaultdict(list)

for dirpath, dirnames, filenames in os.walk(root):
    # skip excludes and the archive itself
    dirnames[:] = [d for d in dirnames if d not in exclude_dirs and d != os.path.basename(archive_root)]
    for fn in filenames:
        path = os.path.join(dirpath, fn)
        try:
            if os.path.islink(path):
                continue
            size = os.path.getsize(path)
            if size == 0:
                continue
            h = sha256(path)
            files_by_hash[h].append((path, size))
        except Exception as e:
            print(f"Skipping {path}: {e}")

# collect duplicate groups
dupe_groups = [v for v in files_by_hash.values() if len(v) > 1]

if not dupe_groups:
    print("No duplicate files found.")
    sys.exit(0)

print(f"Found {len(dupe_groups)} groups of duplicates. Preparing to archive duplicates...\n")

dry_run = '--dry-run' in sys.argv
moved = 0

for i, group in enumerate(dedupe_sorted := [sorted(g, key=lambda x: x[0]) for g in dupe_groups], start=1):
    print(f"Group {i} (count={len(group)}):")
    keeper = group[0][0]
    print(f"  Keeper: {keeper}")
    for path, size in group[1:]:
        rel = os.path.relpath(path, root)
        target = os.path.join(archive_root, rel)
        target_dir = os.path.dirname(target)
        print(f"  Move: {path} → {target}")
        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)
            try:
                shutil.move(path, target)
                moved += 1
            except Exception as e:
                print(f"    Failed to move {path}: {e}")
    print()

print(f"Done. {'(dry-run)' if dry_run else ''} Moved {moved} files to {archive_root}.")
print('Note: Keep a backup of the archive if you need to restore files.')
