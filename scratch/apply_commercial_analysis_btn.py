file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Normalize line endings to LF
content_lf = content.replace("\r\n", "\n")

replacements = []

# 1. Remove automatic openDemandPanel call on marker click
replacements.append((
    """                        marker.on('click', function(e) {
                            openDemandPanel(item.lat, item.lng, item.case_no, item.address, item.property_type);
                        });""",
    "" # Delete this click handler completely
))

# 2. Add Commercial Analysis button next to Right Analysis Report button in bindPopup
replacements.append((
    """                                    <button onclick="window.innerWidth <= 768 ? window.location.href='/?case=${d.case_no}' : (window.opener ? (window.opener.location.href='/?case=${d.case_no}', window.opener.focus()) : window.open('/?case=${d.case_no}', '_blank'))" style="width:100%; background:var(--primary-blue); color:white; border:none; padding:12px 10px; border-radius:6px; cursor:pointer; font-size:1rem; font-weight:bold; touch-action:manipulation;">권리분석 리포트 보기</button>""",
    """                                    <button onclick="window.innerWidth <= 768 ? window.location.href='/?case=${d.case_no}' : (window.opener ? (window.opener.location.href='/?case=${d.case_no}', window.opener.focus()) : window.open('/?case=${d.case_no}', '_blank'))" style="width:100%; background:var(--primary-blue); color:white; border:none; padding:12px 10px; border-radius:6px; cursor:pointer; font-size:1rem; font-weight:bold; touch-action:manipulation;">권리분석 리포트 보기</button>
                                    <button onclick="openDemandPanel(${d.lat}, ${d.lng}, '${d.case_no}', '${d.address}', '${d.property_type}')" style="width:100%; margin-top:8px; background:#10b981; color:white; border:none; padding:12px 10px; border-radius:6px; cursor:pointer; font-size:1rem; font-weight:bold; touch-action:manipulation;"><i class="fa-solid fa-store"></i> 상권분석 (인구/배후수요)</button>"""
))

success_count = 0
for idx, (target, replacement) in enumerate(replacements):
    target_lf = target.replace("\r\n", "\n")
    replacement_lf = replacement.replace("\r\n", "\n")
    if target_lf in content_lf:
        content_lf = content_lf.replace(target_lf, replacement_lf)
        print(f"SUCCESS: Replaced popup segment {idx+1}")
        success_count += 1
    else:
        print(f"ERROR: Target block for popup segment {idx+1} not found in map.html!")

if success_count == len(replacements):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content_lf)
    print("\nCOMMERCIAL ANALYSIS BUTTON RESTORED SUCCESSFULLY!")
else:
    print(f"\nFailed to restore button. Applied {success_count}/{len(replacements)}.")
