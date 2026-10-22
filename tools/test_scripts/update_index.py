import re

file_path = 'public/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the layout
# We want to change the top-level structure of `<div class="report-content-wrapper"`
# From:
# <div class="report-content-wrapper" style="display: flex; flex-direction: column; gap: 20px;">
#     <div style="display: flex; gap: 20px; width: 100%; align-items: stretch; flex-wrap: wrap;">
#         <!-- left side (images) -->
#         <!-- right side (section 1) -->
#     </div>
#     <div class="report-grid" style="display: flex; flex-direction: column; gap: 20px; width: 100%;">
#         <!-- sections 2-9 -->
#     </div>
# </div>

# To:
# <div class="report-content-wrapper" style="display: flex; gap: 20px; width: 100%; align-items: flex-start; flex-wrap: wrap;">
#     <!-- Left sticky side (images) -->
#     <div class="report-item" style="flex: 1; min-width: 300px; max-width: 400px; position: sticky; top: 20px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; border: 1px dashed rgba(187, 0, 255, 0.4); background: rgba(0,0,0,0.2); padding: 10px; max-height: 95vh; overflow-y: auto;">
#        ...
#     </div>
#     <!-- Right side (sections 1-9) -->
#     <div style="flex: 2; min-width: 400px; display: flex; flex-direction: column; gap: 20px;">
#         <!-- sections 1-9 -->
#     </div>
# </div>

# Let's use regex or string replace.
# The `public/index.html` has exactly:
# <div class="report-content-wrapper" style="display: flex; flex-direction: column; gap: 20px;">
new_wrapper_start = '<div class="report-content-wrapper" style="display: flex; gap: 20px; width: 100%; align-items: flex-start; flex-wrap: wrap;">'
content = content.replace('<div class="report-content-wrapper" style="display: flex; flex-direction: column; gap: 20px;">', new_wrapper_start)

# The old top container:
# <div style="display: flex; gap: 20px; width: 100%; align-items: stretch; flex-wrap: wrap;">
content = content.replace('<div style="display: flex; gap: 20px; width: 100%; align-items: stretch; flex-wrap: wrap;">', '<!-- 2-column container -->')

# The old photo container:
old_photo_container_start = '<div class="report-item" style="flex: 1; min-width: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px dashed rgba(187, 0, 255, 0.4); background: rgba(0,0,0,0.2); overflow: hidden; padding: 0; min-height: 300px; position: relative;">'

# Find the end of the old photo container by looking for <!-- 1. 기본정보 (우측) -->
old_photo_end_idx = content.find('<!-- 1. 기본정보 (우측) -->')

new_photo_container = """
                    <!-- 좌측 스티키 사진 갤러리 -->
                    <div class="report-item" id="leftStickyGallery" style="flex: 1; min-width: 300px; max-width: 450px; position: sticky; top: 20px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; border: 1px dashed rgba(187, 0, 255, 0.4); background: rgba(0,0,0,0.2); padding: 15px; max-height: 95vh; overflow-y: auto; scrollbar-width: thin; scrollbar-color: var(--neon-purple) transparent;">
                        <h4 style="color: white; margin-bottom: 15px; width: 100%; text-align: center; font-size: 1.2rem;"><i class="fa-solid fa-images"></i> 물건 사진</h4>
                        
                        <div id="imageGallery" style="width: 100%; display: flex; flex-direction: column; gap: 15px;">
                            <!-- 이미지들이 여기에 동적으로 추가됨 -->
                        </div>
                        
                        <div id="imagePlaceholder" style="text-align: center; width: 100%; margin-top: 50px;">
                            <i class="fa-solid fa-images" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 10px;"></i>
                            <p style="color: var(--text-muted); font-size: 0.9rem;">사진 로딩 중...</p>
                        </div>
                    </div>
"""

old_photo_start_idx = content.find(old_photo_container_start)
content = content[:old_photo_start_idx] + new_photo_container + content[old_photo_end_idx:]

# Right side container start
old_section1_start = '<!-- 1. 기본정보 (우측) -->'
new_right_side_start = """
                    <!-- 우측 보고서 본문 (1~9단계) -->
                    <div style="flex: 2; min-width: 400px; display: flex; flex-direction: column; gap: 20px; width: 100%;">
                        <!-- 1. 기본정보 -->
"""
content = content.replace(old_section1_start, new_right_side_start)

# We need to remove:
# </div>
# <!-- 2단계부터 9단계까지 각 한 행(row)씩 세로로 배치 -->
# <div class="report-grid" style="display: flex; flex-direction: column; gap: 20px; width: 100%;">
old_grid_wrapper = """                    </div>
                </div>

                <!-- 2단계부터 9단계까지 각 한 행(row)씩 세로로 배치 -->
                <div class="report-grid" style="display: flex; flex-direction: column; gap: 20px; width: 100%;">"""

new_grid_wrapper = """                    <!-- 2단계부터 9단계까지 각 한 행(row)씩 세로로 배치 -->"""
content = content.replace(old_grid_wrapper, new_grid_wrapper)

# We need to add one closing div before <!-- Disclaimer -->
old_disclaimer = '<!-- Disclaimer -->'
new_disclaimer = '</div>\n                    <!-- Disclaimer -->'
content = content.replace(old_disclaimer, new_disclaimer)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("public/index.html updated successfully")
