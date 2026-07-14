3715:                             <span style="font-size: 0.8rem; font-weight: bold; color: var(--text-dark);">지하철 접근성</span>
3716:                             <span class="demand-subway-badge ${gradeBadgeClass}">${sub.grade}</span>
3717:                         </div>
3718:                         <div class="demand-subway-list">
3719:                             ${subwayListHtml}
3720:                         </div>
3721:                     </div>
3722: 
3723:                     <!-- Expert Evaluation -->
3724:                     <div class="demand-card" style="background: rgba(37, 99, 235, 0.05); bord        // Drag-and-drop & Resizing Helper with Automatic Font Scaling
3725:         function makeDraggableAndResizable(el, handleClass) {
3726:             let isDragging = false;
3727:             let isResizing = false;
3728:             let startX = 0, startY = 0, startWidth = 0, startHeight = 0, startLeft = 0, startTop = 0;
3729:             let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
3730: 
3731:             const handle = el.querySelector(handleClass) || el;
3732:             handle.style.cursor = 'move';
3733: 
3734:             // Store original font sizes of all sub-elements for scaling
3735:             const textElements = [];
3736:             const collectTextElements = () => {
3737:                 textElements.length = 0;
3738:                 const allElems = [el, ...Array.from(el.querySelectorAll('*'))];
3739:                 allElems.forEach(child => {
3740:                     const computedStyle = window.getComputedStyle(child);
3741:                     const fontSizeStr = computedStyle.fontSize;
3742:                     if (fontSizeStr && fontSizeStr.endsWith('px')) {
3743:                         const size = parseFloat(fontSizeStr);
3744:                         child.dataset.origFontSize = size;
3745:                         textElements.push({ child, origSize: size });
3746:                     }
3747:                 });
3748:             };
3749:             collectTextElements();
3750: 
3751:             // Set initial width
3752:             const initialWidth = el.offsetWidth || parseFloat(window.getComputedStyle(el).width) || 250;
3753:             el.dataset.initialWidth = initialWidth;
3754: 
3755:             // Dynamically add resize handle in bottom-right corner
3756:             if (!el.querySelector('.panel-resize-handle')) {
3757:                 const resizeHandle = document.createElement('div');
3758:                 resizeHandle.className = 'panel-resize-handle';
3759:                 resizeHandle.style.cssText = 'position: absolute; right: 0; bottom: 0; width: 14px; height: 14px; cursor: se-resize; z-index: 10010; background: linear-gradient(135deg, transparent 50%, #94a3b8 50%); border-bottom-right-radius: 12px; user-select: none;';
3760:                 el.appendChild(resizeHandle);
3761:                 
3762:                 resizeHandle.addEventListener('mousedown', function (e) {
3763:                     isResizing = true;
3764:                     startX = e.clientX;
3765:                     startY = e.clientY;
3766:                     startWidth = el.offsetWidth;
3767:                     startHeight = el.offsetHeight;
3768:                     
3769:                     // Re-collect text elements just in case dynamic content was added
3770:                     collectTextElements();
3771: 
3772:                     document.addEventListener('mousemove', onMouseMoveResize);
3773:                     document.addEventListener('mouseup', onMouseUpResize);
3774:                     e.preventDefault();
3775:                     e.stopPropagation();
3776:                 });
3777:             }
3778: 
3779:             handle.onmousedown = dragMouseDown;
3780: 
3781:             function dragMouseDown(e) {
3782:                 e = e || window.event;
3783:                 // Avoid dragging when clicking form controls or tabs
3784:                 if (['INPUT', 'BUTTON', 'SELECT', 'SPAN', 'LABEL', 'I'].includes(e.target.tagName) || e.target.closest('.switch') || e.target.closest('.flow-tab-btn')) {
3785:                     return;
3786:                 }
3787:                 if (e.target.closest('.panel-resize-handle')) {
3788:                     return;
3789:                 }
3790:                 
3791:                 e.preventDefault();
3792:                 
3793:                 const rect = el.getBoundingClientRect();
3794:                 // Clear transform translation if active to avoid jumping
3795:                 if (el.style.transform && el.style.transform !== 'none') {
3796:                     el.style.transform = 'none';
3797:                     el.style.left = rect.left + 'px';
3798:                     el.style.top = rect.top + 'px';
3799:                     el.style.bottom = 'auto';
3800:                     el.style.right = 'auto';
3801:                 }
3802:                 
3803:                 pos3 = e.clientX;
3804:                 pos4 = e.clientY;
3805:                 document.onmouseup = closeDragElement;
3806:                 document.onmousemove = elementDrag;
3807:             }
3808: 
3809:             function elementDrag(e) {
3810:                 if (isResizing) return;
3811:                 e = e || window.event;
3812:                 e.preventDefault();
3813:                 pos1 = pos3 - e.clientX;
3814:                 pos2 = pos4 - e.clientY;
3815:                 pos3 = e.clientX;
3816:                 pos4 = e.clientY;
3817:                 
3818:                 el.style.top = (el.offsetTop - pos2) + "px";
3819:                 el.style.left = (el.offsetLeft - pos1) + "px";
3820:                 el.style.bottom = 'auto';
3821:                 el.style.right = 'auto';
3822:             }
3823: 
3824:             function closeDragElement() {
3825:                 document.onmouseup = null;
3826:                 document.onmousemove = null;
3827:             }
3828: 
3829:             function onMouseMoveResize(e) {
3830:                 if (!isResizing) return;
3831:                 const dx = e.clientX - startX;
3832:                 const dy = e.clientY - startY;
3833:                 
3834:                 const newWidth = Math.max(150, startWidth + dx);
3835:                 const newHeight = Math.max(100, startHeight + dy);
3836:                 
3837:                 el.style.width = newWidth + 'px';
3838:                 el.style.height = newHeight + 'px';
3839: 
3840:                 // Scale font sizes
3841:                 const ratio = newWidth / initialWidth;
3842:                 textElements.forEach(item => {
3843:                     const clampedRatio = Math.max(0.65, Math.min(2.0, ratio));
3844:                     item.child.style.fontSize = (item.origSize * clampedRatio) + 'px';
