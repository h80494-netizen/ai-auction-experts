import json
import os

files_to_apply = [
    r"scratch/extracted_prev_session/step_73_call_0_ai_analyzer.py.txt",
    r"scratch/extracted_prev_session/step_79_call_0_app.py.txt",
    r"scratch/extracted_prev_session/step_81_call_0_app.py.txt"
]

for fp in files_to_apply:
    if not os.path.exists(fp):
        print(f"Skipping {fp} because it does not exist.")
        continue
        
    print(f"Applying {fp}...")
    with open(fp, 'r', encoding='utf-8') as f:
        args = json.load(f)
        
    target_file = args.get('TargetFile')
    if not target_file:
        print("No TargetFile specified in arguments.")
        continue
        
    # Standardize target_file path
    target_file = target_file.replace('"', '').replace("'", "").strip()
    target_file = os.path.abspath(target_file)
    
    if not os.path.exists(target_file):
        # Try local path inside workspace
        rel_path = target_file.split('바이브코딩')[-1].strip('\\/')
        target_file = os.path.abspath(rel_path)
        
    if not os.path.exists(target_file):
        print(f"Target file {target_file} not found.")
        continue
        
    target_content = args.get('TargetContent')
    replacement_content = args.get('ReplacementContent')
    
    if target_content is None or replacement_content is None:
        print("TargetContent or ReplacementContent is missing in arguments.")
        continue
        
    with open(target_file, 'r', encoding='cp949', errors='ignore') as f:
        file_content = f.read()
        
    # Standardize line endings for matching
    file_content_lf = file_content.replace('\r\n', '\n')
    target_content_lf = target_content.replace('\r\n', '\n')
    replacement_content_lf = replacement_content.replace('\r\n', '\n')
    
    if target_content_lf in file_content_lf:
        file_content_lf = file_content_lf.replace(target_content_lf, replacement_content_lf)
        with open(target_file, 'w', encoding='cp949', errors='ignore') as f:
            f.write(file_content_lf)
        print(f"SUCCESS: Applied replacement to {target_file}!")
    else:
        # Try partial match or check if already replaced
        if replacement_content_lf in file_content_lf:
            print(f"ALREADY APPLIED: Replacement already present in {target_file}.")
        else:
            print(f"ERROR: TargetContent not found in {target_file}!")
            # Let's debug by printing lengths
            print(f"Target length: {len(target_content_lf)}")
            print(f"Sample of target content: {target_content_lf[:100]}...")
            print(f"File content sample around length: {file_content_lf[:300]}...")
