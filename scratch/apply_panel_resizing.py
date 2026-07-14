with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace Left/Right Panel CSS
css_left_target = """        /* Left Panel - Layers */
        #left-panel {
            top: 90px;
            left: 15px;
            width: 250px;
        }

        /* Right Panel - Filters */
        #right-panel {
            top: 90px;
            right: 15px;
            width: 280px;
        }"""

css_left_replacement = """        /* Left Panel - Layers */
        #left-panel {
            top: 90px;
            left: 15px;
            width: 220px;
            font-size: 0.75rem;
        }
        #left-panel .panel-header {
            padding: 8px 12px;
            font-size: 0.8rem;
        }
        #left-panel .panel-content {
            padding: 10px 12px;
            gap: 10px;
        }
        #left-panel .layer-group-title {
            font-size: 0.75rem;
            margin-top: 10px !important;
            margin-bottom: 4px;
        }
        #left-panel .toggle-label {
            font-size: 0.75rem;
        }
        #left-panel .toggle-row {
            padding: 4px 0;
        }
        #left-panel .toggle-desc {
            font-size: 0.65rem;
        }
        #left-panel input, #left-panel select, #left-panel button {
            font-size: 0.75rem;
        }

        /* Right Panel - Filters */
        #right-panel {
            top: 90px;
            right: 15px;
            width: 240px;
            font-size: 0.75rem;
        }
        #right-panel .panel-header {
            padding: 8px 12px;
            font-size: 0.8rem;
        }
        #right-panel .panel-content {
            padding: 10px 12px;
            gap: 10px;
        }
        #right-panel .checkbox-item {
            font-size: 0.7rem;
            padding: 4px;
        }
        #right-panel .btn-primary {
            padding: 8px;
            font-size: 0.8rem;
        }
        #right-panel .btn-secondary {
            padding: 8px;
            font-size: 0.8rem;
        }
        #right-panel .range-labels {
            font-size: 0.7rem;
        }
        #right-panel input, #right-panel select, #right-panel button {
            font-size: 0.75rem;
        }"""

# Normalize line endings for replacement
content_lf = content.replace('\r\n', '\n')
css_left_target_lf = css_left_target.replace('\r\n', '\n')
css_left_replacement_lf = css_left_replacement.replace('\r\n', '\n')

if css_left_target_lf in content_lf:
    content_lf = content_lf.replace(css_left_target_lf, css_left_replacement_lf)
    print("SUCCESS: Replaced panel CSS")
else:
    print("ERROR: Panel CSS target not found")

# 2. Replace road-flow-legend inline styles and contents
legend_target = """    <!-- 유동동선 라인맵 5단계 범례 -->
    <div id="road-flow-legend" style="display: none; position: absolute; top: 90px; right: 20px; z-index: 1000; background: white; padding: 12px 15px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); border: 1px solid var(--border-color); font-family: 'Noto Sans KR', sans-serif; min-width: 140px; pointer-events: auto;">
        <div style="font-weight: bold; font-size: 0.9rem; margin-bottom: 10px; color: #1e293b; text-align: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">유동 강도 범례</div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 5px; background: #7f1d1d; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">매우 높음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 5px; background: #b91c1c; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">높음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 5px; background: #ea580c; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">보통</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 5px; background: #ca8a04; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">낮음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 25px; height: 5px; background: #16a34a; border-radius: 2px;"></div>
                    <span style="font-weight: 500; color: #334155;">매우 낮음</span>
                </div>
            </div>
        </div>
    </div>"""

legend_replacement = """    <!-- 유동동선 라인맵 5단계 범례 -->
    <div id="road-flow-legend" style="display: none; position: absolute; bottom: 20px; left: 20px; z-index: 1000; background: white; padding: 8px 10px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); border: 1px solid var(--border-color); font-family: 'Noto Sans KR', sans-serif; min-width: 120px; pointer-events: auto;">
        <div style="font-weight: bold; font-size: 0.75rem; margin-bottom: 6px; color: #1e293b; text-align: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 4px;">유동 강도 범례</div>
        <div style="display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 20px; height: 4px; background: #7f1d1d; border-radius: 1px;"></div>
                    <span style="font-weight: 500; color: #334155;">매우 높음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 20px; height: 4px; background: #b91c1c; border-radius: 1px;"></div>
                    <span style="font-weight: 500; color: #334155;">높음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 20px; height: 4px; background: #ea580c; border-radius: 1px;"></div>
                    <span style="font-weight: 500; color: #334155;">보통</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 20px; height: 4px; background: #ca8a04; border-radius: 1px;"></div>
                    <span style="font-weight: 500; color: #334155;">낮음</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.65rem;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 20px; height: 4px; background: #16a34a; border-radius: 1px;"></div>
                    <span style="font-weight: 500; color: #334155;">매우 낮음</span>
                </div>
            </div>
        </div>
    </div>"""

legend_target_lf = legend_target.replace('\r\n', '\n')
legend_replacement_lf = legend_replacement.replace('\r\n', '\n')

if legend_target_lf in content_lf:
    content_lf = content_lf.replace(legend_target_lf, legend_replacement_lf)
    print("SUCCESS: Replaced road-flow-legend styling and size")
else:
    # Try a simple text replacement for the div tag only
    simple_tag = 'id="road-flow-legend" style="display: none; position: absolute; top: 90px; right: 20px;'
    if simple_tag in content_lf:
        content_lf = content_lf.replace(simple_tag, 'id="road-flow-legend" style="display: none; position: absolute; bottom: 20px; left: 20px;')
        print("SUCCESS: Replaced legend tag position (fallback)")
    else:
        print("ERROR: Road-flow-legend target not found")

with open('public/map.html', 'w', encoding='utf-8') as f:
    f.write(content_lf)
print("Finished applying resizing updates.")
