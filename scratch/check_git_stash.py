import subprocess

output_file = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\git_stash_list.txt"

res = subprocess.run(["git", "stash", "list"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("=== STASHES ===\n" + res.stdout + "\n")
    
    # If there are stashes, show the first one
    if res.stdout.strip():
        res_show = subprocess.run(["git", "stash", "show", "-p", "stash@{0}"], capture_output=True, text=True, encoding="utf-8", errors="ignore", shell=True)
        f.write("=== STASH 0 DETAILS ===\n" + res_show.stdout + "\n")

print("Done! Git stash list written.")
