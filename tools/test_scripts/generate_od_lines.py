from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsPointXY,
    QgsMessageLog,
    Qgis
)
from PyQt5.QtCore import QVariant

def run():
    project = QgsProject.instance()
    
    # 1. 레이어 찾기
    adm_layer = project.mapLayersByName('행정동')
    od_layer = project.mapLayersByName('서울유동인구OD')
    
    if not adm_layer:
        print("오류: '행정동' 레이어를 찾을 수 없습니다.")
        return
    if not od_layer:
        print("오류: '서울유동인구OD' 레이어를 찾을 수 없습니다.")
        return
        
    adm_layer = adm_layer[0]
    od_layer = od_layer[0]
    
    print("레이어 로딩 완료. 중심점 추출 시작...")
    
    # 2. 행정동 중심점 추출
    centroids = {}
    for f in adm_layer.getFeatures():
        adm_cd = str(f['adm_cd']).strip()
        geom = f.geometry()
        if geom and not geom.isEmpty():
            pt = geom.centroid().asPoint()
            centroids[adm_cd] = pt
            
    print(f"중심점 추출 완료: {len(centroids)}개 행정동")
    print("OD 데이터 집계 시작 (동일 행정동 내 이동 제외)...")
    
    # 3. OD 데이터 집계 (총 446만 건이므로 중복된 출발/도착지 그룹핑 필요)
    od_agg = {}
    total_features = od_layer.featureCount()
    count = 0
    
    for f in od_layer.getFeatures():
        count += 1
        if count % 500000 == 0:
            print(f"OD 집계 진행 중: {count}/{total_features}")
            
        o_cd = str(f['o_admdong_cd']).strip()
        d_cd = str(f['d_admdong_cd']).strip()
        
        # 제자리 이동 제외 (출발지 == 도착지)
        if o_cd == d_cd:
            continue
            
        cnt = f['total_cnt']
        if not cnt:
            continue
        try:
            cnt = float(cnt)
        except:
            continue
            
        key = (o_cd, d_cd)
        od_agg[key] = od_agg.get(key, 0) + cnt
        
    print(f"OD 집계 완료. 총 {len(od_agg)}개의 고유 이동 경로 생성됨.")
    print("라인(Line) 레이어 생성 중...")
    
    # 4. 새 라인 레이어 생성
    crs = adm_layer.crs().authid()
    vl = QgsVectorLayer(f"LineString?crs={crs}", "OD_Flow_Lines", "memory")
    pr = vl.dataProvider()
    
    # 속성 추가
    pr.addAttributes([
        QgsField("origin_cd", QVariant.String),
        QgsField("dest_cd", QVariant.String),
        QgsField("total_flow", QVariant.Double)
    ])
    vl.updateFields()
    
    # 5. 라인 피처 생성
    features = []
    missing_points = 0
    
    for (o_cd, d_cd), cnt in od_agg.items():
        if o_cd in centroids and d_cd in centroids:
            pt1 = centroids[o_cd]
            pt2 = centroids[d_cd]
            
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPolylineXY([pt1, pt2]))
            feat.setAttributes([o_cd, d_cd, cnt])
            features.append(feat)
        else:
            missing_points += 1
            
    pr.addFeatures(features)
    vl.updateExtents()
    
    # 6. QGIS에 레이어 추가
    project.addMapLayer(vl)
    
    print(f"작업 완료! 화면에 'OD_Flow_Lines' 레이어가 추가되었습니다.")
    if missing_points > 0:
        print(f"참고: 행정동 경계 데이터에 코드가 없어 연결되지 못한 경로가 {missing_points}개 있습니다.")

# 실행
run()
