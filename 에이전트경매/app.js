document.addEventListener('DOMContentLoaded', () => {
    const navList = document.getElementById('nav-list');
    
    // DOM Elements for Main Content
    const partBadge = document.getElementById('part-badge');
    const slideTitle = document.getElementById('slide-title');
    const timeBadge = document.getElementById('time-badge');
    const theoryList = document.getElementById('theory-list');
    const agentIcon = document.getElementById('agent-icon');
    const agentName = document.getElementById('agent-name');
    const promptSystem = document.getElementById('prompt-system');
    const promptUser = document.getElementById('prompt-user');
    const mainContent = document.querySelector('.main-content');
    
    // Initialization
    function init() {
        renderNav();
        if(curriculumData.length > 0) {
            renderSlide(curriculumData[0].id);
        }
    }

    // Render Sidebar Navigation
    function renderNav() {
        navList.innerHTML = '';
        curriculumData.forEach((item) => {
            const li = document.createElement('li');
            li.className = 'nav-item';
            li.dataset.id = item.id;
            
            li.innerHTML = `
                <div class="nav-part">${item.part} (${item.time})</div>
                <div class="nav-title">${item.title}</div>
            `;
            
            li.addEventListener('click', () => {
                // Update active state
                document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
                li.classList.add('active');
                
                // Render content
                renderSlide(item.id);
            });
            
            navList.appendChild(li);
        });
        
        // Set first item as active initially
        if(navList.firstChild) {
            navList.firstChild.classList.add('active');
        }
    }

    // Render Slide Content
    function renderSlide(id) {
        const data = curriculumData.find(item => item.id === id);
        if(!data) return;

        // Add fade animation
        mainContent.style.animation = 'none';
        mainContent.offsetHeight; /* trigger reflow */
        mainContent.style.animation = null; 

        // Update Header
        partBadge.textContent = data.part;
        slideTitle.textContent = data.title;
        timeBadge.textContent = data.time;

        // Update Theory
        theoryList.innerHTML = '';
        data.theory.forEach(text => {
            const li = document.createElement('li');
            li.textContent = text;
            theoryList.appendChild(li);
        });

        // Update Agent UI
        agentIcon.textContent = data.agentIcon;
        agentName.textContent = data.agentName;
        promptSystem.textContent = data.promptSystem;
        promptUser.textContent = data.promptUser;
    }

    init();
});

// Global Copy Function for the Button
function copyPrompt() {
    const sysText = document.getElementById('prompt-system').textContent;
    const userText = document.getElementById('prompt-user').textContent;
    const fullText = `[System]\n${sysText}\n\n[User]\n${userText}`;
    
    navigator.clipboard.writeText(fullText).then(() => {
        const btn = document.getElementById('copy-btn');
        const originalText = btn.textContent;
        btn.textContent = '복사 완료! ✅';
        btn.style.background = '#10b981'; // green
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = 'var(--accent-blue)';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy!', err);
        alert('복사에 실패했습니다.');
    });
}
