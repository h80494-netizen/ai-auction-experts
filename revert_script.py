import re

file_path = 'public/script.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = '// 1. 모든 사진 가져와서 좌측 갤러리에 추가'
end_str = '// (이전 위치도/구조도 캐러셀 처리 코드는 삭제 또는 대체됨)'

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx != -1 and end_idx != -1:
    old_script = """            // 1. 전경사진, 위치도, 내부구조도
            const carousel = document.getElementById('imageCarousel');
            const placeholderEl = document.getElementById('imagePlaceholder');
            
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
                    } else if (loadedCount + errorCount === 3) {
                        placeholderEl.innerHTML = `<i class="fa-solid fa-image-slash" style="font-size: 3rem; color: var(--danger); margin-bottom: 10px;"></i><p style="color: var(--danger); font-size: 0.9rem;">사진을 불러올 수 없습니다.</p>`;
                    }
                };

                const onLoad = () => { loadedCount++; checkDisplay(); };
                const onError = (e) => { 
                    e.target.parentElement.style.display = 'none'; // 에러난 사진 컨테이너 숨김
                    errorCount++; 
                    checkDisplay(); 
                };

                imgPhoto.onload = onLoad;
                imgMap.onload = onLoad;
                imgStruct.onload = onLoad;
                
                imgPhoto.onerror = onError;
                imgMap.onerror = onError;
                imgStruct.onerror = onError;

                imgPhoto.src = `/api/download_photo/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                imgMap.src = `/api/download_map/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                imgStruct.src = `/api/download_structure/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
            }
"""
    new_content = content[:start_idx] + old_script + content[end_idx + len(end_str):]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("public/script.js reverted successfully")
else:
    print("Could not find the sections in script.js to revert")
