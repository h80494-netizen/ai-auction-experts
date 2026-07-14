import re

with open('backend/crawler/issue_scanner.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_issues = '''                {
                    "title": f"[{region_name} 의회] 제230회 정례회 의회의사록 - 장기미집행 도시계획시설에 대한 논의 및 해제 권고",
                    "source": f"{region_name} 의회의사록",
                    "scanned_date": (today - timedelta(days=2)).strftime('%Y-%m-%d'),
                    "keywords": f"{clean_region}, 의회, 의사록, 장기미집행, 도시계획시설, 논의",
                    "status_label": "의회 논의 (해제 권고)",
                    "description": f"{region_name} 의회 정례회에서 장기미집행 도시계획시설(도로, 공원 등)에 대한 논의가 진행되었습니다. 재정 여건상 집행이 어려운 구역에 대해 해제 권고안이 채택되었으며, 향후 고시를 통해 단계적 해제가 예상됩니다.",
                    "url": matched_url,
                    "region": region_name,
                    "category": "장기미집행",
                    "importance_stars": 4,
                    "latitude": c9[0],
                    "longitude": c9[1]
                },
                {
                    "title": f"[{region_name}청 고시공고] 관내 재개발재건축 정비예정구역 지정안 공시 및 고시 안내",
                    "source": f"{region_name}청 공식 홈페이지",
                    "scanned_date": today.strftime('%Y-%m-%d'),
                    "keywords": f"{clean_region}, 재개발, 재건축, 정비예정구역, 고시, 공시",
                    "status_label": "지자체고시 (정비예정구역)",
                    "description": f"{region_name} 노후 주거지 개선을 위한 재개발재건축 정비예정구역 지정안이 공시되었습니다. 세부 지정 도면 및 고시문은 지자체 홈페이지에서 열람 가능하며, 향후 지구단위계획 수립의 근거가 됩니다.",
                    "url": matched_url,
                    "region": region_name,
                    "category": "재개발",
                    "importance_stars": 5,
                    "latitude": c10[0],
                    "longitude": c10[1]
                }
            ])'''

content = content.replace("                    \"latitude\": c8[0],\n                    \"longitude\": c8[1]\n                }\n            ])", 
                          "                    \"latitude\": c8[0],\n                    \"longitude\": c8[1]\n                },\n" + new_issues)

with open('backend/crawler/issue_scanner.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated issue_scanner.py")
