with open('public_detail.html', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Replace the UI block
old_ui = """        	<div id="dtlw_link">
                <h3>지도보기</h3>
                <ul>
                    <li><a href="https://map.kakao.com/?map_type=TYPE_MAP&amp;q=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC+%EC%B0%BD%EC%B2%9C%EB%8F%99+72-22+105%ED%98%B8" target="_blank">전자지도</a></li>
					<li><a href="javascript:pop_detailg('roadview','Y2x0cl9tbm10X25vPTIwMjQtMDEwMC0wMDgzNzI=||');">로드뷰</a></li>
					<li><a href="https://map.kakao.com/?map_type=TYPE_SKYVIEW&amp;map_hybrid=true&amp;q=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC+%EC%B0%BD%EC%B2%9C%EB%8F%99+72-22+105%ED%98%B8" target="_blank">위성지도</a></li>
					<li><a href="https://map.kakao.com/?map_type=TYPE_MAP&amp;map_usedistrict=usedistrict&amp;q=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC+%EC%B0%BD%EC%B2%9C%EB%8F%99+72-22+105%ED%98%B8" target="_blank">지적도</a></li>
					<li><a href="https://map.naver.com/p/search/%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC+%EC%B0%BD%EC%B2%9C%EB%8F%99+72-22+105%ED%98%B8" target="_blank">네이버지도</a></li>
                </ul>
            </div>"""

new_ui = """        	<div id="dtlw_link">
                <h3>지도보기</h3>
                <ul>
                    <li><a href="https://map.kakao.com/?map_type=TYPE_MAP&amp;q=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC+%EC%B0%BD%EC%B2%9C%EB%8F%99+72-22+105%ED%98%B8" target="_blank">전자지도</a></li>
					<li><a href="javascript:pop_detailg('roadview','Y2x0cl9tbm10X25vPTIwMjQtMDEwMC0wMDgzNzI=||');">로드뷰</a></li>
					<li><a href="https://map.kakao.com/?map_type=TYPE_SKYVIEW&amp;map_hybrid=true&amp;q=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC+%EC%B0%BD%EC%B2%9C%EB%8F%99+72-22+105%ED%98%B8" target="_blank">위성지도</a></li>
					<li><a href="https://map.kakao.com/?map_type=TYPE_MAP&amp;map_usedistrict=usedistrict&amp;q=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC+%EC%B0%BD%EC%B2%9C%EB%8F%99+72-22+105%ED%98%B8" target="_blank">지적도</a></li>
					<li><a href="https://map.naver.com/p/search/%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C+%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC+%EC%B0%BD%EC%B2%9C%EB%8F%99+72-22+105%ED%98%B8" target="_blank">네이버지도</a></li>
                </ul>
            </div>
            
            <div id="dtlw_link" style="border-top: 1px dashed #e2e8f0; padding-top: 12px; margin-top: 12px;">
                <h3 style="color: #ef4444; display: flex; align-items: center; gap: 6px;"><i class="fa-solid fa-triangle-exclamation"></i> 이슈보기</h3>
                <ul>
                    <li><a href="javascript:openIssueModal();" style="color: #ef4444; font-weight: bold; text-decoration: underline;"><i class="fa-solid fa-magnifying-glass-location"></i> 지역 개발 호재/이슈 감지</a></li>
                </ul>
            </div>"""

code = code.replace(old_ui.replace('\r\n', '\n'), new_ui.replace('\r\n', '\n'))
code = code.replace(old_ui, new_ui)

# 2. Replace the bottom closing tags block to insert modal
old_closing = '<div class="balloon"></div></body></html>'

new_closing = """<!-- 이슈보기 모달 -->
<div id="issue-modal" class="chatbot-modal" style="z-index: 9999;">
    <div style="background: white; width: 100%; height: 100%; display: flex; flex-direction: column; font-family: 'Noto Sans KR', sans-serif;">
        <!-- Modal Header -->
        <div style="padding: 20px; background: #fff; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 36px; height: 36px; border-radius: 8px; background: #fee2e2; display: flex; justify-content: center; align-items: center; color: #ef4444;">
                    <i class="fa-solid fa-triangle-exclamation fa-lg"></i>
                </div>
                <div>
                    <h4 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;" id="issue-modal-title">지역 개발 초기 이슈 감지</h4>
                    <p style="margin: 2px 0 0 0; font-size: 0.75rem; color: #64748b;">지구 지정 전 입찰공고 및 사전 시그널 매일 감지</p>
                </div>
            </div>
            <button onclick="closeIssueModal()" style="border: none; background: transparent; font-size: 1.5rem; color: #94a3b8; cursor: pointer; padding: 4px; display: flex; align-items: center; justify-content: center; transition: color 0.2s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#94a3b8'">&times;</button>
        </div>
        
        <!-- Modal Content -->
        <div id="issue-modal-body" style="flex: 1; overflow-y: auto; padding: 20px; background: #f8fafc; display: flex; flex-direction: column; gap: 16px;">
            <!-- Loading indicator -->
            <div id="issue-loading" style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; height: 200px;">
                <i class="fa-solid fa-circle-notch fa-spin fa-2x" style="color: #ef4444;"></i>
                <p style="font-size: 0.85rem; color: #64748b; margin: 0;">실시간 공공 포털(나라장터, LH, 환경영향평가 등) 검색 중...</p>
            </div>
            
            <!-- Issue List Container -->
            <div id="issue-list" style="display: none; flex-direction: column; gap: 12px;"></div>
        </div>
    </div>
</div>

<style>
/* Swiping animation / chatbot-modal compatibility */
.chatbot-modal {
    position: fixed;
    bottom: -100%;
    right: 30px;
    width: 420px;
    height: 600px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    opacity: 0;
    visibility: hidden;
}
.chatbot-modal.show {
    bottom: 30px;
    opacity: 1;
    visibility: visible;
}
@media (max-width: 768px) {
    .chatbot-modal {
        right: 0;
        bottom: -100%;
        width: 100%;
        height: 100%;
        border-radius: 0;
    }
    .chatbot-modal.show {
        bottom: 0;
    }
}
</style>

<script>
// open issue modal and fetch issues
async function openIssueModal() {
    // Extract region from 소재지 text
    let region = "서대문구"; // default fallback
    const addrTd = document.querySelector('td.tdl_left');
    if (addrTd) {
        const addrText = addrTd.textContent || addrTd.innerText;
        // Search for 구 (e.g. 서대문구, 마포구, 강남구 등)
        const match = addrText.match(/([가-힣]+구)\b/);
        if (match && match[1]) {
            region = match[1];
        }
    }
    
    // Update title
    document.getElementById('issue-modal-title').textContent = `${region} 개발 초기 이슈 감지`;
    
    // Open modal
    const modal = document.getElementById('issue-modal');
    modal.classList.add('show');
    
    // Show loading
    document.getElementById('issue-loading').style.display = 'flex';
    document.getElementById('issue-list').style.display = 'none';
    document.getElementById('issue-list').innerHTML = '';
    
    try {
        // Fetch from API
        const res = await fetch(`/api/issues?region=${encodeURIComponent(region)}`);
        const json = await res.json();
        
        if (json.status === 'success' && json.data.length > 0) {
            const listContainer = document.getElementById('issue-list');
            
            json.data.forEach(issue => {
                let sourceBadgeColor = '#3b82f6'; // Blue
                let sourceBgColor = '#dbeafe';
                if (issue.source.includes('나라장터')) {
                    sourceBadgeColor = '#10b981'; // Green
                    sourceBgColor = '#d1fae5';
                } else if (issue.source.includes('LH')) {
                    sourceBadgeColor = '#f59e0b'; // Amber
                    sourceBgColor = '#fef3c7';
                } else if (issue.source.includes('환경')) {
                    sourceBadgeColor = '#8b5cf6'; // Purple
                    sourceBgColor = '#ede9fe';
                } else if (issue.source.includes('서울')) {
                    sourceBadgeColor = '#ef4444'; // Red
                    sourceBgColor = '#fee2e2';
                }
                
                const card = document.createElement('div');
                card.style.cssText = 'background: white; border-radius: 12px; border: 1px solid #e2e8f0; padding: 16px; display: flex; flex-direction: column; gap: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); transition: transform 0.2s, box-shadow 0.2s; cursor: default;';
                card.onmouseover = function() {
                    this.style.transform = 'translateY(-2px)';
                    this.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.05)';
                };
                card.onmouseout = function() {
                    this.style.transform = 'none';
                    this.style.boxShadow = '0 1px 3px rgba(0,0,0,0.02)';
                };
                
                card.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                        <span style="font-size: 0.7rem; font-weight: bold; color: ${sourceBadgeColor}; background: ${sourceBgColor}; padding: 2px 8px; border-radius: 12px;">${issue.source}</span>
                        <span style="font-size: 0.75rem; color: #94a3b8;">${issue.scanned_date}</span>
                    </div>
                    <h5 style="margin: 0; font-size: 0.85rem; font-weight: 700; color: #1e293b; line-height: 1.4;">${issue.title}</h5>
                    <div style="font-size: 0.75rem; color: #64748b; line-height: 1.5; background: #f8fafc; padding: 10px; border-radius: 8px; border-left: 3px solid ${sourceBadgeColor};">
                        ${issue.description}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                        <div style="display: flex; gap: 4px; align-items: center;">
                            <span style="font-size: 0.7rem; color: #94a3b8;">감지단어:</span>
                            <span style="font-size: 0.7rem; font-weight: bold; color: #ef4444; background: #fee2e2; padding: 1px 6px; border-radius: 4px;">${issue.keywords}</span>
                        </div>
                        <a href="${issue.url}" target="_blank" style="font-size: 0.75rem; font-weight: bold; color: #ef4444; text-decoration: none; display: flex; align-items: center; gap: 4px;">
                            공고원문 <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        </a>
                    </div>
                `;
                listContainer.appendChild(card);
            });
            
            document.getElementById('issue-loading').style.display = 'none';
            document.getElementById('issue-list').style.display = 'flex';
        } else {
            document.getElementById('issue-loading').innerHTML = `
                <i class="fa-solid fa-triangle-exclamation fa-2x" style="color: #94a3b8;"></i>
                <p style="font-size: 0.85rem; color: #64748b; margin: 0;">감지된 개발 이슈가 없습니다.</p>
            `;
        }
    } catch (e) {
        console.error("Error loading issues:", e);
        document.getElementById('issue-loading').innerHTML = `
            <i class="fa-solid fa-circle-exclamation fa-2x" style="color: #ef4444;"></i>
            <p style="font-size: 0.85rem; color: #64748b; margin: 0;">실시간 이슈 데이터를 가져오는 데 실패했습니다.</p>
        `;
    }
}

function closeIssueModal() {
    const modal = document.getElementById('issue-modal');
    modal.classList.remove('show');
}
</script>
<div class="balloon"></div></body></html>"""

code = code.replace(old_closing.replace('\r\n', '\n'), new_closing.replace('\r\n', '\n'))
code = code.replace(old_closing, new_closing)

with open('public_detail.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("Modification of public_detail.html complete!")
