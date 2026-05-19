import re

file_path = 'public/script.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = '// 1. 전경사진, 위치도, 내부구조도'
end_str = 'imgStruct.onerror = onError;'

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx != -1 and end_idx != -1:
    old_script = """            // 1. 전경사진, 위치도, 내부구조도 캐러셀
            const carousel = document.getElementById('imageCarousel');
            const placeholderEl = document.getElementById('imagePlaceholder');
            const scrollHint = document.getElementById('scrollHint');
            
            const imgPhoto = document.getElementById('resultImagePhoto');
            const imgMap = document.getElementById('resultImageMap');
            const imgStruct = document.getElementById('resultImageStructure');
            
            if (carousel && placeholderEl) {
                let loadedCount = 0;
                let errorCount = 0;
                
                const checkDisplay = () => {
                    if (loadedCount > 0) {
                        carousel.style.display = 'flex';
                        placeholderEl.style.display = 'none';
                        if (loadedCount > 1 && scrollHint) {
                            scrollHint.style.display = 'block'; // 2장 이상이면 스크롤 안내
                        }
                    } else if (loadedCount + errorCount === 3) {
                        placeholderEl.innerHTML = `<i class="fa-solid fa-image-slash" style="font-size: 3rem; color: var(--danger); margin-bottom: 10px;"></i><p style="color: var(--danger); font-size: 0.9rem;">사진을 불러올 수 없습니다.</p>`;
                    }
                };

                const onLoad = () => { loadedCount++; checkDisplay(); };
                const onError = (e) => { 
                    if(e.target && e.target.parentElement) {
                        e.target.parentElement.style.display = 'none'; // 에러난 사진 컨테이너 숨김
                    }
                    errorCount++; 
                    checkDisplay(); 
                };

                imgPhoto.onload = onLoad;
                imgMap.onload = onLoad;
                imgStruct.onload = onLoad;
                
                imgPhoto.onerror = onError;
                imgMap.onerror = onError;
                imgStruct.onerror = onError;
"""
    new_content = content[:start_idx] + old_script + content[end_idx + len(end_str):]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("public/script.js fixed scrollHint successfully")
else:
    print("Could not find the sections in script.js to fix")
