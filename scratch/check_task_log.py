import os
import glob

tasks_dir = r"C:\Users\llll\.gemini\antigravity-ide\brain\03a97b0d-7beb-4c39-896d-4743ddee2934\.system_generated\tasks"
if os.path.exists(tasks_dir):
    print("Files in tasks dir:")
    for f in glob.glob(os.path.join(tasks_dir, "*")):
        print(f, os.path.getsize(f))
else:
    print("Tasks dir does not exist")
