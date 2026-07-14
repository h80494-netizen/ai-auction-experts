import sys

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_logic = """                if (matchedLayers.some(l => l.includes('재개발') || l.includes('재건축') || l.includes('정비'))) {
                    devDetails.push("정비사업지구 추진 호재와 직결되어 인근 노후 지역의 정비 및 현대화에 따른 프리미엄 지가 상승 여력이 대단히 강력합니다.");
                }
                if (matchedLayers.some(l => l.includes('택지'))) {
                    devDetails.push("택지개발지구에 정밀 연접하여 대규모 공공 주거지 조성에 따른 도로 확장, 신축 배후 단지 등 신흥 주거 벨트 형성의 가치 상승 혜택을 선점합니다.");
                }
                if (matchedLayers.some(l => l.includes('개발행위') || l.includes('제한지역'))) {
                    devDetails.push("개발행위허가제한지역 내에 위치하여 향후 본격적인 개발 계획의 수립 및 구역 지정에 따른 프리미엄 지가 상승 여력이 강력하게 존재합니다.");
                }
                if (matchedLayers.some(l => l.includes('도로') || l.includes('노선') || l.includes('계획선'))) {
                    devDetails.push("도시계획도로 신설 및 진입로 연결 호재선에 걸쳐 차량 및 보행자 접근성이 획기적으로 향상되는 지가 상승 트리거를 갖췄습니다.");
                }
                
                if (devDetails.length > 0) {
                    valueAnalysis = `본 물건은 <strong>${matchedLayersStr}</strong> 권역 내에 위치하고 있습니다. ${subwayStr}, ${devDetails.join(' ')}`;
                } else {
                    valueAnalysis = `본 물건은 ${subwayStr}, 기본 배후 임대수요 및 정주 생활권 인프라가 견고하게 유지되는 지점입니다. 하방 경직성이 강력하여 시세 하락 리스크가 매우 낮고 중장기 지가 안정이 확실시됩니다.`;
                }\n"""

start_idx = -1
for i, line in enumerate(lines):
    if 'if (matchedLayers.some(l => l.includes(\'재개발\')' in line:
        start_idx = i
        break

if start_idx != -1:
    end_idx = -1
    for i in range(start_idx, len(lines)):
        if 'valueAnalysis = `본 물건은 ${subwayStr}, 기본 배후 임대수요 및 정주 생활권 인프라가 견고하게 유지되는 지점입니다' in lines[i]:
            for j in range(i, i+5):
                if '}' in lines[j]:
                    end_idx = j
                    break
            break

    if end_idx != -1:
        lines = lines[:start_idx] + [new_logic] + lines[end_idx+1:]
        with open('public/analysis.html', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print('Successfully replaced the logic block.')
    else:
        print('End index not found.')
else:
    print('Start index not found.')
