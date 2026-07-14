import os

files = os.listdir("c:/Users/llll/Documents/두인경매/바이브코딩/scratch")
print(f"Total files in scratch: {len(files)}")
for f in sorted(files):
    fpath = os.path.join("c:/Users/llll/Documents/두인경매/바이브코딩/scratch", f)
    # Check if file has planning, road, zoning, or dev
    if any(k in f.lower() for k in ["planning", "road", "zoning", "dev"]):
        print(f"  {f} ({os.path.getsize(fpath)} bytes)")
