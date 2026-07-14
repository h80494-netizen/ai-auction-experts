log_path = r"C:\Users\llll\.gemini\antigravity-ide\brain\2a0f1800-2888-415a-947f-7bb96d1ef91a\.system_generated\logs\transcript.jsonl"
out_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\matched_logs.txt"

with open(log_path, 'r', encoding='utf-8') as f, open(out_path, 'w', encoding='utf-8') as out:
    for line in f:
        if 'console' in line.lower() or 'log' in line.lower():
            out.write(line[:2000] + "\n") # write first 2000 chars of matching lines

print("Finished writing matched lines.")
