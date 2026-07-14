import subprocess
import os

print("Running git fsck --lost-found to find dangling blobs...")
res_fsck = subprocess.run(["git", "fsck", "--lost-found"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)

# Parse dangling blobs
# Format: "dangling blob <hash>"
blobs = []
for line in res_fsck.stdout.split("\n"):
    if "dangling blob" in line:
        blobs.append(line.split()[-1])

print(f"Found {len(blobs)} dangling blobs.")

output_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\lost_blobs"
os.makedirs(output_dir, exist_ok=True)

for b in blobs:
    res_show = subprocess.run(["git", "cat-file", "-p", b], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
    content = res_show.stdout
    if "fetchPlanningRoads" in content or "road-flow-legend" in content:
        print(f"FOUND MATCH IN BLOB: {b} (Length: {len(content)})")
        with open(os.path.join(output_dir, f"blob_{b}.html"), "w", encoding="utf-8") as f:
            f.write(content)
