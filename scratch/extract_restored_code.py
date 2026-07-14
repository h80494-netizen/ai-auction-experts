with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\workspace_search_results.txt", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Let's search for "initRoadFlowLegendControls" or "dragHandle" or "scaleSlider"
keywords = ["initRoadFlowLegendControls", "dragHandle", "scaleSlider", "Antigravity 프리미엄 에디션"]
for kw in keywords:
    print(f"Keyword '{kw}' in workspace_search_results.txt:", kw in content)
