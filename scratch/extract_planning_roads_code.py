import re

files_to_check = [
    'scratch/apply_complete_planning_upgrades.py',
    'scratch/apply_complete_map_speedups.py',
    'scratch/modify_map_stages.py'
]

output_file = 'scratch/extracted_layers_code.txt'
with open(output_file, 'w', encoding='utf-8') as out:
    for filename in files_to_check:
        out.write(f"\n=========================================\n")
        out.write(f"FILE: {filename}\n")
        out.write(f"=========================================\n")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find definitions of functions: fetchPlanningRoads, fetchZoningPolygons, fetchRedevelopmentZones, updateTaekjiLayer
            funcs = ['fetchPlanningRoads', 'fetchZoningPolygons', 'fetchRedevelopmentZones', 'updateTaekjiLayer', 'getTaekjiStage']
            for fn in funcs:
                out.write(f"\n--- Function: {fn} ---\n")
                # Look for the function definition and print around it (up to 150 lines)
                pos = content.find(f"function {fn}")
                if pos == -1:
                    pos = content.find(f"{fn}(")
                if pos != -1:
                    start_idx = max(0, pos - 100)
                    end_idx = min(len(content), pos + 3000)
                    out.write(content[start_idx:end_idx])
                    out.write("\n... [END OF EXTRACT] ...\n")
                else:
                    out.write("Not found.\n")
                    
        except Exception as e:
            out.write(f"Error reading file: {e}\n")

print("Done! Check scratch/extracted_layers_code.txt")
