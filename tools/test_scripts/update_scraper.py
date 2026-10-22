import re
import os

file_path = 'backend/crawler/madangs_scraper.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = """
            img_locators = page.locator("img")
            count = await img_locators.count()
            print(f"총 {count}개의 이미지를 찾았습니다.")
            
            found_targets = []
            photo_count = 1
            
            for i in range(count):
                src = await img_locators.nth(i).get_attribute("src")
                alt = await img_locators.nth(i).get_attribute("alt") or ""
                
                if not src:
                    continue
                    
                # 필터링: 로고나 의미 없는 UI 아이콘 제외
                src_lower = src.lower()
                alt_lower = alt.lower()
                if "logo" in src_lower or "logo" in alt_lower or "icon" in src_lower or "btn" in src_lower or "button" in src_lower:
                    continue
                
                # 보통 부동산 사진은 /upload/ 또는 /file/ 등의 경로를 가지거나 특정 형식을 띔
                # 여기서는 필터링을 최소화하여 모두 받아옴
                if src.startswith("//"): src = "https:" + src
                elif src.startswith("/"): src = "https://madangs.com" + src
                
                filename = f"photo_{photo_count:02d}.jpg"
                target_path = os.path.join(download_dir, filename)
                
                try:
                    req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                    with open(target_path, 'wb') as f:
                        f.write(urllib.request.urlopen(req).read())
                    print(f"{filename} 다운로드 완료 ({src})")
                    found_targets.append(filename)
                    photo_count += 1
                except Exception as e:
                    print(f"{filename} 다운로드 실패: {e}")
                            
            if len(found_targets) == 0:
                print("마당스에서 일치하는 이미지를 찾지 못했습니다.")
            else:
                print(f"마당스 이미지 수집 완료: {len(found_targets)}장")
"""

# Replace the specific block from `img_locators = page.locator("img")` to `print(f"마당스 이미지 수집 완료...`
start_idx = content.find('img_locators = page.locator("img")')
end_idx = content.find('except Exception as e:', start_idx)

new_content = content[:start_idx] + new_logic.strip() + "\n                \n        " + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("madangs_scraper.py updated successfully")
