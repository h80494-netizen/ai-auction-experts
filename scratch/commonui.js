﻿//ui작업

$(document).ready(function() {
	sideLayer();

	$(document).on('input', '.range_slider_input_left', function() {
		var min = parseFloat($(this).attr('min'));
		var max = parseFloat($(this).attr('max'));

		var now_val = Math.min(parseFloat($(this).val()), parseFloat($(this).parent().find('.range_slider_input_right').val()) - parseFloat($(this).attr('step')));

		$(this).val(now_val);

		var percent = ((now_val - min) / (max - min)) * 100;
		$(this).parent().find('.thumb.left').css('left', percent + '%').addClass('active');
		$(this).parent().find('.range').css('left', percent + '%');
	});

	$(document).on('input', '.range_slider_input_right', function() {
		var min = parseFloat($(this).attr('min'));
		var max = parseFloat($(this).attr('max'));

		var now_val = Math.max(parseFloat($(this).val()), parseFloat($(this).parent().find('.range_slider_input_left').val()) + parseFloat($(this).attr('step')));

		$(this).val(now_val);

		var percent = ((now_val - min) / (max - min)) * 100;
		$(this).parent().find('.thumb.right').css('right', (100 - percent) + '%').addClass('active');
		$(this).parent().find('.range').css('right', (100 - percent) + '%');
	});

	$(document).on('input', '.range_slider_input_left', function() {
		$(this).parent().find('.thumb.left').removeClass('active');
	});

	$(document).on('input', '.range_slider_input_right', function() {
		$(this).parent().find('.thumb.right').removeClass('active');
	});

	setTimeout(function() {
		$('.range_slider_input_left').trigger('input');
		$('.range_slider_input_right').trigger('input');
		$('.range_slider_input_left').trigger('change');
		$('.range_slider_input_right').trigger('change');
	}, 100);

	$(document).on('click', '.map_button_list .map-button', function(e) {
		if (!$(e.target).hasClass('map-button-extra')) {
			if (!$(e.target).parents().hasClass('map-button-extra')) {
				if ($(this).hasClass('active')) {
					$(this).removeClass('active');
				} else {
					$(this).parent().find('.map-button').removeClass('active');
					$(this).addClass('active');
				}
			}
		}
	});

	$(document).on('click', '.tab-wrap .tab_menu', function() {
		$(this).parent().find('.tab_menu').removeClass('tabselected');
		$(this).addClass('tabselected');

		var index = $(this).parent().find('.tab_menu').index(this);
		$(this).parent().parent().find('.tabcontent').hide();
		$(this).parent().parent().find('.tabcontent-wrap .tabcontent').eq(index).show();
	});

	$(document).on('click', '.round-tab-wrap .tab_menu', function() {
		$(this).parent().find('.tab_menu').removeClass('tabselected');
		$(this).addClass('tabselected');

		var index = $(this).parent().find('.tab_menu').index(this);
		$(this).parent().parent().find('.round-tab-cont').hide();
		$(this).parent().parent().find('.round-tab-cont-wrap .round-tab-cont').eq(index).show();
	});

	$(document).on('click', '.category-tab-wrap .tab_menu', function() {
		$(this).parent().find('.tab_menu').removeClass('tabselected');
		$(this).addClass('tabselected');

		var index = $(this).parent().find('.tab_menu').index(this);
		$(this).parent().parent().find('.category-tab-cont').hide();
		$(this).parent().parent().find('.category-tab-cont-wrap .category-tab-cont').eq(index).show();
	});

	$(document).on('click', '.induL-wrap > div', function() {
		$(this).siblings().removeClass('selected');
		$(this).addClass('selected');
	});

	$(document).on('click', '.induM-wrap > div > div', function() {
		$(this).siblings().removeClass('selected');
		$(this).addClass('selected');
	});

	/* 화면 분할 버튼 */
	$(document).on('click', '.mapSectionBtn', function() {
		var section = $(this).attr('data-section');
		var $mapWrap = $(this).parents('.map-wrap');

		$(this).parent().find('.mapSectionBtn').removeClass('now');
		$(this).addClass('now');

		$(this).parents('.map-button').removeClass('active');

		$mapWrap.alterClass('map-section-*', 'map-section-' + section);

		// 현재 지도 분할이 새로운 지도 분할보다 많을 때
		if ($mapWrap.find('.map-area').length > section) {
			while ($mapWrap.find('.map-area').length > section) {
				$mapWrap.find('.map-area:last').remove();
			}

			// 현재 지도 분할이 새로운 지도 분할보다 적을 때
		} else if ($mapWrap.find('.map-area').length < section) {
			while ($mapWrap.find('.map-area').length < section) {
				$mapWrap.find('.map-area:last').after('<div class="map-area" style="background:url(../../../images/map/map.png) no-repeat center; background-size: cover;"></div>');
			}
		}
	});

	// 3D 레이어 보이기
	$(document).on('click', '.clsBtn3DMap', function() {
		if ($('.layout-3d-wrap').length > 0) $('.layout-3d-wrap').show();
	});
});

// 3D 레이어 숨기기
function closeWrap(obj) {
	$(obj).parents('.wrap').hide();
}

// 체크박스 최대 개수 체크
function checkboxLimitCheck(obj, count) {
	if ($(obj).parents('.checkbox-group').find('input[type=checkbox]:checked').length > count) {
		alert('최대 ' + count + '개까지 선택 가능합니다.');
		$(obj).prop('checked', false);
	}
}

// mobile layer

var timer = null;

$(window).resize(function() {
	clearTimeout(timer);
	timer = setTimeout(sideLayer);
});

function sideLayer() {
	if ($(window).width() < 1500) {
		sideHide();
		reportRhide();
	} else {
		sideShow();
		$('.service_login_menu, .store_cate_list').animate({ opacity: '1' }, 200);
	}
}

window.addEventListener('resize', function() {
	clearTimeout(timer);
	timer = setTimeout(sideLayer);
}, false);


//side content show/hide
$(document).ready(function() {
	$(document).on('click', '#btnlefthandle', function() {
		var sidePosition = $('.side-wrap').css('left').replace('px', '');
		if ($(window).width() < 900) {
			if (sidePosition < 0) {
				$('.service_login_menu, .store_cate_list').css('opacity', '0');
			} else {
				$('.service_login_menu, .store_cate_list').delay(100).animate({ opacity: '1' }, 200);
			}

			if ($(this).parent('.side-wrap').hasClass('active')) {
				$('.report_right_layer').removeClass('active');
				$('.report_right_layer').addClass('noactive');
			}

			if ($('.report_right_layer').hasClass('active')) {
				reportRhide();
			}
		}

		if ($(this).parent('.side-wrap').hasClass('noactive')) {
			sideShow();
		} else {
			sideHide();
		}

	});
});

function sideShow() {
	$('.side-wrap').addClass('active');
	$('.side-wrap').removeClass('noactive');

	//report 위치 변경(2022 03 15)
	var r = $('.report-wrap , .tripreport-wrap');
	$(r).css('left', '365px');
	$(r).css('width', 'calc(100% - 385px)');
}
function sideHide() {
	$('.side-wrap').removeClass('active');
	$('.side-wrap').addClass('noactive');

	//report 위치 변경
	var r = $('.report-wrap, .tripreport-wrap');
	$(r).css('left', '100px');
	$(r).css('width', 'calc(100% - 120px)');
}


//map side content show/hide
var MapSideUI = {
	event: function(nid, func) {	//side content
		var that = this;
		$(nid).click(function() {
			var r = $(this).parent().css('right');
			r = r.replace('px', '');


			if (r < 0) {
				that.show(this, func);
			}
			else {
				that.hide(this, func);
			}
		});
	},
	show: function(nid, func) {
		$(nid).parent().stop().animate({
			right: '0px'
		}, {
			duration: 300,
			complete: function() {
				$(nid).css('background', 'url(../images/map/ic_map_slide_button.png)');
				$(nid).css('background-position', 'left');

				if (func != undefined) {
					Doc[func](true);
				}
			}
		});
	},
	hide: function(nid, func) {
		$(nid).parent().stop().animate({
			right: '-184px'
		}, {
			duration: 300,
			complete: function() {
				$(nid).css('background', 'url(../images/map/ic_map_slide_button.png)');
				$(nid).css('background-position', 'left');

				if (func != undefined) {
					Doc[func](false);
				}
			}
		});
	},
	buttonshow: function(nid) {
		$(nid).css('display', 'block');
	},
	buttonhide: function(nid) {
		$(nid).css('display', 'none');
	}
}

//left submenu show /hide
var SubmenuUI = {
	event: function(nid) {	//submenu
		// 서브 메뉴 마우스 오버
		$(document).on('mouseenter', nid + " > ul > li ", function() {
			if ($(this).hasClass('logo'))
				return;

			var isselected = $(this).hasClass('selected');

			if (!isselected) {
				var src = $(this).children('div').children('img').attr('src');
				src = Util.replaceAt(src, src.length - 5, '');

				$(this).children('div').children('img').attr('src', src);
			}
			$(this).children('ul').fadeIn();
		});

		// 서브 메뉴 마우스 아웃
		$(document).on('mouseleave', nid + " > ul > li ", function() {
			if ($(this).hasClass('logo'))
				return;

			var isselected = $(this).hasClass('selected');

			if (!isselected) {
				var src = $(this).children('div').children('img').attr('src');
				src = Util.replaceAt(src, src.length - 5, '');
				$(this).children('div').children('img').attr('src', src);
			}

			$(this).children('ul').fadeOut();
		});
	}
}

//report show / hide
class ReportSingleUI {
	constructor() {

	}
	event(nid, maxh, minh) {
		this.nid = nid;
		this.maxh = maxh;
		this.minh = minh;
		this.drag = false;

		var that = this;
		$(this.nid).mousedown(function(e) { return that.mousedown(e); });
	}
	mousedown(e) {
		e.preventDefault();

		this.drag = true;
		var h = $(this.nid).parent().css('height');
		this.height = h.replace('px', '');
		this.pageY = e.pageY;

		var that = this;
		$(document).mouseup(function(e) { return that.mouseup(e); });
		$(document).mousemove(function(e) { return that.mousemove(e); });
	}
	mouseup(e) {
		e.preventDefault();

		this.drag = false;

		$(document).unbind('mousemove');
		$(document).unbind('mouseup');
	}
	mousemove(e) {
		e.stopPropagation();

		if (!this.drag)
			return;

		var y = e.pageY - this.pageY;

		var h = parseInt(this.height) - y;
		if (h < this.minh) {
			h = this.minh;
		}
		else if (h > $(window).height() * this.maxh) {
			h = $(window).height() * this.maxh;
		}

		if (h <= this.minh) {
			$('.report-show-button i').removeClass('xi-angle-down');
			$('.report-show-button i').addClass('xi-angle-up');
			$('.rightmenu_open').removeClass('deactive');
		} else {
			$('.report-show-button i').removeClass('xi-angle-up');
			$('.report-show-button i').addClass('xi-angle-down');
			$('.rightmenu_open').addClass('deactive');
		}

		$(this.nid).parent().css('height', h + 'px');
	}
	display(show) {
		if (show) {
			$(this.nid).parent().css('display', 'block');
		}
		else {
			$(this.nid).parent().fadeOut();
		}
	}
	hide() {
		var h = $(this.nid).parent().height();

		if (h > this.minh) {
			h = this.minh;
		}
		else {
			h = this.maxh;
		}

		$(this.nid).parent().stop().animate({
			height: h
		}, {
			duration: 300,
			complete: function() {

			}
		});
	}
	fold(show) {
		var h = this.minh;
		if (show)
			h = this.maxh;


		$(this.nid).parent().stop().animate({
			height: h
		}, {
			duration: 300,
			complete: function() {

			}
		});
	}
}

var ReportUI = {
	constructor() {

	},
	event: function(nid, maxh, minh) {
		this.nid = nid;
		this.maxh = maxh;
		this.minh = minh;
		this.drag = false;

		var that = this;
		$(this.nid).mousedown(function(e) { return that.mousedown(e); });
	},
	mousedown: function(e) {
		e.preventDefault();

		this.drag = true;
		var h = $(this.nid).parent().css('height');
		this.height = h.replace('px', '');
		this.pageY = e.pageY;

		var that = this;
		$(document).mouseup(function(e) { return that.mouseup(e); });
		$(document).mousemove(function(e) { return that.mousemove(e); });
	},
	mouseup: function(e) {
		e.preventDefault();

		this.drag = false;

		$(document).unbind('mousemove');
		$(document).unbind('mouseup');
	},
	mousemove: function(e) {
		e.stopPropagation();

		if (!this.drag)
			return;

		var y = e.pageY - this.pageY;

		var h = parseInt(this.height) - y;
		if (h < this.minh) {
			h = this.minh;
		}
		else if (h > $(window).height() * this.maxh) {
			h = $(window).height() * this.maxh;
		}

		if (h <= this.minh) {
			$('.report-show-button i').removeClass('xi-angle-down');
			$('.report-show-button i').addClass('xi-angle-up');
			$('.rightmenu_open').removeClass('deactive');
		} else {
			$('.report-show-button i').removeClass('xi-angle-up');
			$('.report-show-button i').addClass('xi-angle-down');
			$('.rightmenu_open').addClass('deactive');
		}

		$(this.nid).parent().css('height', h + 'px');
	},
	display: function(show) {
		if (show) {
			$(this.nid).parent().css('display', 'block');
			//$(this.nid).parent().fadeIn();
		}
		else {
			$(this.nid).parent().fadeOut();
		}
	},
	isdisplay: function() {
		var display = $(this.nid).parent().css('display');

		return display == 'block' ? true : false;
	},
	hide: function() {
		var h = $(this.nid).parent().height();

		if (h > this.minh) {
			h = this.minh;
			$('.report-show-button i').removeClass('xi-angle-down');
			$('.report-show-button i').addClass('xi-angle-up');
			$('.rightmenu_open').removeClass('deactive');
		}
		else {
			h = $(window).height() * this.maxh;
			$('.report-show-button i').removeClass('xi-angle-up');
			$('.report-show-button i').addClass('xi-angle-down');
			$('.rightmenu_open').addClass('deactive');
		}

		$(this.nid).parent().stop().animate({
			height: h
		}, {
			duration: 300,
			complete: function() {

			}
		});
	},
	fold: function(show) {
		var h = this.minh;
		if (show)
			h = this.maxh;

		$(this.nid).parent().stop().animate({
			height: h
		}, {
			duration: 300,
			complete: function() {

			}
		});
	},
	tabselected: function(nid, tabid, contentid, result) {	//select report tab
		var tabs = $(tabid).children('div');
		var content = $(contentid).children('div');

		var idx = 0;

		for (var n = 0; n < tabs.length; n++) {
			$(tabs[n]).removeClass('tabselected');
			$(content[n]).css('display', 'none');

			if (tabs[n] == nid) {
				idx = n;
			}
		}

		$(tabs[idx]).addClass('tabselected');
		$(content[idx]).fadeIn();

		if (result != undefined)
			Doc[result](nid, tabid, contentid);
	},
	tabinsert: function(tabcount, tabid, contentid, tabhtml, contenthtml) {
		var tabs = $(tabid).children('div');
		var content = $(contentid).children('div');

		if (tabs.length >= tabcount) {
			//더이상 추가 안됨
			return false;
		}

		$(tabid).append(tabhtml);
		$(contentid).append(contenthtml);

		var idx = tabs.length;

		tabs = $(tabid).children('div');
		content = $(contentid).children('div');

		//추가된 tab select..
		for (var n = 0; n < tabs.length; n++) {
			$(tabs[n]).removeClass('tabselected');
			$(content[n]).css('display', 'none');

			//line 그리기 위한 작업..
			$(tabs[n]).children('div.report-white-line').removeClass('first last');

			if (n == 0) {
				$(tabs[n]).children('div.report-white-line').addClass('first');
			}
			else if (n == 2) {
				$(tabs[n]).children('div.report-white-line').addClass('last');
			}
		}

		$(tabs[idx]).addClass('tabselected');
		$(content[idx]).fadeIn();
		return true;
	},
	tabclose: function(nid, tabid, contentid) {
		var tabs = $(tabid).children('div');
		var content = $(contentid).children('div');

		var idx = $(nid).parent().index();

		for (var n = 0; n < tabs.length; n++) {
			$(tabs[n]).removeClass('tabselected');
			$(content[n]).css('display', 'none');
		}

		$(tabs[idx]).remove();
		$(content[idx]).remove();

		tabs = $(tabid).children('div');
		content = $(contentid).children('div');

		//추가된 tab select..
		for (var n = 0; n < tabs.length; n++) {
			$(tabs[n]).removeClass('tabselected');
			$(content[n]).css('display', 'none');

			//line 그리기 위한 작업..
			$(tabs[n]).children('div.report-white-line').removeClass('first last');

			if (n == 0) {
				$(tabs[n]).children('div.report-white-line').addClass('first');
			}
			else if (n == 2) {
				$(tabs[n]).children('div.report-white-line').addClass('last');
			}
		}

		if (idx > 0) {
			idx--;
		}
		else {
			idx = 0;
		}

		$(tabs[idx]).addClass('tabselected');
		$(content[idx]).fadeIn();

		$('.report-tab-wrap').alterClass('report-tab-count-*', 'report-tab-count-' + tabs.length);

		return tabs.length;
	},
	tabcount: function(tabid) {
		var tabs = $(tabid).children('div');
		return tabs.length;
	}
}

//report right show / hide
var RightReportUI = {
	tabselected: function(nid, tabid, contentid) {	//select report tab
		var tabs = $(tabid).children('div');
		var content = $(contentid).children('div');

		var idx = 0;

		for (var n = 0; n < tabs.length; n++) {
			$(tabs[n]).removeClass('tabselected');
			$(content[n]).css('display', 'none');

			if (tabs[n] == nid) {
				idx = n;
			}
		}

		$(tabs[idx]).addClass('tabselected');
		$(content[idx]).fadeIn();
	},
	show: function() {
		$('.map-wrap .rightmenu_open').addClass('deactive');
		$('.report_right_layer').addClass('active');
		$('.report_right_layer').removeClass('noactive');
	},
	hide: function() {
		$('.map-wrap .rightmenu_open').removeClass('deactive');
		$('.report_right_layer').removeClass('active');
		$('.report_right_layer').addClass('noactive');
	}
}

$(document).ready(function() {
	$(document).on('click', '.report-right-show-button', function() {
		if ($(this).parents('.report_right_layer').hasClass('noactive')) {
			reportRshow();
		} else {
			reportRhide();
		}

		if ($(window).width() < 900) {
			if ($(this).parents('.report_right_layer').hasClass('active')) {
				$('.side-wrap').removeClass('active');
				$('.side-wrap').addClass('noactive');
				$('.service_login_menu, .store_cate_list').delay(200).animate({ opacity: '1' }, 200);
			}
		}
	});


	$(document).on('click', '.map-wrap .rightmenu_open', function() {
		/* deactive 상태가 아닐 때만 메뉴 리스트 토글 되도록 설정 */
		if (!$(this).hasClass('deactive')) {
			$(this).next('.map_button_list').slideToggle();
		}
	});

	$(document).on('click', '.report-right-show-button', function() {
		var reportPosition = $(this).parents('.report_right_layer').css('right').replace('px', '');
		if (reportPosition < 0) {
			$('.map-wrap .map_button_list').css('display', 'none');
		} else {
			$('.map-wrap .map_button_list').delay(200).slideDown();
		}
	});


});

function reportRshow() {
	$('.map-wrap .rightmenu_open').addClass('deactive');
	$('.report_right_layer').addClass('active');
	$('.report_right_layer').removeClass('noactive');
}
function reportRhide() {
	$('.map-wrap .rightmenu_open').removeClass('deactive');
	$('.report_right_layer').removeClass('active');
	$('.report_right_layer').addClass('noactive');
}

var Loader = {
	show: function() {
		$('.loadlayer').css('display', 'block');
	},
	hide: function() {
		$('.loadlayer').css('display', 'none');
	},
}

$.fn.alterClass = function(removals, additions) {
	var self = this;

	if (removals.indexOf('*') === -1) {
		// Use native jQuery methods if there is no wildcard matching
		self.removeClass(removals);
		return !additions ? self : self.addClass(additions);
	}

	var patt = new RegExp('\\s' +
		removals.
			replace(/\*/g, '[A-Za-z0-9-_]+').
			split(' ').
			join('\\s|\\s') +
		'\\s', 'g');

	self.each(function(i, it) {
		var cn = ' ' + it.className + ' ';
		while (patt.test(cn)) {
			cn = cn.replace(patt, ' ');
		}
		it.className = $.trim(cn);
	});

	return !additions ? self : self.addClass(additions);
};

var layout3d = {
	show: function() {

	},
	hide: function() {
		$('#wrap').css('display', 'block');
		$('#layout3d').empty();
		$('#layout3d').css('display', 'none');
	},
	load: function(url) {

		$('#wrap').css('display', 'none');
		$('#layout3d').empty();
		$('#layout3d').css('display', 'block');
		$('#layout3d').load(url);

	},
}

var leftMenuUI = {
	setMenu: function(roleCd, index, authCd) {
		// index: 예상손익=0, 창업온도=1, 경기상권=2, 내점포=3, 노후=4, 경기영향=5
		//		일반시민
		//		ROLE_BIZ	사업자
		//		ROLE_READY	예비창업자(경기도민)
		//		ROLE_SELF	자영업자(경기도민)
		//
		//		정책사용자
		//		ROLE_CONS	컨설턴트
		//		ROLE_LOCAL	지자체
		//		ROLE_GGGO	경기도-경제실-소상공인과
		//
		//		관리자
		//		ROLE_GBSA	경기도시장상권진흥원

		//		POLICY_SS		노후상가거리거리
		// ->   노후상가거리는 시민 X , 정책만 O
		//		POLICY_SL		영세자영업
		//		POLICY_PY		지역화폐		
		//		POLICY_RS		리서치			
		//		POLICY_BD		빅데이터	

		//		AFFC_LC			지자체(현황판, 기존점포분석, 신규점포분석)
		//		AFFC_BZ			사업자(신규점포분석)		

		var menuHtml = "";
		var subliHtml = "";

		if (
			roleCd.indexOf("ROLE_BIZ") > -1
			|| roleCd.indexOf("ROLE_READY") > -1
			|| roleCd.indexOf("ROLE_SELF") > -1
			//정책사용자,관리자 임시로 일반시민용으로 보이게 
			//			||roleCd.indexOf("ROLE_CONS") > -1
			//			||roleCd.indexOf("ROLE_LOCAL") > -1
			//			||roleCd.indexOf("ROLE_GGGO") > -1
			//			||roleCd.indexOf("ROLE_GBSA") > -1
		) {
			//SubmenuUI.event 에서 마우스 오버/아웃에 따라 이벤트 부여함
			//일반시민
			menuHtml += '<ul class="top_menu">';

			menuHtml += '	<li class="logo ' + ((index == 3) ? 'selectedtop' : '') + '">';
			menuHtml += '		<div onclick="location.href=\'../../main.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm1.png">';
			menuHtml += '			<div onclick="location.href=\'../../main.do\'">처음으로</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 3) ? 'selected' : ((index == 2) ? 'selectedtop' : '')) + '">';
			menuHtml += '		<div onclick="location.href=\'myStore.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm5' + ((index == 3) ? '-on' : '') + '.png">';
			menuHtml += '			<div>내 점포<br>분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 3) ? 'selectedbottom' : ((index == 2) ? 'selected' : ((index == 0) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'trdArea.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm4' + ((index == 2) ? '-on' : '') + '.png">';
			menuHtml += '			<div>경기상권<br>분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';


			menuHtml += '	<li class="' + ((index == 2) ? 'selectedbottom' : ((index == 0) ? 'selected' : ((index == 1) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'myConsult.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm2' + ((index == 0) ? '-on' : '') + '.png">';
			menuHtml += '			<div>예상<br>손익분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';


			menuHtml += '	<li class="' + ((index == 0) ? 'selectedbottom' : ((index == 1) ? 'selected' : ((index == 4) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'startTemp.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm3' + ((index == 1) ? '-on' : '') + '.png">';
			menuHtml += '			<div>창업 온도</div>';
			menuHtml += '		</div>';
			menuHtml += '		<ul class="submenu">';
			menuHtml += '			<li onclick="location.href=\'startTemp.do\'"><a>창업 온도</a></li>';
			menuHtml += '			<li onclick="location.href=\'trdActivity.do\'"><a>상권 활성화 지수</a></li>';
			menuHtml += '			<li onclick="location.href=\'tripActivity.do\'"><a>관광 활성화 지수</a></li>';
			menuHtml += '			<li onclick="location.href=\'trdOpen.do\'"><a>개폐업 지수</a></li>';
			//menuHtml += '			<li onclick="location.href=\'trdWorker.do\'">주거직장인구 지수</li>';
			menuHtml += '			<li onclick="location.href=\'trdChange.do\'"><a>상권 변화 시각화</a></li>';
			menuHtml += '		</ul>';
			menuHtml += '	</li>';


			if (authCd.indexOf("AFFC") > -1) {
				menuHtml += '	<li class="' + ((index == 1) ? 'selectedbottom' : ((index == 5) ? 'selected' : '')) + '">';
				menuHtml += '		<div onclick="location.href=\'storeReport.do\'">';
				menuHtml += '			<img src="../../../images/map/ico-lm7' + ((index == 5) ? '-on' : '') + '.png">';
				menuHtml += '			<div>경기상권<br>영향평가</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';
			}
			menuHtml += '</ul>';
			menuHtml += '<ul class="bottom_menu">';
			// 리서치
			if (authCd.indexOf("POLICY_RS") > -1) {/*
				menuHtml += '	<li>';
				menuHtml += '		<div onclick="location.href=\'../../listSurveyUser.do\'">';
				menuHtml += '			<img src="../../../images/map/ic_btn_research.png">';
				menuHtml += '			<div>리서치</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';*/
			}
			menuHtml += '	<li>';
			menuHtml += '		<div onclick="location.href=\'/help/getGuide.json\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm-help.png">';
			menuHtml += '			<div>도움말</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';
			menuHtml += '</ul>';

			subliHtml += '<a href="#" onclick="leftMenuUI.reqPrc()">서비스 신청</a>';
		} else if (roleCd.indexOf("ROLE_CONS") > -1
			|| roleCd.indexOf("ROLE_LOCAL") > -1
			|| roleCd.indexOf("ROLE_GGGO") > -1
		) {
			//정책사용자
			menuHtml += '<ul class="top_menu">';
			menuHtml += '	<li class="logo ' + ((index == 0) ? 'selectedtop' : '') + '">';
			menuHtml += '		<div onclick="location.href=\'../../main.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm1.png">';
			menuHtml += '			<div>처음으로</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 3) ? 'selected' : ((index == 2) ? 'selectedtop' : '')) + '">';
			menuHtml += '		<div onclick="location.href=\'myStore.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm5' + ((index == 3) ? '-on' : '') + '.png">';
			menuHtml += '			<div>내 점포<br>분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 3) ? 'selectedbottom' : ((index == 2) ? 'selected' : ((index == 0) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'trdArea.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm4' + ((index == 2) ? '-on' : '') + '.png">';
			menuHtml += '			<div>경기상권<br>분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 2) ? 'selectedbottom' : ((index == 0) ? 'selected' : ((index == 1) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'myConsult.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm2' + ((index == 0) ? '-on' : '') + '.png">';
			menuHtml += '			<div>예상<br>손익분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';


			menuHtml += '	<li class="' + ((index == 0) ? 'selectedbottom' : ((index == 1) ? 'selected' : ((index == 4) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'startTemp.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm3' + ((index == 1) ? '-on' : '') + '.png">';
			menuHtml += '			<div>창업 온도</div>';
			menuHtml += '		</div>';
			menuHtml += '		<ul class="submenu">';
			menuHtml += '			<li onclick="location.href=\'startTemp.do\'"><a>창업 온도</a></li>';
			menuHtml += '			<li onclick="location.href=\'trdActivity.do\'"><a>상권 활성화 지수</a></li>';
			menuHtml += '			<li onclick="location.href=\'tripActivity.do\'"><a>관광 활성화 지수</a></li>';
			menuHtml += '			<li onclick="location.href=\'trdOpen.do\'"><a>개폐업 지수</a></li>';
			//menuHtml += '			<li onclick="location.href=\'trdWorker.do\'">주거직장인구 지수</li>';
			menuHtml += '			<li onclick="location.href=\'trdChange.do\'"><a>상권 변화 시각화</a></li>';
			menuHtml += '		</ul>';
			menuHtml += '	</li>';

			// 노후상가거리
			//			if(1) {
			if (authCd.indexOf("POLICY_SS") > -1) {
				menuHtml += '	<li class="' + ((index == 3) ? 'selectedbottom' : ((index == 4) ? 'selected' : ((index == 5) ? 'selectedtop' : ''))) + '">';
				menuHtml += '		<div onclick="location.href=\'oldStore.do\'">';
				menuHtml += '			<img src="../../../images/map/ico-lm6' + ((index == 4) ? '-on' : '') + '.png">';
				menuHtml += '			<div>노후상가<br>거리</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';
			}

			//			if(1) {
			if (authCd.indexOf("AFFC") > -1) {
				menuHtml += '	<li class="' + ((index == 1) ? 'selectedbottom' : ((index == 5) ? 'selected' : '')) + '">';
				menuHtml += '		<div onclick="location.href=\'storeReport.do\'">';
				menuHtml += '			<img src="../../../images/map/ico-lm7' + ((index == 5) ? '-on' : '') + '.png">';
				menuHtml += '			<div>경기상권<br>영향평가</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';
			}
			menuHtml += '</ul>';
			menuHtml += '<ul class="bottom_menu">';
			// 리서치
			if (authCd.indexOf("POLICY_RS") > -1) {/*
				menuHtml += '	<li>';
				menuHtml += '		<div onclick="location.href=\'../../listSurveyUser.do\'">';
				menuHtml += '			<img src="../../../images/map/ic_btn_research.png">';
				menuHtml += '			<div>리서치</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';*/
			}
			menuHtml += '	<li>';
			menuHtml += '		<div onclick="location.href=\'/help/getGuide.json\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm-help.png">';
			menuHtml += '			<div>도움말</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';
			menuHtml += '</ul>';
		} else if (roleCd.indexOf("ROLE_GBSA") > -1
			|| roleCd.indexOf("ROLE_GMRA") > -1
		) {
			//관리자
			menuHtml += '<ul class="top_menu">';
			menuHtml += '	<li class="logo ' + ((index == 3) ? 'selectedtop' : '') + '">';
			menuHtml += '		<div onclick="location.href=\'../../main.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm1.png">';
			menuHtml += '			<div>처음으로</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 3) ? 'selected' : ((index == 2) ? 'selectedtop' : '')) + '">';
			menuHtml += '		<div onclick="location.href=\'myStore.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm5' + ((index == 3) ? '-on' : '') + '.png">';
			menuHtml += '			<div>내 점포<br>분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 3) ? 'selectedbottom' : ((index == 2) ? 'selected' : ((index == 0) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'trdArea.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm4' + ((index == 2) ? '-on' : '') + '.png">';
			menuHtml += '			<div>경기상권<br>분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';


			menuHtml += '	<li class="' + ((index == 2) ? 'selectedbottom' : ((index == 0) ? 'selected' : ((index == 1) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'myConsult.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm2' + ((index == 0) ? '-on' : '') + '.png">';
			menuHtml += '			<div>예상<br>손익분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';


			menuHtml += '	<li class="' + ((index == 0) ? 'selectedbottom' : ((index == 1) ? 'selected' : ((index == 4) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'startTemp.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm3' + ((index == 1) ? '-on' : '') + '.png">';
			menuHtml += '			<div>창업 온도</div>';
			menuHtml += '		</div>';
			menuHtml += '		<ul class="submenu">';
			menuHtml += '			<li onclick="location.href=\'startTemp.do\'"><a>창업 온도</a></li>';
			menuHtml += '			<li onclick="location.href=\'trdActivity.do\'"><a>상권 활성화 지수</a></li>';
			menuHtml += '			<li onclick="location.href=\'tripActivity.do\'"><a>관광 활성화 지수</a></li>';
			menuHtml += '			<li onclick="location.href=\'trdOpen.do\'"><a>개폐업 지수</a></li>';
			//menuHtml += '			<li onclick="location.href=\'trdWorker.do\'">주거직장인구 지수</li>';
			menuHtml += '			<li onclick="location.href=\'trdChange.do\'"><a>상권 변화 시각화</a></li>';
			menuHtml += '		</ul>';
			menuHtml += '	</li>';


			// 노후상가거리
			//			if(1) {
			if (authCd.indexOf("POLICY_SS") > -1) {
				menuHtml += '	<li class="' + ((index == 1) ? 'selectedbottom' : ((index == 4) ? 'selected' : ((index == 5) ? 'selectedtop' : ''))) + '">';
				menuHtml += '		<div onclick="location.href=\'oldStore.do\'">';
				menuHtml += '			<img src="../../../images/map/ico-lm6' + ((index == 4) ? '-on' : '') + '.png">';
				menuHtml += '			<div>노후상가<br>거리</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';
			}

			//			if(1) {
			if (authCd.indexOf("AFFC") > -1) {
				menuHtml += '	<li class="' + ((index == 4) ? 'selectedbottom' : ((index == 5) ? 'selected' : '')) + '">';
				menuHtml += '		<div onclick="location.href=\'storeReport.do\'">';
				menuHtml += '			<img src="../../../images/map/ico-lm7' + ((index == 5) ? '-on' : '') + '.png">';
				menuHtml += '			<div>경기상권<br>영향평가</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';
			}
			menuHtml += '</ul>';
			menuHtml += '<ul class="bottom_menu">';
			// 리서치
			if (authCd.indexOf("POLICY_RS") > -1) {/*
				menuHtml += '	<li>';
				menuHtml += '		<div onclick="location.href=\'../../listSurveyUser.do\'">';
				menuHtml += '			<img src="../../../images/map/ic_btn_research.png">';
				menuHtml += '			<div>리서치</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';*/
			}
			menuHtml += '	<li>';
			menuHtml += '		<div onclick="location.href=\'/help/getGuide.json\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm-help.png">';
			menuHtml += '			<div>도움말</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';
			menuHtml += '</ul>';

			if (roleCd.indexOf("ROLE_GMRA") > -1) {
				subliHtml += '<a href="#" onclick="location.href=\'/manage/confirmList.do\'">관리 페이지</a>';
			}

		} else {
			// Guest
			menuHtml += '<ul class="top_menu">';

			menuHtml += '	<li class="logo ' + ((index == 0) ? 'selectedtop' : '') + '">';
			menuHtml += '		<div onclick="location.href=\'../../main.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm1.png">';
			menuHtml += '			<div>처음으로</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 3) ? 'selected' : ((index == 2) ? 'selectedtop' : '')) + '">';
			menuHtml += '		<div onclick="location.href=\'myStore.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm5' + ((index == 3) ? '-on' : '') + '.png">';
			menuHtml += '			<div>내 점포<br>분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';

			menuHtml += '	<li class="' + ((index == 3) ? 'selectedbottom' : ((index == 2) ? 'selected' : ((index == 0) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'trdArea.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm4' + ((index == 2) ? '-on' : '') + '.png">';
			menuHtml += '			<div>경기상권<br>분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';


			menuHtml += '	<li class="' + ((index == 2) ? 'selectedbottom' : ((index == 0) ? 'selected' : ((index == 1) ? 'selectedtop' : ''))) + '">';
			menuHtml += '		<div onclick="location.href=\'myConsult.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm2' + ((index == 0) ? '-on' : '') + '.png">';
			menuHtml += '			<div>예상<br>손익분석</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';


			menuHtml += '	<li class="' + ((index == 0) ? 'selectedbottom' : ((index == 1) ? 'selected' : '')) + '">';
			menuHtml += '		<div onclick="location.href=\'startTemp.do\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm3' + ((index == 1) ? '-on' : '') + '.png">';
			menuHtml += '			<div>창업 온도</div>';
			menuHtml += '		</div>';
			menuHtml += '		<ul class="submenu">';
			menuHtml += '			<li onclick="location.href=\'startTemp.do\'"><a>창업 온도</a></li>';
			menuHtml += '			<li onclick="location.href=\'trdActivity.do\'"><a>상권 활성화 지수</a></li>';
			menuHtml += '			<li onclick="location.href=\'tripActivity.do\'"><a>관광 활성화 지수</a></li>';
			menuHtml += '			<li onclick="location.href=\'trdOpen.do\'"><a>개폐업 지수</a></li>';
			//menuHtml += '			<li onclick="location.href=\'trdWorker.do\'">주거직장인구 지수</li>';
			menuHtml += '			<li onclick="location.href=\'trdChange.do\'"><a>상권 변화 시각화</a></li>';
			menuHtml += '		</ul>';
			menuHtml += '	</li>';





			if (authCd.indexOf("AFFC") > -1) {
				menuHtml += '	<li class="' + ((index == 4) ? 'selectedbottom' : ((index == 5) ? 'selected' : '')) + '">';
				menuHtml += '		<div onclick="location.href=\'storeReport.do\'">';
				menuHtml += '			<img src="../../../images/map/ico-lm7' + ((index == 5) ? '-on' : '') + '.png">';
				menuHtml += '			<div>경기상권<br>영향평가</div>';
				menuHtml += '		</div>';
				menuHtml += '	</li>';
			}
			menuHtml += '</ul>';
			menuHtml += '<ul class="bottom_menu">';

			menuHtml += '	<li>';
			menuHtml += '		<div onclick="location.href=\'/help/getGuide.json\'">';
			menuHtml += '			<img src="../../../images/map/ico-lm-help.png">';
			menuHtml += '			<div>도움말</div>';
			menuHtml += '		</div>';
			menuHtml += '	</li>';
			menuHtml += '</ul>';

			subliHtml += '<a href="#" onclick="location.href=\'/passni/jsp/intergration/sso_init_url.jsp\'">회원가입</a>';
		}
		var menuDiv = $(".leftNav");
		menuDiv.empty();
		menuDiv.html(menuHtml);
		var subli = $("#userMenu > ul").children('li').eq(2);
		subli.empty();
		subli.html(subliHtml);
	},
	loginPopup: function(nid) {
		//alert($(nid));
		$(nid).fadeIn();
		//$(nid).hide();
	},
	login: function(div) {
		if (div == "guest") {
			location.href = "/user/guestCheck.do";
		} else if (div == "bigsale") {//통큰세일 추가
			location.href = "/user/guestInject.do";
		} else if (div == "member") {
			location.href = "/passni/jsp/intergration/sso_init_url.jsp";
		}
	},
	logOut: function() {
		location.href = "/user/logout.do";
	},
	join: function() {
		location.href = "/passni/jsp/intergration/sso_init_url.jsp";
	},
	reqPrc: function() {
		var param = {};
		$.ajax({
			url: '/main/requestPrc.json',
			method: 'post',
			data: param,
			success: function(response) {
				alert("[" + response.resultCd + "] " + response.resultMsg);
			},
			error: function(error) {
				alert("[" + response.resultCd + "] " + response.resultMsg + "\n 다시 시도해 주세요.");
			}
		});
	},
}
