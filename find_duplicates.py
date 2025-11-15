#!/usr/bin/env python3
"""
find_duplicates.py
Scan workspace for duplicate files (by SHA256) and report groups.
Usage:
  python find_duplicates.py
  python find_duplicates.py --delete  # DANGEROUS: deletes duplicates, keeps first occurrence
"""
import os
import sys
import hashlib
from collections import defaultdict

root = os.path.dirname(__file__)
exclude_dirs = {'.git','node_modules','__pycache__'}

def sha256(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

files_by_hash = defaultdict(list)

for dirpath, dirnames, filenames in os.walk(root):
    # skip excludes and the generated minified file (we still scan it though)
    dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
    for fn in filenames:
        # skip very small helper files if desired
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

# collect duplicates
dupe_groups = [v for v in files_by_hash.values() if len(v) > 1]

if not dupe_groups:
    print("No duplicate files found.")
    sys.exit(0)

print(f"Found {len(dupe_groups)} groups of duplicates:\n")
for i, group in enumerate(dupe_groups,1):
    print(f"Group {i} (count={len(group)}):")
    # sort by path for stable output
    group_sorted = sorted(group, key=lambda x: x[0])
    total = 0
    for idx,(p,s) in enumerate(group_sorted,1):
        print(f"  [{idx}] {p} — {s/1024:.1f} KB")
        total += s
    print(f"  Combined size: {total/1024:.1f} KB\n")

# If user asked to delete, remove duplicates keeping first
if '--delete' in sys.argv:
    confirm = input('Are you sure you want to delete duplicates and keep the first file of each group? (yes/NO): ')
    if confirm.lower() != 'yes':
        print('Aborted deletion.')
        sys.exit(0)
    removed = 0
    for group in dupe_groups:
        # keep the first (sorted) and delete others
        group_sorted = sorted(group, key=lambda x: x[0])
        keeper = group_sorted[0][0]
        for p,_ in group_sorted[1:]:
            try:
                os.remove(p)
                removed +=1
                print(f"Removed {p}")
            except Exception as e:
                print(f"Failed to remove {p}: {e}")
    print(f"Done. Removed {removed} files.")
else:
    print("Run with '--delete' to remove duplicate files (will prompt for confirmation).")
