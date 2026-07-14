import re

file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\public\issues.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content_lf = content.replace("\r\n", "\n")

target_media_query = """        /* Responsive adjustments */
        @media (max-width: 768px) {
            .issue-card {
                flex-direction: column;
            }
            .priority-col {
                border-left: none;
                border-top: 1px dashed rgba(255, 255, 255, 0.1);
                padding-left: 0;
                padding-top: 16px;
                align-items: flex-start;
                min-width: 100%;
            }
            .search-row {
                flex-direction: column;
                align-items: stretch;
            }
            .scan-btn {
                width: 100%;
                justify-content: center;
            }
            .title {
                font-size: 2.1rem;
            }
            .filter-row {
                flex-direction: column;
                align-items: stretch;
            }
            .limit-container {
                width: 100%;
                justify-content: space-between;
            }
        }"""

replacement_media_query = """        /* Responsive adjustments */
        @media (max-width: 768px) {
            .issue-card {
                flex-direction: column;
            }
            .priority-col {
                border-left: none;
                border-top: 1px dashed rgba(255, 255, 255, 0.1);
                padding-left: 0;
                padding-top: 16px;
                align-items: flex-start;
                min-width: 100%;
            }
            .search-row {
                flex-direction: column;
                align-items: stretch;
            }
            .scan-btn {
                width: 100%;
                justify-content: center;
            }
            .title {
                font-size: 2.1rem;
            }
            .filter-row {
                flex-direction: column;
                align-items: stretch;
            }
            .limit-container {
                width: 100%;
                justify-content: space-between;
            }
            
            /* 모바일 이슈상세 모달 뷰 개선 (스크롤 및 레이아웃 넘침 방지) */
            .detail-modal-dialog {
                border-radius: 16px !important;
                width: 95% !important;
            }
            .detail-modal-header {
                padding: 14px 16px !important;
            }
            .detail-modal-header h3 {
                font-size: 1.1rem !important;
            }
            .detail-modal-body {
                padding: 14px 16px !important;
                gap: 16px !important;
                max-height: calc(100vh - 130px) !important;
            }
            .detail-map-container {
                height: 220px !important;
            }
            
            /* 모바일 대시보드 스태츠 위젯 레이아웃 개선 */
            .stat-grid {
                grid-template-columns: 1fr !important;
                gap: 12px !important;
                margin-bottom: 20px !important;
            }
            .stat-card {
                padding: 14px 16px !important;
            }
            
            /* 모바일 퀵포탈 이동 바 레이아웃 개선 */
            .quick-portals-bar {
                flex-direction: column !important;
                align-items: stretch !important;
                padding: 14px 16px !important;
                gap: 10px !important;
            }
            .portal-quick-buttons {
                justify-content: center !important;
                gap: 8px !important;
                width: 100% !important;
            }
            .quick-portal-btn {
                flex: 1 !important;
                min-width: 120px !important;
                font-size: 0.78rem !important;
                padding: 6px 10px !important;
            }
        }"""

# Apply replacement
target_lf = target_media_query.replace("\r\n", "\n")
replacement_lf = replacement_media_query.replace("\r\n", "\n")

if target_lf in content_lf:
    new_content = content_lf.replace(target_lf, replacement_lf)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SUCCESS: Beautifully applied responsive CSS overrides to issues.html!")
else:
    print("ERROR: Target media query block not found in issues.html!")
