import re

file_path = 'backend/crawler/madangs_scraper.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('img_locators = page.locator("img")')
end_idx = content.find('except Exception as e:', start_idx)

old_logic = """img_locators = page.locator("img")
            count = await img_locators.count()
            print(f"총 {count}개의 이미지를 찾았습니다.")
            
            # 대상 파일명 설정
            targets = {
                "전경": "photo.jpg",
                "위치도": "map.jpg",          # '위 치 도' 매칭
                "내부구조도": "structure.jpg"  # '내 부 구 조 도' 매칭
            }
            found_targets = []
            
            for i in range(count):
                src = await img_locators.nth(i).get_attribute("src")
                alt = await img_locators.nth(i).get_attribute("alt")
                if not src or not alt:
                    continue
                    
                alt_clean = alt.replace(" ", "")
                
                for key, filename in targets.items():
                    if key in alt_clean and filename not in found_targets:
                        if src.startswith("//"): src = "https:" + src
                        elif src.startswith("/"): src = "https://madangs.com" + src
                        
                        target_path = os.path.join(download_dir, filename)
                        print(f"[{key}] 이미지 발견: {src} -> {filename}")
                        
                        try:
                            req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
                            with open(target_path, 'wb') as f:
                                f.write(urllib.request.urlopen(req).read())
                            print(f"{filename} 다운로드 완료 (마당스 팝업 소스)")
                            found_targets.append(filename)
                        except Exception as e:
                            print(f"{filename} 다운로드 실패: {e}")
                            
            if len(found_targets) == 0:
                print("마당스에서 일치하는 이미지를 찾지 못했습니다.")
            else:
                print(f"마당스 이미지 수집 완료: {', '.join(found_targets)}")
                
        """

new_content = content[:start_idx] + old_logic + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("backend/crawler/madangs_scraper.py reverted successfully")
