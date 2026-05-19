import re

file_path = 'public/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the new gallery with the old carousel inside the sticky bar.
# Find the sticky bar start
start_str = '<div id="imageGallery"'
end_str = '<!-- 우측 보고서 본문'

start_idx = content.find(start_str)
end_idx = content.find(end_str)

new_gallery = """<div id="imageCarousel" style="width: 100%; height: 100%; display: none; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: thin; scrollbar-color: var(--neon-purple) transparent; display: flex; flex-direction: column; gap: 10px;">
                            <div style="min-width: 100%; height: auto; position: relative; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden; margin-bottom: 10px;">
                                <img id="resultImagePhoto" src="" alt="전경사진" style="width: 100%; object-fit: cover;">
                                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); padding: 5px 10px; border-radius: 5px; font-size: 0.9rem; font-weight: bold; color: white;">Ⅰ. 전경사진</div>
                            </div>
                            <div style="min-width: 100%; height: auto; position: relative; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden; margin-bottom: 10px;">
                                <img id="resultImageMap" src="" alt="위치도" style="width: 100%; object-fit: cover;">
                                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); padding: 5px 10px; border-radius: 5px; font-size: 0.9rem; font-weight: bold; color: white;">Ⅱ. 위치도</div>
                            </div>
                            <div style="min-width: 100%; height: auto; position: relative; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden; margin-bottom: 10px;">
                                <img id="resultImageStructure" src="" alt="내부구조도" style="width: 100%; object-fit: cover;">
                                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); padding: 5px 10px; border-radius: 5px; font-size: 0.9rem; font-weight: bold; color: white;">Ⅲ. 내부구조도</div>
                            </div>
                        </div>
                        
                        <div id="imagePlaceholder" style="text-align: center; width: 100%; margin-top: 50px;">
                            <i class="fa-solid fa-images" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 10px;"></i>
                            <p style="color: var(--text-muted); font-size: 0.9rem;">사진 3장 로딩 중...</p>
                        </div>
                    </div>
                    
"""

new_content = content[:start_idx] + new_gallery + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("public/index.html updated successfully")
