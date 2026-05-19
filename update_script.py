import re

file_path = 'public/script.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '// 1. 전경사진, 위치도, 내부구조도 캐러셀'
# Actually, the old script might have different structure now, but let's just find the start of image loading block.
# and replace it.

start_idx = content.find(start_marker)
end_idx = content.find('// 3. 내부구조도', start_idx)

if start_idx == -1:
    print("Could not find start marker in script.js")
else:
    if end_idx == -1:
        end_idx = content.find('// 4.', start_idx)

    new_image_logic = """
            // 1. 모든 사진 가져와서 좌측 갤러리에 추가
            const imageGallery = document.getElementById('imageGallery');
            const placeholderEl = document.getElementById('imagePlaceholder');
            
            if (imageGallery && placeholderEl) {
                // 기존 갤러리 비우기
                imageGallery.innerHTML = '';
                placeholderEl.style.display = 'block';
                placeholderEl.innerHTML = `<div class="spinner" style="display:inline-block; border-top-color:var(--neon-purple);"></div><p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 10px;">사진 로딩 중...</p>`;
                
                try {
                    const res = await fetch(`/api/images/${encodeURIComponent(safeCaseNum)}`);
                    const imgData = await res.json();
                    
                    if (imgData.status === "success" && imgData.images.length > 0) {
                        placeholderEl.style.display = 'none';
                        
                        imgData.images.forEach(filename => {
                            const imgContainer = document.createElement('div');
                            imgContainer.style.width = '100%';
                            imgContainer.style.position = 'relative';
                            imgContainer.style.borderRadius = '8px';
                            imgContainer.style.overflow = 'hidden';
                            imgContainer.style.border = '1px solid rgba(255,255,255,0.1)';
                            
                            const img = document.createElement('img');
                            img.src = `/api/download_image/${encodeURIComponent(safeCaseNum)}/${encodeURIComponent(filename)}?t=${new Date().getTime()}`;
                            img.alt = "물건 사진";
                            img.style.width = '100%';
                            img.style.display = 'block';
                            img.style.objectFit = 'cover';
                            
                            // 로딩 에러 시 숨김
                            img.onerror = () => { imgContainer.style.display = 'none'; };
                            
                            const label = document.createElement('div');
                            label.style.position = 'absolute';
                            label.style.top = '10px';
                            label.style.left = '10px';
                            label.style.background = 'rgba(0,0,0,0.7)';
                            label.style.color = 'white';
                            label.style.padding = '4px 8px';
                            label.style.borderRadius = '4px';
                            label.style.fontSize = '0.8rem';
                            label.innerText = filename;
                            
                            imgContainer.appendChild(img);
                            imgContainer.appendChild(label);
                            imageGallery.appendChild(imgContainer);
                        });
                    } else {
                        placeholderEl.innerHTML = `<i class="fa-solid fa-image-slash" style="font-size: 3rem; color: var(--danger); margin-bottom: 10px;"></i><p style="color: var(--danger); font-size: 0.9rem;">이미지를 찾을 수 없습니다.</p>`;
                    }
                } catch (e) {
                    console.error('이미지 로딩 에러:', e);
                    placeholderEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="font-size: 3rem; color: var(--warning); margin-bottom: 10px;"></i><p style="color: var(--warning); font-size: 0.9rem;">이미지 로드 중 오류 발생</p>`;
                }
            }

            // (이전 위치도/구조도 캐러셀 처리 코드는 삭제 또는 대체됨)
"""
    new_content = content[:start_idx] + new_image_logic + "\n            " + content[end_idx:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("public/script.js updated successfully")
