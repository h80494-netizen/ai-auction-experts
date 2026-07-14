import re

file_path = "scratch/extracted_changes.txt"
print(f"Searching {file_path} for app.py modifications or crosswalk related edits...")

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Split by the separator "================================================================================"
blocks = content.split("================================================================================\n")

print(f"Total blocks found: {len(blocks)}")

relevant_blocks = []
keywords = ["crosswalk", "횡단보도", "app.py", "ai_analyzer.py"]

for idx, block in enumerate(blocks):
    block_lower = block.lower()
    # Check if this block contains any keyword
    matched_kws = [kw for kw in keywords if kw in block_lower or (kw == "횡단보도" and "횡단보도" in block)]
    if matched_kws:
        relevant_blocks.append((idx, block, matched_kws))

print(f"Found {len(relevant_blocks)} relevant blocks:\n")

for b_idx, block_text, kws in relevant_blocks:
    # Print the header of the block (first 3 lines usually contains Line, Tool, Target)
    lines = block_text.strip().split("\n")
    header = "\n".join(lines[:3])
    print(f"[Block #{b_idx}] Keywords matched: {kws}")
    print(header)
    print("-" * 40)
    # Print a preview of target and replacement contents (up to 400 chars each)
    target_match = re.search(r"\[TARGET CONTENT\]\n(.*?)(?=\n\[REPLACEMENT CONTENT\]|\Z)", block_text, re.DOTALL)
    replacement_match = re.search(r"\[REPLACEMENT CONTENT\]\n(.*)", block_text, re.DOTALL)
    
    if target_match:
        target_preview = target_match.group(1).strip()
        print("[TARGET PREVIEW]")
        print(target_preview[:400] + ("..." if len(target_preview) > 400 else ""))
    if replacement_match:
        repl_preview = replacement_match.group(1).strip()
        print("[REPLACEMENT PREVIEW]")
        print(repl_preview[:800] + ("..." if len(repl_preview) > 800 else ""))
    print("=" * 80 + "\n")
