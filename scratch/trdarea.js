//통신 작업
var Api = {
	services: {
		//행정구역
		get_sgList: {method: 'get_sgList', type: 'post', url: '../common/get_sgList.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		get_sgdList: {method: 'get_sgdList', type: 'post', url: '../common/get_sgList.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		//업종
		getUpjongList: {method: 'getUpjongList', type: 'post', url: '../common/getUpjongList.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		//기준분기
		get_stdr_qt: {method: 'get_stdr_qt', type: 'post', url: '../common/get_stdr_qt.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		storList: {method: 'storList', type: 'post', url: '../mapi/storList.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		maechul: {method: 'maechul', type: 'post', url: '../mapi/maechul.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		ingu: {method: 'ingu', type: 'post', url: '../mapi/ingu.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		region: {method: 'region', type: 'post', url: '../mapi/region.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		//검색
		getRnkTrdList: {method: 'getRnkTrdList', type: 'post', url: '../common/getRnkTrdList.json', 
			contentType: 'application/json; charset=UTF-8', dataType: 'json'},
			//contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		//분석
		get_anlTrd: {method: 'get_anlTrd', type: 'post', url: '../trd/get_anlTrd.json', 
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8', dataType: ''},
		//상권비교
		getTrdComp: {method: 'getTrdComp', type: 'post', url: '../mapi/getTrdComp.json', 
			contentType: 'application/json; charset=UTF-8', dataType: 'json'},
	},
	call : function(key, params, loading) {
//		if(key === 'getRnkTrdList') console.log("getRnkTrdList:::" + params)
		
		if(loading != undefined && loading) {
			Loader.show();
		}
		
		this.params = params;
		
		const service = this.services[key];
		
		//call api
		var api = new ApiService(this, service, params);
		if(key == 'address') {
			api.kakaosend();
		}
		else {
			api.send();	
		}
	},
	notify : function(result) {
		Loader.hide();
		
		if(result.status != '200') {
			//error 처리..
			
			return;
		}
		
		result.params = this.params;		
		View[result.service.method](result.data);
	}
}

//view handle
var View = {
	getTrdComp : function(data) {
		//상권비교 분석
		var content = $('#reportsinglecontent').find('.report-table-wrap');
		$(content).empty();
		
		for(var n=0; n<data.length; n++) {
			var d = data[n];
			
			var t = $('#singlereporttabletemp');
			var th = $(t).find('th');
			var td = $(t).find('td');
			
			th.html(d.trdarNm);
			
			var x=-1;
			var c = $('#induL').find('div.selected').attr('code');
			
			$(td[x+=2]).html(d.cdNm);							//상권유형
			$(td[x+=2]).html(d.trdArea);						//상권면적
			// 선택업종
			if(d.lfbtNm === null && c === '0'){
				$(td[x+=2]).html("전체업종");							
			}else if(d.lfbtNm === null && c === '1'){
				$(td[x+=2]).html("소매업전체");
			}else if(d.lfbtNm === null && c === '2'){
				$(td[x+=2]).html("서비스업전체");
			}else if(d.lfbtNm === null && c === '3'){
				$(td[x+=2]).html("외식업전체");
			}else{
				$(td[x+=2]).html(d.lfbtNm);							
			}
			$(td[x+=2]).html(d.opTmep);							//창업온도
			$(td[x+=2]).html(d.allOperStorCnt);					//점포수
			$(td[x+=2]).html(d.yr3SrvlRt);						//3년생존율
			$(td[x+=2]).html(d.rcntYr10TotStorCnt);				//평균영업기간
			$(td[x+=2]).html(Util.commaString(d.rdCnt));		//상존인구(길단위)
			$(td[x+=2]).html(Util.commaString(d.blCnt));		//상존인구(건물단위)
			$(td[x+=2]).html(Util.commaString(d.allRsdpplCnt));	//주거인구
			$(td[x+=2]).html(Util.commaString(d.totEmpCnt));	//직장인구
			$(td[x+=2]).html(Util.commaString(d.slsAmt));		//매출
			
			var div = $('<div class="report-table">');
			div.append(t.html());
			content.append(div);
		}
		
		// singlerepo open
		Func.openSingleRepo();
		
		//Doc.btnCompare(true);
	},
	get_stdr_qt : function(data) {
		
		var list = [];
		var year = null;
		
		for(var n=0; n<data.length; n++) {
			var d = data[n].stdrQt;
			
			var y = d.substr(0, 4);
			if(y != year) {
				year = y;
				
				var item = {};
				item.year = y;
				item.qu = [];
				item.qu.push(d.substr(5, 1));
				
				list.push(item);
				continue;
			}
			
			list[list.length-1].qu.push(d.substr(5, 1));
		}
		
		this._yearqt = list;
		
		//화면 출력
		$('#selectYear').empty();
		for(var idx = 0; idx < list.length; idx++){                
	 		var option = $("<option value="+list[idx].year+">"+list[idx].year+"년</option>");
	 		$('#selectYear').append(option);
		}
		
		//year change 이벤트
		$('#selectYear').change();
	},
	getRnkTrdList :function(data) {
		
		var c = $('#rtabcontents .tab-content-trd');
		c.empty();
		
		for(var n=0; n<data.length; n++) {
			var d = data[n];
			var div = '<div trdarId="'+d.trdarId+'" wprk="'+d.wprk+'">'+d.trdarNm+'</div>';
			if(d.trdarSeCd == '1') {
				$(c[0]).append(div);
				$(c[3]).append(div);
			}
			else if(d.trdarSeCd == '2') {
				$(c[1]).append(div);
				$(c[4]).append(div);
			}
			else {
				$(c[2]).append(div);
				$(c[5]).append(div);
			}
		}
		
		//검색 결과 건수 입력
		var te = $('#rtabcontents .text');
		
		var label = '발달상권 검색결과 <label>'+$(c[3]).children('div').length+'건</label>';
		if($(c[3]).children('div').length == 0) {
			label = '검색 결과가 존재하지 않습니다';
		}
		$(te[0]).html(label);
		$(te[3]).html(label);
		
		label = '골목상권 검색결과 <label>'+$(c[4]).children('div').length+'건</label>';
		if($(c[4]).children('div').length == 0) {
			label = '검색 결과가 존재하지 않습니다';
		}
		$(te[1]).html(label);
		$(te[4]).html(label);
		
		label = '전통시장 검색결과 <label>'+$(c[5]).children('div').length+'건</label>';
		if($(c[5]).children('div').length == 0) {
			label = '검색 결과가 존재하지 않습니다';
		}
		$(te[2]).html(label);
		$(te[5]).html(label);
		
		//select 활성화
		c.children('div').click(function() {
			Doc.btnTrdAddressSelect(this);
		});
	},
	get_anlTrd : function(data) {

		if(!ReportUI.isdisplay()) {
			ReportUI.display(true);
		}
			
		ReportUI.fold(true);
		
		this._data = data;

		//업종분석
		this.tab_1_1();
		this.tab_1_2();
		this.tab_1_3();
		this.tab_1_4();
	
		//매출분석
		this.tab_2_1();
		this.tab_2_2();

		//인구분석
		this.tab_3_1();
		this.tab_3_2();	
		this.tab_3_3();
		this.tab_3_4();
		this.tab_3_5();
		this.tab_3_6();
		this.tab_3_7();
		/*this.tab_3_8();*/
		
		//지역(배후)분석
		this.tab_4_1();
		this.tab_4_2();
		this.tab_4_3();
		this.tab_4_4();
		this.tab_4_5();
		
		//소비분석
		this.tab_5_1();
		this.tab_5_2();
		this.tab_5_3();
		this.tab_5_4();
		this.tab_5_5();
		this.tab_5_6();
		this.tab_5_7();
		this.tab_5_8();

		//table click event
		$('.link-span').click(function() { 
			Doc.btnTableSpan(this);
		});
		
		// open multirepo
		Func.openMultiRepo();
	},
	get_sgList : function(data) {
		$('#sglist').empty();

		for(var idx = 0; idx < data.length; idx++){                
	 		var option = $("<option value="+data[idx].sggcd+">"+data[idx].sggnm+"</option>");
	 		$('#sglist').append(option);
		}
		
		//change event
		$('#sglist').change();
	},
	get_sgdList : function(data) {
		$('#sgdlist').empty();

		for(var idx = 0; idx < data.length; idx++){                
	 		var option = $("<option value="+data[idx].dongCd+">"+data[idx].dongNm+"</option>");
	 		$('#sgdlist').append(option);
		}
	},
	getUpjongList : function(data) {
		/*$('#induM').empty();
		
		for(var idx=0; idx<data.length; idx++) {
			var item = data[idx];
			Func.insertInduM('#induM', item);	
		}*/
		
		$('#induM').empty();
		
		var c = $('#induL').find('div.selected').attr('code');
		
		var cl = {};
		cl.lfbtCd = 'S'+c;
		cl.lfbtNm = '전체업종';
		
		if(c == '1') {
			cl.lfbtNm = '소매업전체';
		}
		else if(c == '2') {
			cl.lfbtNm = '서비스업전체';
		}
		else if(c == '3') {
			cl.lfbtNm = '외식업전체';
		}
		
		Func.insertInduM('#induM', cl);
		
		for(var idx=0; idx<data.length; idx++) {
			var item = data[idx];
			Func.insertInduM('#induM', item);
		}
		
		// 경기상권분석 페이지 진입시 각 전체업종 디폴트로 선택
		$("#induM > div[code='S0']").addClass('selected');
		$("#induM > div[code='S1']").addClass('selected');
		$("#induM > div[code='S2']").addClass('selected');
		$("#induM > div[code='S3']").addClass('selected');
		
		//생활밀접업종 세부선택 이벤트 처리
		$('#induM > div').on('click', function () {
			//class 제거
			$(this).parent().children('div').removeClass('selected');
			$(this).addClass('selected');
		});
	},
	storList : function(data) {
		
	},
	maechul : function(data) {
		
	},
	ingu : function(data) {
		
	},
	region : function(data) {
		
	},
	tab_1_1 : function() {
		var div = $('.subtabcontent-wrap').eq(0).children('div').eq(0);
		Func.commonBaseDate(div, 1);
		
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.UpjongStorCnt;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotCnt.substr(0, 4)+'년 '+li[0].firstTotCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotCnt.substr(0, 4)+'년 '+li[0].secondTotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotCnt.substr(0, 4)+'년 '+li[0].thirdTotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstFrncCnt', 'firstGnrlCnt', 'firstTotCnt', 
			'secondFrncCnt', 'secondGnrlCnt', 'secondTotCnt', 
			'thirdFrncCnt', 'thirdGnrlCnt', 'thirdTotCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_1_1_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '프랜차이즈',
					data: [parseInt(item.firstFrncCnt), parseInt(item.secondFrncCnt), parseInt(item.thirdFrncCnt)]
				},
				{
					name: '일반점포',
					data: [parseInt(item.firstGnrlCnt), parseInt(item.secondGnrlCnt), parseInt(item.thirdGnrlCnt)]
				},
				{
					name: '점포수',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		const options = Func.chartCommonOption('chart_1_1_0');
		this._chart_1_1_0 = toastui.Chart.columnChart({ el, data, options });
		
	},
	tab_1_2 : function() {
		var div = $('.subtabcontent-wrap').eq(0).children('div').eq(1);
		Func.commonBaseDate(div, 2);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.UpjongStorCnt;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotCnt.substr(0, 4)+'년 '+li[0].firstTotCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotCnt.substr(0, 4)+'년 '+li[0].secondTotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotCnt.substr(0, 4)+'년 '+li[0].thirdTotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstOpbizCnt', 'firstClsbizCnt', 'firstOpbizRt', 'firstClsbizRt', 
			'secondOpbizCnt', 'secondClsbizCnt', 'secondOpbizRt', 'secondClsbizRt', 
			'thirdOpbizCnt', 'thirdClsbizCnt', 'thirdOpbizRt', 'thirdClsbizRt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_1_2_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '개업수',
					data: [parseInt(item.firstOpbizCnt), parseInt(item.secondOpbizCnt), parseInt(item.thirdOpbizCnt)]
				},
				{
					name: '폐업수',
					data: [parseInt(item.firstClsbizCnt), parseInt(item.secondClsbizCnt), parseInt(item.thirdClsbizCnt)]
				},
				{
					name: '개업률',
					data: [parseInt(item.firstOpbizRt), parseInt(item.secondOpbizRt), parseInt(item.thirdOpbizRt)]
				},
				{
					name: '폐업률',
					data: [parseInt(item.firstClsbizRt), parseInt(item.secondClsbizRt), parseInt(item.thirdClsbizRt)]
				},
 			],
		};
		
		const options = Func.chartCommonOption('chart_1_2_0');
		this._chart_1_2_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_1_3 : function() {
		var div = $('.subtabcontent-wrap').eq(0).children('div').eq(2);
		Func.commonBaseDate(div, 2);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.UpjongSrvlRt;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstYr1Rt.substr(0, 4)+'년 '+li[0].firstYr1Rt.substr(5, 1)+'분기';
		var second = li[0].secondYr1Rt.substr(0, 4)+'년 '+li[0].secondYr1Rt.substr(5, 1)+'분기';
		var third = li[0].thirdYr1Rt.substr(0, 4)+'년 '+li[0].thirdYr1Rt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstYr1Rt', 'firstYr3Rt', 'firstYr5Rt', 
			'secondYr1Rt', 'secondYr3Rt', 'secondYr5Rt', 
			'thirdYr1Rt', 'thirdYr3Rt', 'thirdYr5Rt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_1_3_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '1년생존율',
					data: [parseInt(item.firstYr1Rt), parseInt(item.secondYr1Rt), parseInt(item.thirdYr1Rt)]
				},
				{
					name: '3년생존율',
					data: [parseInt(item.firstYr3Rt), parseInt(item.secondYr3Rt), parseInt(item.thirdYr3Rt)]
				},
				{
					name: '5년생존율',
					data: [parseInt(item.firstYr5Rt), parseInt(item.secondYr5Rt), parseInt(item.thirdYr5Rt)]
				},
 			],
		};
		console.log(data);
		const options = Func.chartCommonOption('chart_1_3_0 ');
		this._chart_1_3_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_1_4 : function() {
		var div = $('.subtabcontent-wrap').eq(0).children('div').eq(3);
		Func.commonBaseDate(div, 4);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.UpjongAvgBsns;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstAvgBsns.substr(0, 4)+'년 '+li[0].firstAvgBsns.substr(5, 1)+'분기';
		var second = li[0].secondAvgBsns.substr(0, 4)+'년 '+li[0].secondAvgBsns.substr(5, 1)+'분기';
		var third = li[0].thirdAvgBsns.substr(0, 4)+'년 '+li[0].thirdAvgBsns.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstAvgBsns', 'secondAvgBsns', 'thirdAvgBsns'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_1_4_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '평균영업기간',
					data: [parseInt(item.firstAvgBsns), parseInt(item.secondAvgBsns), parseInt(item.thirdAvgBsns)]
				},
 			],
		};
		
		const options = Func.chartCommonOption('chart_1_4_0');
		this._chart_1_4_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_2_1 : function() {
		var div = $('.subtabcontent-wrap').eq(1).children('div').eq(0);
		Func.commonBaseDate(div, 4);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.MaechulQt;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstAmt.substr(0, 4)+'년 '+li[0].firstAmt.substr(5, 1)+'분기';
		var second = li[0].secondAmt.substr(0, 4)+'년 '+li[0].secondAmt.substr(5, 1)+'분기';
		var third = li[0].thirdAmt.substr(0, 4)+'년 '+li[0].thirdAmt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstAmt', 'secondAmt', 'thirdAmt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_2_1_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '매출액',
					data: [parseInt(item.firstAmt), parseInt(item.secondAmt), parseInt(item.thirdAmt)]
				},
 			],
		};
		
		const options = Func.chartCommonOption('chart_2_1_0');
		this._chart_2_1_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_2_2 : function() {
		var div = $('.subtabcontent-wrap').eq(1).children('div').eq(1);
		Func.commonBaseDate(div, 4);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.MaechulYr;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstAmt.substr(0, 4)+'년 '+li[0].firstAmt.substr(5, 1)+'분기';
		var second = li[0].secondAmt.substr(0, 4)+'년 '+li[0].secondAmt.substr(5, 1)+'분기';
		var third = li[0].thirdAmt.substr(0, 4)+'년 '+li[0].thirdAmt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstAmt', 'secondAmt', 'thirdAmt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_2_2_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '매출액',
					data: [parseInt(item.firstAmt), parseInt(item.secondAmt), parseInt(item.thirdAmt)]
				},
 			],
		};
		
		const options = Func.chartCommonOption('chart_2_2_0');
		this._chart_2_2_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_3_1 : function() {
		var div = $('.subtabcontent-wrap').eq(2).children('div').eq(0);
		Func.commonBaseDate(div, 66);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.RoadAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstRdTot.substr(0, 4)+'년 '+li[0].firstRdTot.substr(5, 1)+'분기';
		var second = li[0].secondRdTot.substr(0, 4)+'년 '+li[0].secondRdTot.substr(5, 1)+'분기';
		var third = li[0].thirdRdTot.substr(0, 4)+'년 '+li[0].thirdRdTot.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstRdMan', 'firstRdWmn', 'firstRdTot',
						'secondRdMan', 'secondRdWmn', 'secondRdTot',
						'thirdRdMan', 'thirdRdWmn', 'thirdRdTot'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_1_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstRdMan), parseInt(item.secondRdMan), parseInt(item.thirdRdMan)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstRdWmn), parseInt(item.secondRdWmn), parseInt(item.thirdRdWmn)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstRdTot), parseInt(item.secondRdTot), parseInt(item.thirdRdTot)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_3_1_0');
		this._chart_3_1_0 = toastui.Chart.columnChart({ el, data, options });

		//table 2
		table = div.find('table').eq(1);
		el = div.find('.graph-chart').eq(1).get(0);

		tbody = table.find('tbody');
		th = table.find('thead > tr:first > th');
		
		li = this._data.BldgAge;
		item = li[1];
		
		first = li[0].firstBlTot.substr(0, 4)+'년 '+li[0].firstBlTot.substr(5, 1)+'분기';
		second = li[0].secondBlTot.substr(0, 4)+'년 '+li[0].secondBlTot.substr(5, 1)+'분기';
		third = li[0].thirdBlTot.substr(0, 4)+'년 '+li[0].thirdBlTot.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		props = ['region', 'firstBlMan', 'firstBlWmn', 'firstBlTot',
						'secondBlMan', 'secondBlWmn', 'secondBlTot',
						'thirdBlMan', 'thirdBlWmn', 'thirdBlTot'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_1_1_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart 2
		data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstBlMan), parseInt(item.secondBlMan), parseInt(item.thirdBlMan)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstBlWmn), parseInt(item.secondBlWmn), parseInt(item.thirdBlWmn)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstBlTot), parseInt(item.secondBlTot), parseInt(item.thirdBlTot)]
				},
 			],
		};
		
		options = Func.chartCommonOption('chart_3_1_1');
		this._chart_3_1_1 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_3_2 : function() {
		var div = $('.subtabcontent-wrap').eq(2).children('div').eq(1);
		Func.commonBaseDate(div, 66);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.RoadAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstRdTot.substr(0, 4)+'년 '+li[0].firstRdTot.substr(5, 1)+'분기';
		var second = li[0].secondRdTot.substr(0, 4)+'년 '+li[0].secondRdTot.substr(5, 1)+'분기';
		var third = li[0].thirdRdTot.substr(0, 4)+'년 '+li[0].thirdRdTot.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstRd1020', 'firstRd3040', 'firstRd5060', 'firstRdTot',
						'secondRd1020', 'secondRd3040', 'secondRd5060', 'secondRdTot',
						'thirdRd1020', 'thirdRd3040', 'thirdRd5060', 'thirdRdTot'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_2_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '10~20대',
					data: [parseInt(item.firstRd1020), parseInt(item.secondRd1020), parseInt(item.thirdRd1020)]
				},
				{
					name: '30~40대',
					data: [parseInt(item.firstRd3040), parseInt(item.secondRd3040), parseInt(item.thirdRd3040)]
				},
				{
					name: '50~60대',
					data: [parseInt(item.firstRd5060), parseInt(item.secondRd5060), parseInt(item.thirdRd5060)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstRdTot), parseInt(item.secondRdTot), parseInt(item.thirdRdTot)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_3_2_0');
		this._chart_3_2_0 = toastui.Chart.columnChart({ el, data, options });
		
		
		//table 2
		table = div.find('table').eq(1);
		el = div.find('.graph-chart').eq(1).get(0);
		
		tbody = table.find('tbody');
		th = table.find('thead > tr:first > th');
		
		li = this._data.BldgAge;
		item = li[1];
		
		first = li[0].firstBlTot.substr(0, 4)+'년 '+li[0].firstBlTot.substr(5, 1)+'분기';
		second = li[0].secondBlTot.substr(0, 4)+'년 '+li[0].secondBlTot.substr(5, 1)+'분기';
		third = li[0].thirdBlTot.substr(0, 4)+'년 '+li[0].thirdBlTot.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstBl1020', 'firstBl3040', 'firstBl5060', 'firstBlTot',
						'secondBl1020', 'secondBl3040', 'secondBl5060', 'secondBlTot',
						'thirdBl1020', 'thirdBl3040', 'thirdBl5060', 'thirdBlTot'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_2_1_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart 2
		data = {
			categories: [first, second, third],
			series: [
				{
					name: '10~20대',
					data: [parseInt(item.firstBl1020), parseInt(item.secondBl1020), parseInt(item.thirdBl1020)]
				},
				{
					name: '30~40대',
					data: [parseInt(item.firstBl3040), parseInt(item.secondBl3040), parseInt(item.thirdBl3040)]
				},
				{
					name: '50~60대',
					data: [parseInt(item.firstBl5060), parseInt(item.secondBl5060), parseInt(item.thirdBl5060)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstBlTot), parseInt(item.secondBlTot), parseInt(item.thirdBlTot)]
				},
 			],
		};
		
		options = Func.chartCommonOption('chart_3_2_1');
		this._chart_3_2_1 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_3_3 : function() {
		var div = $('.subtabcontent-wrap').eq(2).children('div').eq(2);
		Func.commonBaseDate(div, 66);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.RoadTime;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstRdTot.substr(0, 4)+'년 '+li[0].firstRdTot.substr(5, 1)+'분기';
		var second = li[0].secondRdTot.substr(0, 4)+'년 '+li[0].secondRdTot.substr(5, 1)+'분기';
		var third = li[0].thirdRdTot.substr(0, 4)+'년 '+li[0].thirdRdTot.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstRdMrn', 'firstRdAft', 'firstRdEvn', 'firstRdTot',
						'secondRdMrn', 'secondRdAft', 'secondRdEvn', 'secondRdTot',
						'thirdRdMrn', 'thirdRdAft', 'thirdRdEvn', 'thirdRdTot'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_3_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '오전',
					data: [parseInt(item.firstRdMrn), parseInt(item.secondRdMrn), parseInt(item.thirdRdMrn)]
				},
				{
					name: '오후',
					data: [parseInt(item.firstRdAft), parseInt(item.secondRdAft), parseInt(item.thirdRdAft)]
				},
				{
					name: '저녁',
					data: [parseInt(item.firstRdEvn), parseInt(item.secondRdEvn), parseInt(item.thirdRdEvn)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstRdTot), parseInt(item.secondRdTot), parseInt(item.thirdRdTot)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_3_3_0');
		this._chart_3_3_0 = toastui.Chart.columnChart({ el, data, options });
		
		
		//table 2
		table = div.find('table').eq(1);
		el = div.find('.graph-chart').eq(1).get(0);
		
		tbody = table.find('tbody');
		th = table.find('thead > tr:first > th');
		
		li = this._data.BldgTime;
		item = li[1];
		
		first = li[0].firstBlTot.substr(0, 4)+'년 '+li[0].firstBlTot.substr(5, 1)+'분기';
		second = li[0].secondBlTot.substr(0, 4)+'년 '+li[0].secondBlTot.substr(5, 1)+'분기';
		third = li[0].thirdBlTot.substr(0, 4)+'년 '+li[0].thirdBlTot.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		props = ['region', 'firstBlMrn', 'firstBlAft', 'firstBlEvn', 'firstBlTot',
						'secondBlMrn', 'secondBlAft', 'secondBlEvn', 'secondBlTot',
						'thirdBlMrn', 'thirdBlAft', 'thirdBlEvn', 'thirdBlTot'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_3_1_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart 2
		data = {
			categories: [first, second, third],
			series: [
				{
					name: '오전',
					data: [parseInt(item.firstBlMrn), parseInt(item.secondBlMrn), parseInt(item.thirdBlMrn)]
				},
				{
					name: '오후',
					data: [parseInt(item.firstBlAft), parseInt(item.secondBlAft), parseInt(item.thirdBlAft)]
				},
				{
					name: '저녁',
					data: [parseInt(item.firstBlEvn), parseInt(item.secondBlEvn), parseInt(item.thirdBlEvn)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstBlTot), parseInt(item.secondBlTot), parseInt(item.thirdBlTot)]
				},
 			],
		};
		
		options = Func.chartCommonOption('chart_3_3_1');
		this._chart_3_3_1 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_3_4 : function() { // 요일별(길단위),  요일별(건물단위) 
		var div = $('.subtabcontent-wrap').eq(2).children('div').eq(3);
		Func.commonBaseDate(div, 66);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.RoadDay;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstRdTot.substr(0, 4)+'년 '+li[0].firstRdTot.substr(5, 1)+'분기';
		var second = li[0].secondRdTot.substr(0, 4)+'년 '+li[0].secondRdTot.substr(5, 1)+'분기';
		var third = li[0].thirdRdTot.substr(0, 4)+'년 '+li[0].thirdRdTot.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstRdWday', 'firstRdFri', 'firstRdWend', 'firstRdTot',
						'secondRdWday', 'secondRdFri', 'secondRdWend', 'secondRdTot',
						'thirdRdWday', 'thirdRdFri', 'thirdRdWend', 'thirdRdTot'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_4_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];
		
		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '평일',
					data: [parseInt(item.firstRdWday), parseInt(item.secondRdWday), parseInt(item.thirdRdWday)]
				},
				{
					name: '금요일',
					data: [parseInt(item.firstRdFri), parseInt(item.secondRdFri), parseInt(item.thirdRdFri)]
				},
				{
					name: '주말',
					data: [parseInt(item.firstRdWend), parseInt(item.secondRdWend), parseInt(item.thirdRdWend)]
				},
				{
					name: '주',
					data: [parseInt(item.firstRdTot), parseInt(item.secondRdTot), parseInt(item.thirdRdTot)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_3_4_0');
		this._chart_3_4_0 = toastui.Chart.columnChart({ el, data, options });
		
		//table 2
		table = div.find('table').eq(1);
		el = div.find('.graph-chart').eq(1).get(0);
		
		tbody = table.find('tbody');
		th = table.find('thead > tr:first > th');
		
		li = this._data.BldgDay;
		item = li[1];
		
		first = li[0].firstBlTot.substr(0, 4)+'년 '+li[0].firstBlTot.substr(5, 1)+'분기';
		second = li[0].secondBlTot.substr(0, 4)+'년 '+li[0].secondBlTot.substr(5, 1)+'분기';
		third = li[0].thirdBlTot.substr(0, 4)+'년 '+li[0].thirdBlTot.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		props = ['region', 'firstBlWday', 'firstBlFri', 'firstBlWend', 'firstBlTot',
						'secondBlWday', 'secondBlFri', 'secondBlWend', 'secondBlTot',
						'thirdBlWday', 'thirdBlFri', 'thirdBlWend', 'thirdBlTot'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_4_1_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart 2
		data = {
			categories: [first, second, third],
			series: [
				{
					name: '평일',
					data: [parseInt(item.firstBlWday), parseInt(item.secondBlWday), parseInt(item.thirdBlWday)]
				},
				{
					name: '금요일',
					data: [parseInt(item.firstBlFri), parseInt(item.secondBlFri), parseInt(item.thirdBlFri)]
				},
				{
					name: '주말',
					data: [parseInt(item.firstBlWend), parseInt(item.secondBlWend), parseInt(item.thirdBlWend)]
				},
				{
					name: '주',
					data: [parseInt(item.firstBlTot), parseInt(item.secondBlTot), parseInt(item.thirdBlTot)]
				},
 			],
		};
		
		options = Func.chartCommonOption('chart_3_4_1');
		this._chart_3_4_1 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_3_5 : function() {
		var div = $('.subtabcontent-wrap').eq(2).children('div').eq(4);
		Func.commonBaseDate(div, 6);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.RplSexAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotCnt.substr(0, 4)+'년 '+li[0].firstTotCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotCnt.substr(0, 4)+'년 '+li[0].secondTotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotCnt.substr(0, 4)+'년 '+li[0].thirdTotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstManCnt', 'firstWmnCnt', 'firstTotCnt',
						'secondManCnt', 'secondWmnCnt', 'secondTotCnt',
						'thirdManCnt', 'thirdWmnCnt', 'thirdTotCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_5_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstManCnt), parseInt(item.secondManCnt), parseInt(item.thirdManCnt)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstWmnCnt), parseInt(item.secondWmnCnt), parseInt(item.thirdWmnCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_3_5_0');
		this._chart_3_5_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_3_6 : function() {
		var div = $('.subtabcontent-wrap').eq(2).children('div').eq(5);
		Func.commonBaseDate(div, 6);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.RplSexAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotCnt.substr(0, 4)+'년 '+li[0].firstTotCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotCnt.substr(0, 4)+'년 '+li[0].secondTotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotCnt.substr(0, 4)+'년 '+li[0].thirdTotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstYthCnt', 'firstPpsCnt', 'firstOldCnt', 'firstTotCnt',
						'secondYthCnt', 'secondPpsCnt', 'secondOldCnt', 'secondTotCnt',
						'thirdYthCnt', 'thirdPpsCnt', 'thirdOldCnt', 'thirdTotCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_6_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];
		
		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '유소년',
					data: [parseInt(item.firstYthCnt), parseInt(item.secondYthCnt), parseInt(item.thirdYthCnt)]
				},
				{
					name: '생산가능',
					data: [parseInt(item.firstPpsCnt), parseInt(item.secondPpsCnt), parseInt(item.thirdPpsCnt)]
				},
				{
					name: '노령',
					data: [parseInt(item.firstOldCnt), parseInt(item.secondOldCnt), parseInt(item.thirdOldCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_3_6_0');
		this._chart_3_6_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_3_7 : function() {
		var div = $('.subtabcontent-wrap').eq(2).children('div').eq(6);
		Func.commonBaseDate(div, 6);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.WplSexAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotEmpCnt.substr(0, 4)+'년 '+li[0].firstTotEmpCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotEmpCnt.substr(0, 4)+'년 '+li[0].secondTotEmpCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotEmpCnt.substr(0, 4)+'년 '+li[0].thirdTotEmpCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstManEmpCnt', 'firstWmnEmpCnt', 'firstTotEmpCnt',
						'secondManEmpCnt', 'secondWmnEmpCnt', 'secondTotEmpCnt',
						'thirdManEmpCnt', 'thirdWmnEmpCnt', 'thirdTotEmpCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_7_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstManEmpCnt), parseInt(item.secondManEmpCnt), parseInt(item.thirdManEmpCnt)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstWmnEmpCnt), parseInt(item.secondWmnEmpCnt), parseInt(item.thirdWmnEmpCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotEmpCnt), parseInt(item.secondTotEmpCnt), parseInt(item.thirdTotEmpCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_3_7_0');
		this._chart_3_7_0 = toastui.Chart.columnChart({ el, data, options });
	},
/*	tab_3_8 : function() {
		var div = $('.subtabcontent-wrap').eq(2).children('div').eq(7);
		Func.commonBaseDate(div, 6);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.WplSexAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotEmpCnt.substr(0, 4)+'년 '+li[0].firstTotEmpCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotEmpCnt.substr(0, 4)+'년 '+li[0].secondTotEmpCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotEmpCnt.substr(0, 4)+'년 '+li[0].thirdTotEmpCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstRglrManCnt', 'firstRglrWmnCnt', 'firstTmprManCnt', 'firstTmprWmnCnt', 'firstTotEmpCnt',
						'secondRglrManCnt', 'secondRglrWmnCnt', 'secondTmprManCnt', 'secondTmprWmnCnt', 'secondTotEmpCnt',
						'thirdRglrManCnt', 'thirdRglrWmnCnt', 'thirdTmprManCnt', 'thirdTmprWmnCnt', 'thirdTotEmpCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_3_8_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '상용직 남성',
					data: [parseInt(item.firstRglrManCnt), parseInt(item.secondRglrManCnt), parseInt(item.thirdRglrManCnt)]
				},
				{
					name: '상용직 여성',
					data: [parseInt(item.firstRglrWmnCnt), parseInt(item.secondRglrWmnCnt), parseInt(item.thirdRglrWmnCnt)]
				},
				{
					name: '일용직 남성',
					data: [parseInt(item.firstTmprManCnt), parseInt(item.secondTmprManCnt), parseInt(item.thirdTmprManCnt)]
				},
				{
					name: '일용직 여성',
					data: [parseInt(item.firstTmprWmnCnt), parseInt(item.secondTmprWmnCnt), parseInt(item.thirdTmprWmnCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotEmpCnt), parseInt(item.secondTotEmpCnt), parseInt(item.thirdTotEmpCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_3_8_0');
		this._chart_3_8_0 = toastui.Chart.columnChart({ el, data, options });
	},*/
	tab_4_1 : function() {
		var div = $('.subtabcontent-wrap').eq(3).children('div').eq(0);
		Func.commonBaseDate(div, 7);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.IndOalp;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstAvgOalp.substr(0, 4)+'년 '+li[0].firstAvgOalp.substr(5, 1)+'분기';
		var second = li[0].secondAvgOalp.substr(0, 4)+'년 '+li[0].secondAvgOalp.substr(5, 1)+'분기';
		var third = li[0].thirdAvgOalp.substr(0, 4)+'년 '+li[0].thirdAvgOalp.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstAvgOalp', 'secondAvgOalp', 'thirdAvgOalp'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_4_1_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '공시지가',
					data: [parseInt(item.firstAvgOalp), parseInt(item.secondAvgOalp), parseInt(item.thirdAvgOalp)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_4_1_0');
		this._chart_4_1_0 = toastui.Chart.columnChart({ el, data, options });
		
		//table 2
		table = div.find('table').eq(1);
		el = div.find('.graph-chart').eq(1).get(0);
		
		tbody = table.find('tbody');
		th = table.find('thead > tr:first > th');
		
		li = this._data.IndOalp;
		item = li[1];
		
		first = li[0].firstIrdRt.substr(0, 4)+'년 '+li[0].firstIrdRt.substr(5, 1)+'분기';
		second = li[0].secondIrdRt.substr(0, 4)+'년 '+li[0].secondIrdRt.substr(5, 1)+'분기';
		third = li[0].thirdIrdRt.substr(0, 4)+'년 '+li[0].thirdIrdRt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		props = ['region', 'firstIrdRt', 'secondIrdRt', 'thirdIrdRt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_4_1_1_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart 2
		data = {
			categories: [first, second, third],
			series: [
				{
					name: '변동율',
					data: [parseInt(item.firstIrdRt), parseInt(item.secondIrdRt), parseInt(item.thirdIrdRt)]
				},
 			],
		};
		
		options = Func.chartCommonOption('chart_4_1_1');
		this._chart_4_1_1 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_4_2 : function() {
		var div = $('.subtabcontent-wrap').eq(3).children('div').eq(1);
		Func.commonBaseDate(div, 8);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.AptHhCnt;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotCnt.substr(0, 4)+'년 '+li[0].firstTotCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotCnt.substr(0, 4)+'년 '+li[0].secondTotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotCnt.substr(0, 4)+'년 '+li[0].thirdTotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstGitaCnt', 'firstAptCnt', 'firstTotCnt',
						'secondGitaCnt', 'secondAptCnt', 'secondTotCnt',
						'thirdGitaCnt', 'thirdAptCnt', 'thirdTotCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_4_2_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '비아파트',
					data: [parseInt(item.firstGitaCnt), parseInt(item.secondGitaCnt), parseInt(item.thirdGitaCnt)]
				},
				{
					name: '아파트',
					data: [parseInt(item.firstAptCnt), parseInt(item.secondAptCnt), parseInt(item.thirdAptCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_4_2_0');
		this._chart_4_2_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_4_3 : function() {
		var div = $('.subtabcontent-wrap').eq(3).children('div').eq(2);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		var li = this._data.SobiTrend;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		// 차트 4개 전부 초기화
		$(div.find('.graph-chart')).empty();
		
		var data = {
			categories: ['전체업종'],
			series: [],
		};
		
		for(var n=0; n<li.length; n++) {
			var item = li[n];
			if(item.sortno != 0)
				continue;
				
			var t = {};
			t.name = item.cdNm;
			t.data = parseFloat(item.rt);
			data.series.push(t);
		}
		
		var options = Func.chartCommonOption('chart_4_3_0');
		toastui.Chart.pieChart({ el, data, options });
		
		//소매업
		el = div.find('.graph-chart').eq(1).get(0);
		data = {
			categories: ['소매업'],
			series: [],
		};
		
		for(var n=0; n<li.length; n++) {
			var item = li[n];
			if(item.sortno != 1)
				continue;
				
			var t = {};
			t.name = item.cdNm;
			t.data = parseFloat(item.rt);
			data.series.push(t);
		}

		toastui.Chart.pieChart({ el, data, options });
		
		//서비스업
		el = div.find('.graph-chart').eq(2).get(0);
		data = {
			categories: ['서비스업'],
			series: [],
		};
		
		for(var n=0; n<li.length; n++) {
			var item = li[n];
			if(item.sortno != 2)
				continue;
				
			var t = {};
			t.name = item.cdNm;
			t.data = parseFloat(item.rt);
			data.series.push(t);
		}
		
		toastui.Chart.pieChart({ el, data, options });
		
		//외식업
		el = div.find('.graph-chart').eq(3).get(0);
		data = {
			categories: ['외식업'],
			series: [],
		};
		
		for(var n=0; n<li.length; n++) {
			var item = li[n];
			if(item.sortno != 3)
				continue;
				
			var t = {};
			t.name = item.cdNm;
			t.data = parseFloat(item.rt);
			data.series.push(t);
		}
		
		toastui.Chart.pieChart({ el, data, options });
	},
	tab_4_4 : function() {
		var div = $('.subtabcontent-wrap').eq(3).children('div').eq(3);
		Func.commonBaseDate(div, 9);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var td = table.find('td');
		
		var item = this._data.AptCpx;
		
		// 이슈사항 fix (item.arSqmt66HhCnt -> item[0].arSqmt66HhCnt)
		// 		  or item = item[0]
		item = item[0];
		
		if(item == null || item == undefined || item.arSqmt66HhCnt == null || item.arSqmt66HhCnt == undefined) {
			return;
		}
		
		//table 1
		var total = parseInt(item.arSqmt66HhCnt)+parseInt(item.arSqmt99HhCnt)+parseInt(item.arSqmt132HhCnt)+parseInt(item.arSqmt165HhCnt);
		$(td[1]).html(Util.commaString(total, 0));
		$(td[2]).html(Util.commaString(item.arSqmt66HhCnt, 0));
		$(td[3]).html(Util.commaString(item.arSqmt99HhCnt, 0));
		$(td[4]).html(Util.commaString(item.arSqmt132HhCnt, 0));
		$(td[5]).html(Util.commaString(item.arSqmt165HhCnt, 0));
		
		//chart draw
		$(el).empty();

		var data = {
			categories: ['총가구수', '66㎡이하', '99㎡이하', '132㎡이하', '165㎡이하'],
			series: [
				{
					name: '아파트 가구수',
					data: [total, parseInt(item.arSqmt66HhCnt), parseInt(item.arSqmt99HhCnt), parseInt(item.arSqmt132HhCnt), parseInt(item.arSqmt165HhCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_4_4_0');
		toastui.Chart.columnChart({ el, data, options });
		
		//table 2
		table = div.find('table').eq(1);
		el = div.find('.graph-chart').eq(1).get(0);
		
		td = table.find('td');
		
		$(td[1]).html(Util.commaString(item.mlnwn100LtHhCnt, 0));
		$(td[2]).html(Util.commaString(item.mlnwn100HhCnt, 0));
		$(td[3]).html(Util.commaString(item.mlnwn200HhCnt, 0));
		$(td[4]).html(Util.commaString(item.mlnwn300HhCnt, 0));
		$(td[5]).html(Util.commaString(item.mlnwn400HhCnt, 0));
		$(td[6]).html(Util.commaString(item.mlnwn500HhCnt, 0));
		$(td[7]).html(Util.commaString(item.mlnwn600GtetHhCnt, 0));
		
		//chart 2
		data = {
			categories: ['1억이하', '1억대', '2억대', '3억대', '4억대', '5억대', '6억이상'],
			series: [
				{
					name: '아파트 가격대',
					data: [parseInt(item.mlnwn100LtHhCnt), parseInt(item.mlnwn100HhCnt), parseInt(item.mlnwn200HhCnt),
						parseInt(item.mlnwn300HhCnt), parseInt(item.mlnwn400HhCnt), parseInt(item.mlnwn500HhCnt), parseInt(item.mlnwn600GtetHhCnt)]
				},
 			],
		};
		
		//chart draw
		$(el).empty();
		
		options = Func.chartCommonOption('chart_4_4_1');
		toastui.Chart.columnChart({ el, data, options });
	},
	tab_4_5 : function() {
		var div = $('.subtabcontent-wrap').eq(3).children('div').eq(4);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		
		$(tbody).empty();
		$(el).empty();
		
		var li = this._data.Fclty;
		if(li == null || li == undefined)
			return;

		//chart draw
		var data = {
			categories: ['시설수'],
			series: [],
		};
		
		// 차트 fix, data 형태는 Array 로 줘야 tui-chart 라이브러리에서 for-each 가 가능하므로, a = [] 생성 후 데이터 넣어줌
		for(var i=0; i<li.length; i++) {
			var tr =  $('<tr>');
			$('<td>').html(li[i].cdNm).appendTo(tr);
			$('<td>').html(Util.commaString(li[i].count, 0)).appendTo(tr);
			$(tbody).append(tr);
			
			//chart data
			var t = {};
			var a = [];
			
			t.name = li[i].cdNm;
			
			a.push(li[i].count);
			t.data = a;
			
			data.series.push(t);
		}
		
		var options = Func.chartCommonOption('chart_4_5_0');
		toastui.Chart.columnChart({ el, data, options });
	},
	tab_5_1 : function() {
		var div = $('.subtabcontent-wrap').eq(4).children('div').eq(0);
		Func.commonBaseDate(div, 10);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.SobiSexAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotCnt.substr(0, 4)+'년 '+li[0].firstTotCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotCnt.substr(0, 4)+'년 '+li[0].secondTotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotCnt.substr(0, 4)+'년 '+li[0].thirdTotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstManCnt', 'firstWmnCnt', 'firstTotCnt',
						'secondManCnt', 'secondWmnCnt', 'secondTotCnt',
						'thirdManCnt', 'thirdWmnCnt', 'thirdTotCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_5_1_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstManCnt), parseInt(item.secondManCnt), parseInt(item.thirdManCnt)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstWmnCnt), parseInt(item.secondWmnCnt), parseInt(item.thirdWmnCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_5_1_0');
		this._chart_5_1_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_5_2 : function() {
		var div = $('.subtabcontent-wrap').eq(4).children('div').eq(1);
		Func.commonBaseDate(div, 10);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.SobiSexAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstIestotCnt.substr(0, 4)+'년 '+li[0].firstIestotCnt.substr(5, 1)+'분기';
		var second = li[0].secondIestotCnt.substr(0, 4)+'년 '+li[0].secondIestotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdIestotCnt.substr(0, 4)+'년 '+li[0].thirdIestotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstIes1020Cnt', 'firstIes3040Cnt', 'firstIes5060Cnt', 'firstIestotCnt',
						'secondIes1020Cnt', 'secondIes3040Cnt', 'secondIes5060Cnt', 'secondIestotCnt',
						'thirdIes1020Cnt', 'thirdIes3040Cnt', 'thirdIes5060Cnt', 'thirdIestotCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_5_2_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '10~20대',
					data: [parseInt(item.firstIes1020Cnt), parseInt(item.secondIes1020Cnt), parseInt(item.thirdIes1020Cnt)]
				},
				{
					name: '30~40대',
					data: [parseInt(item.firstIes3040Cnt), parseInt(item.secondIes3040Cnt), parseInt(item.thirdIes3040Cnt)]
				},
				{
					name: '50~60대',
					data: [parseInt(item.firstIes5060Cnt), parseInt(item.secondIes5060Cnt), parseInt(item.thirdIes5060Cnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstIestotCnt), parseInt(item.secondIestotCnt), parseInt(item.thirdIestotCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_5_2_0');
		this._chart_5_2_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_5_3 : function() {
		var div = $('.subtabcontent-wrap').eq(4).children('div').eq(2);
		Func.commonBaseDate(div, 10);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.SobiTmzn;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotTmznCnt.substr(0, 4)+'년 '+li[0].firstTotTmznCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotTmznCnt.substr(0, 4)+'년 '+li[0].secondTotTmznCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotTmznCnt.substr(0, 4)+'년 '+li[0].thirdTotTmznCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstMrnCnt', 'firstAftCnt', 'firstEvnCnt', 'firstTotTmznCnt',
						'secondMrnCnt', 'secondAftCnt', 'secondEvnCnt', 'secondTotTmznCnt',
						'thirdMrnCnt', 'thirdAftCnt', 'thirdEvnCnt', 'thirdTotTmznCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_5_3_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '오전',
					data: [parseInt(item.firstMrnCnt), parseInt(item.secondMrnCnt), parseInt(item.thirdMrnCnt)]
				},
				{
					name: '오후',
					data: [parseInt(item.firstAftCnt), parseInt(item.secondAftCnt), parseInt(item.thirdAftCnt)]
				},
				{
					name: '저녁',
					data: [parseInt(item.firstEvnCnt), parseInt(item.secondEvnCnt), parseInt(item.thirdEvnCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotTmznCnt), parseInt(item.secondTotTmznCnt), parseInt(item.thirdTotTmznCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_5_3_0');
		this._chart_5_3_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_5_4 : function() {
		var div = $('.subtabcontent-wrap').eq(4).children('div').eq(3);
		Func.commonBaseDate(div, 10);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.SobiDay;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotDayCnt.substr(0, 4)+'년 '+li[0].firstTotDayCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotDayCnt.substr(0, 4)+'년 '+li[0].secondTotDayCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotDayCnt.substr(0, 4)+'년 '+li[0].thirdTotDayCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstWdayCnt', 'firstFriCnt', 'firstWendCnt', 'firstTotDayCnt',
						'secondWdayCnt', 'secondFriCnt', 'secondWendCnt', 'secondTotDayCnt',
						'thirdWdayCnt', 'thirdFriCnt', 'thirdWendCnt', 'thirdTotDayCnt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_5_4_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '평일',
					data: [parseInt(item.firstWdayCnt), parseInt(item.secondWdayCnt), parseInt(item.thirdWdayCnt)]
				},
				{
					name: '금요일',
					data: [parseInt(item.firstFriCnt), parseInt(item.secondFriCnt), parseInt(item.thirdFriCnt)]
				},
				{
					name: '주말',
					data: [parseInt(item.firstWendCnt), parseInt(item.secondWendCnt), parseInt(item.thirdWendCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotDayCnt), parseInt(item.secondTotDayCnt), parseInt(item.thirdTotDayCnt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_5_4_0');
		this._chart_5_4_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_5_5 : function() {
		var div = $('.subtabcontent-wrap').eq(4).children('div').eq(4);
		Func.commonBaseDate(div, 11);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.SobiSexAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotCnt.substr(0, 4)+'년 '+li[0].firstTotCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotCnt.substr(0, 4)+'년 '+li[0].secondTotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotCnt.substr(0, 4)+'년 '+li[0].thirdTotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstManAmt', 'firstWmnAmt', 'firstTotAmt',
						'secondManAmt', 'secondWmnAmt', 'secondTotAmt',
						'thirdManAmt', 'thirdWmnAmt', 'thirdTotAmt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_5_5_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstManAmt), parseInt(item.secondManAmt), parseInt(item.thirdManAmt)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstWmnAmt), parseInt(item.secondWmnAmt), parseInt(item.thirdWmnAmt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotAmt), parseInt(item.secondTotAmt), parseInt(item.thirdTotAmt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_5_5_0');
		this._chart_5_5_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_5_6 : function() {
		var div = $('.subtabcontent-wrap').eq(4).children('div').eq(5);
		Func.commonBaseDate(div, 11);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.SobiSexAge;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstIestotCnt.substr(0, 4)+'년 '+li[0].firstIestotCnt.substr(5, 1)+'분기';
		var second = li[0].secondIestotCnt.substr(0, 4)+'년 '+li[0].secondIestotCnt.substr(5, 1)+'분기';
		var third = li[0].thirdIestotCnt.substr(0, 4)+'년 '+li[0].thirdIestotCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstIes1020Amt', 'firstIes3040Amt', 'firstIes5060Amt', 'firstIestotAmt',
						'secondIes1020Amt', 'secondIes3040Amt', 'secondIes5060Amt', 'secondIestotAmt',
						'thirdIes1020Amt', 'thirdIes3040Amt', 'thirdIes5060Amt', 'thirdIestotAmt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_5_2_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '10~20대',
					data: [parseInt(item.firstIes1020Amt), parseInt(item.secondIes1020Amt), parseInt(item.thirdIes1020Amt)]
				},
				{
					name: '30~40대',
					data: [parseInt(item.firstIes3040Amt), parseInt(item.secondIes3040Amt), parseInt(item.thirdIes3040Amt)]
				},
				{
					name: '50~60대',
					data: [parseInt(item.firstIes5060Amt), parseInt(item.secondIes5060Amt), parseInt(item.thirdIes5060Amt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstIestotAmt), parseInt(item.secondIestotAmt), parseInt(item.thirdIestotAmt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_5_6_0');
		this._chart_5_6_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_5_7 : function() {
		var div = $('.subtabcontent-wrap').eq(4).children('div').eq(6);
		Func.commonBaseDate(div, 11);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.SobiTmzn;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotTmznCnt.substr(0, 4)+'년 '+li[0].firstTotTmznCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotTmznCnt.substr(0, 4)+'년 '+li[0].secondTotTmznCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotTmznCnt.substr(0, 4)+'년 '+li[0].thirdTotTmznCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstMrnAmt', 'firstAftAmt', 'firstEvnAmt', 'firstTotTmznAmt',
						'secondMrnAmt', 'secondAftAmt', 'secondEvnAmt', 'secondTotTmznAmt',
						'thirdMrnAmt', 'thirdAftAmt', 'thirdEvnAmt', 'thirdTotTmznAmt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_5_3_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '오전',
					data: [parseInt(item.firstMrnAmt), parseInt(item.secondMrnAmt), parseInt(item.thirdMrnAmt)]
				},
				{
					name: '오후',
					data: [parseInt(item.firstAftAmt), parseInt(item.secondAftAmt), parseInt(item.thirdAftAmt)]
				},
				{
					name: '저녁',
					data: [parseInt(item.firstEvnAmt), parseInt(item.secondEvnAmt), parseInt(item.thirdEvnAmt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotTmznAmt), parseInt(item.secondTotTmznAmt), parseInt(item.thirdTotTmznAmt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_5_3_0');
		this._chart_5_3_0 = toastui.Chart.columnChart({ el, data, options });
	},
	tab_5_8 : function() {
		var div = $('.subtabcontent-wrap').eq(4).children('div').eq(7);
		Func.commonBaseDate(div, 11);
		var table = div.find('table').eq(0);
		var el = div.find('.graph-chart').eq(0).get(0);
		
		//table draw
		var tbody = table.find('tbody');
		var th = table.find('thead > tr:first > th');
		
		var li = this._data.SobiDay;
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = li[0].firstTotDayCnt.substr(0, 4)+'년 '+li[0].firstTotDayCnt.substr(5, 1)+'분기';
		var second = li[0].secondTotDayCnt.substr(0, 4)+'년 '+li[0].secondTotDayCnt.substr(5, 1)+'분기';
		var third = li[0].thirdTotDayCnt.substr(0, 4)+'년 '+li[0].thirdTotDayCnt.substr(5, 1)+'분기';
		
		$(th[1]).html(first);
		$(th[2]).html(second);
		$(th[3]).html(third);
		
		$(tbody).empty();
		$(el).empty();
		
		var props = ['region', 'firstWdayAmt', 'firstFriAmt', 'firstWendAmt', 'firstTotDayAmt',
						'secondWdayAmt', 'secondFriAmt', 'secondWendAmt', 'secondTotDayAmt',
						'thirdWdayAmt', 'thirdFriAmt', 'thirdWendAmt', 'thirdTotDayAmt'];
		
		for(var i=1; i<li.length; i++) {
			Func.insertRow('chart_5_8_0_reload', tbody, li[i], props, i==1?true:false);
		}
		
		//chart draw
		var item = li[1];

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '평일',
					data: [parseInt(item.firstWdayAmt), parseInt(item.secondWdayAmt), parseInt(item.thirdWdayAmt)]
				},
				{
					name: '금요일',
					data: [parseInt(item.firstFriAmt), parseInt(item.secondFriAmt), parseInt(item.thirdFriAmt)]
				},
				{
					name: '주말',
					data: [parseInt(item.firstWendAmt), parseInt(item.secondWendAmt), parseInt(item.thirdWendAmt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotDayAmt), parseInt(item.secondTotDayAmt), parseInt(item.thirdTotDayAmt)]
				},
 			],
		};
		
		var options = Func.chartCommonOption('chart_5_8_0');
		this._chart_5_8_0 = toastui.Chart.columnChart({ el, data, options });
	},
	chart_1_1_0_reload : function(node) {
		var period = this._data.UpjongStorCnt[0];
		var item = this._data.UpjongStorCnt[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotCnt.substr(0, 4)+'년 '+period.firstTotCnt.substr(5, 1)+'분기';
		var second = period.secondTotCnt.substr(0, 4)+'년 '+period.secondTotCnt.substr(5, 1)+'분기';
		var third = period.thirdTotCnt.substr(0, 4)+'년 '+period.thirdTotCnt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '프랜차이즈',
					data: [parseInt(item.firstFrncCnt), parseInt(item.secondFrncCnt), parseInt(item.thirdFrncCnt)]
				},
				{
					name: '일반점포',
					data: [parseInt(item.firstGnrlCnt), parseInt(item.secondGnrlCnt), parseInt(item.thirdGnrlCnt)]
				},
				{
					name: '점포수',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		this._chart_1_1_0.setData(data);
	},
	chart_1_2_0_reload : function(node) {
		var period = this._data.UpjongStorCnt[0];
		var item = this._data.UpjongStorCnt[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotCnt.substr(0, 4)+'년 '+period.firstTotCnt.substr(5, 1)+'분기';
		var second = period.secondTotCnt.substr(0, 4)+'년 '+period.secondTotCnt.substr(5, 1)+'분기';
		var third = period.thirdTotCnt.substr(0, 4)+'년 '+period.thirdTotCnt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '개업수',
					data: [parseInt(item.firstOpbizCnt), parseInt(item.secondOpbizCnt), parseInt(item.thirdOpbizCnt)]
				},
				{
					name: '폐업수',
					data: [parseInt(item.firstClsbizCnt), parseInt(item.secondClsbizCnt), parseInt(item.thirdClsbizCnt)]
				},
				{
					name: '개업률',
					data: [parseInt(item.firstOpbizRt), parseInt(item.secondOpbizRt), parseInt(item.thirdOpbizRt)]
				},
				{
					name: '폐업률',
					data: [parseInt(item.firstClsbizRt), parseInt(item.secondClsbizRt), parseInt(item.thirdClsbizRt)]
				},
 			],
		};

		this._chart_1_2_0.setData(data);
	},
	chart_1_3_0_reload : function(node) {
		var period = this._data.UpjongSrvlRt[0];
		var item = this._data.UpjongSrvlRt[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstYr1Rt.substr(0, 4)+'년 '+period.firstYr1Rt.substr(5, 1)+'분기';
		var second = period.secondYr1Rt.substr(0, 4)+'년 '+period.secondYr1Rt.substr(5, 1)+'분기';
		var third = period.thirdYr1Rt.substr(0, 4)+'년 '+period.thirdYr1Rt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '1년생존률',
					data: [parseInt(item.firstYr1Rt), parseInt(item.firstYr3Rt), parseInt(item.firstYr5Rt)]
				},
				{
					name: '3년생존률',
					data: [parseInt(item.secondYr1Rt), parseInt(item.secondYr3Rt), parseInt(item.secondYr5Rt)]
				},
				{
					name: '5년생존률',
					data: [parseInt(item.thirdYr1Rt), parseInt(item.thirdYr3Rt), parseInt(item.thirdYr5Rt)]
				},
 			],
		};

		this._chart_1_3_0.setData(data);
	},
	chart_1_4_0_reload : function(node) {
		var period = this._data.UpjongAvgBsns[0];
		var item = this._data.UpjongAvgBsns[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstAvgBsns.substr(0, 4)+'년 '+period.firstAvgBsns.substr(5, 1)+'분기';
		var second = period.secondAvgBsns.substr(0, 4)+'년 '+period.secondAvgBsns.substr(5, 1)+'분기';
		var third = period.thirdAvgBsns.substr(0, 4)+'년 '+period.thirdAvgBsns.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '평균영업기간',
					data: [parseInt(item.firstAvgBsns), parseInt(item.secondAvgBsns), parseInt(item.thirdAvgBsns)]
				},
 			],
		};

		this._chart_1_4_0.setData(data);
	},
	chart_2_1_0_reload : function(node) {
		var period = this._data.MaechulQt[0];
		var item = this._data.MaechulQt[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstAmt.substr(0, 4)+'년 '+period.firstAmt.substr(5, 1)+'분기';
		var second = period.secondAmt.substr(0, 4)+'년 '+period.secondAmt.substr(5, 1)+'분기';
		var third = period.thirdAmt.substr(0, 4)+'년 '+period.thirdAmt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '매출액',
					data: [parseInt(item.firstAmt), parseInt(item.secondAmt), parseInt(item.thirdAmt)]
				},
 			],
		};

		this._chart_2_1_0.setData(data);
	},
	chart_2_2_0_reload : function(node) {
		var period = this._data.MaechulYr[0];
		var item = this._data.MaechulYr[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstAmt.substr(0, 4)+'년 '+period.firstAmt.substr(5, 1)+'분기';
		var second = period.secondAmt.substr(0, 4)+'년 '+period.secondAmt.substr(5, 1)+'분기';
		var third = period.thirdAmt.substr(0, 4)+'년 '+period.thirdAmt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '매출액',
					data: [parseInt(item.firstAmt), parseInt(item.secondAmt), parseInt(item.thirdAmt)]
				},
 			],
		};

		this._chart_2_2_0.setData(data);
	},
	chart_3_1_0_reload : function(node) {
		var period = this._data.RoadAge[0];
		var item = this._data.RoadAge[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstRdTot.substr(0, 4)+'년 '+period.firstRdTot.substr(5, 1)+'분기';
		var second = period.secondRdTot.substr(0, 4)+'년 '+period.secondRdTot.substr(5, 1)+'분기';
		var third = period.thirdRdTot.substr(0, 4)+'년 '+period.thirdRdTot.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstRdMan), parseInt(item.secondRdMan), parseInt(item.thirdRdMan)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstRdWmn), parseInt(item.secondRdWmn), parseInt(item.thirdRdWmn)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstRdTot), parseInt(item.secondRdTot), parseInt(item.thirdRdTot)]
				},
 			],
		};

		this._chart_3_1_0.setData(data);
	},
	chart_3_1_1_reload : function(node) {
		var period = this._data.BldgAge[0];
		var item = this._data.BldgAge[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstBlTot.substr(0, 4)+'년 '+period.firstBlTot.substr(5, 1)+'분기';
		var second = period.secondBlTot.substr(0, 4)+'년 '+period.secondBlTot.substr(5, 1)+'분기';
		var third = period.thirdBlTot.substr(0, 4)+'년 '+period.thirdBlTot.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstBlMan), parseInt(item.secondBlMan), parseInt(item.thirdBlMan)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstBlWmn), parseInt(item.secondBlWmn), parseInt(item.thirdBlWmn)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstBlTot), parseInt(item.secondBlTot), parseInt(item.thirdBlTot)]
				},
 			],
		};
		
		this._chart_3_1_1.setData(data);
	},
	chart_3_2_0_reload : function(node) {
		var period = this._data.RoadAge[0];
		var item = this._data.RoadAge[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstRdTot.substr(0, 4)+'년 '+period.firstRdTot.substr(5, 1)+'분기';
		var second = period.secondRdTot.substr(0, 4)+'년 '+period.secondRdTot.substr(5, 1)+'분기';
		var third = period.thirdRdTot.substr(0, 4)+'년 '+period.thirdRdTot.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '10~20대',
					data: [parseInt(item.firstRd1020), parseInt(item.secondRd1020), parseInt(item.thirdRd1020)]
				},
				{
					name: '30~40대',
					data: [parseInt(item.firstRd3040), parseInt(item.secondRd3040), parseInt(item.thirdRd3040)]
				},
				{
					name: '50~60대',
					data: [parseInt(item.firstRd5060), parseInt(item.secondRd5060), parseInt(item.thirdRd5060)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstRdTot), parseInt(item.secondRdTot), parseInt(item.thirdRdTot)]
				},
 			],
		};
		
		this._chart_3_2_0.setData(data);
	},
	chart_3_2_1_reload : function(node) {
		var period = this._data.BldgAge[0];
		var item = this._data.BldgAge[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstBlTot.substr(0, 4)+'년 '+period.firstBlTot.substr(5, 1)+'분기';
		var second = period.secondBlTot.substr(0, 4)+'년 '+period.secondBlTot.substr(5, 1)+'분기';
		var third = period.thirdBlTot.substr(0, 4)+'년 '+period.thirdBlTot.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '10~20대',
					data: [parseInt(item.firstBl1020), parseInt(item.secondBl1020), parseInt(item.thirdBl1020)]
				},
				{
					name: '30~40대',
					data: [parseInt(item.firstBl3040), parseInt(item.secondBl3040), parseInt(item.thirdBl3040)]
				},
				{
					name: '50~60대',
					data: [parseInt(item.firstBl5060), parseInt(item.secondBl5060), parseInt(item.thirdBl5060)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstBlTot), parseInt(item.secondBlTot), parseInt(item.thirdBlTot)]
				},
 			],
		};
		
		this._chart_3_2_1.setData(data);
	},
	chart_3_3_0_reload : function(node) {
		var period = this._data.RoadTime[0];
		var item = this._data.RoadTime[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstRdTot.substr(0, 4)+'년 '+period.firstRdTot.substr(5, 1)+'분기';
		var second = period.secondRdTot.substr(0, 4)+'년 '+period.secondRdTot.substr(5, 1)+'분기';
		var third = period.thirdRdTot.substr(0, 4)+'년 '+period.thirdRdTot.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '오전',
					data: [parseInt(item.firstRdMrn), parseInt(item.secondRdMrn), parseInt(item.thirdRdMrn)]
				},
				{
					name: '오후',
					data: [parseInt(item.firstRdAft), parseInt(item.secondRdAft), parseInt(item.thirdRdAft)]
				},
				{
					name: '저녁',
					data: [parseInt(item.firstRdEvn), parseInt(item.secondRdEvn), parseInt(item.thirdRdEvn)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstRdTot), parseInt(item.secondRdTot), parseInt(item.thirdRdTot)]
				},
 			],
		};
		
		this._chart_3_3_0.setData(data);
	},
	chart_3_3_1_reload : function(node) {
		var period = this._data.BldgTime[0];
		var item = this._data.BldgTime[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstBlTot.substr(0, 4)+'년 '+period.firstBlTot.substr(5, 1)+'분기';
		var second = period.secondBlTot.substr(0, 4)+'년 '+period.secondBlTot.substr(5, 1)+'분기';
		var third = period.thirdBlTot.substr(0, 4)+'년 '+period.thirdBlTot.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '오전',
					data: [parseInt(item.firstBlMrn), parseInt(item.secondBlMrn), parseInt(item.thirdBlMrn)]
				},
				{
					name: '오후',
					data: [parseInt(item.firstBlAft), parseInt(item.secondBlAft), parseInt(item.thirdBlAft)]
				},
				{
					name: '저녁',
					data: [parseInt(item.firstBlEvn), parseInt(item.secondBlEvn), parseInt(item.thirdBlEvn)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstBlTot), parseInt(item.secondBlTot), parseInt(item.thirdBlTot)]
				},
 			],
		};

		this._chart_3_3_1.setData(data);
	},
	chart_3_4_0_reload : function(node) {
		var period = this._data.RoadDay[0];
		var item = this._data.RoadDay[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstRdTot.substr(0, 4)+'년 '+period.firstRdTot.substr(5, 1)+'분기';
		var second = period.secondRdTot.substr(0, 4)+'년 '+period.secondRdTot.substr(5, 1)+'분기';
		var third = period.thirdRdTot.substr(0, 4)+'년 '+period.thirdRdTot.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '평일',
					data: [parseInt(item.firstRdWday), parseInt(item.secondRdWday), parseInt(item.thirdRdWday)]
				},
				{
					name: '금요일',
					data: [parseInt(item.firstRdFri), parseInt(item.secondRdFri), parseInt(item.thirdRdFri)]
				},
				{
					name: '주말',
					data: [parseInt(item.firstRdWend), parseInt(item.secondRdWend), parseInt(item.thirdRdWend)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstRdTot), parseInt(item.secondRdTot), parseInt(item.thirdRdTot)]
				},
 			],
		};
		
		this._chart_3_4_0.setData(data);
	},
	chart_3_4_1_reload : function(node) {
		var period = this._data.BldgDay[0];
		var item = this._data.BldgDay[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstBlTot.substr(0, 4)+'년 '+period.firstBlTot.substr(5, 1)+'분기';
		var second = period.secondBlTot.substr(0, 4)+'년 '+period.secondBlTot.substr(5, 1)+'분기';
		var third = period.thirdBlTot.substr(0, 4)+'년 '+period.thirdBlTot.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '평일',
					data: [parseInt(item.firstBlWday), parseInt(item.secondBlWday), parseInt(item.thirdBlWday)]
				},
				{
					name: '금요일',
					data: [parseInt(item.firstBlFri), parseInt(item.secondBlFri), parseInt(item.thirdBlFri)]
				},
				{
					name: '주말',
					data: [parseInt(item.firstBlWend), parseInt(item.secondBlWend), parseInt(item.thirdBlWend)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstBlTot), parseInt(item.secondBlTot), parseInt(item.thirdBlTot)]
				},
 			],
		};
		
		this._chart_3_4_1.setData(data);
	},
	chart_3_5_0_reload : function(node) {
		var period = this._data.RplSexAge[0];
		var item = this._data.RplSexAge[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotCnt.substr(0, 4)+'년 '+period.firstTotCnt.substr(5, 1)+'분기';
		var second = period.secondTotCnt.substr(0, 4)+'년 '+period.secondTotCnt.substr(5, 1)+'분기';
		var third = period.thirdTotCnt.substr(0, 4)+'년 '+period.thirdTotCnt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstManCnt), parseInt(item.secondManCnt), parseInt(item.thirdManCnt)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstWmnCnt), parseInt(item.secondWmnCnt), parseInt(item.thirdWmnCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};

		this._chart_3_5_0.setData(data);
	},
	chart_3_6_0_reload : function(node) {
		var period = this._data.RplSexAge[0];
		var item = this._data.RplSexAge[node+1];

		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotCnt.substr(0, 4)+'년 '+period.firstTotCnt.substr(5, 1)+'분기';
		var second = period.secondTotCnt.substr(0, 4)+'년 '+period.secondTotCnt.substr(5, 1)+'분기';
		var third = period.thirdTotCnt.substr(0, 4)+'년 '+period.thirdTotCnt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '유소년',
					data: [parseInt(item.firstYthCnt), parseInt(item.secondYthCnt), parseInt(item.thirdYthCnt)]
				},
				{
					name: '생산가능',
					data: [parseInt(item.firstPpsCnt), parseInt(item.secondPpsCnt), parseInt(item.thirdPpsCnt)]
				},
				{
					name: '노령',
					data: [parseInt(item.firstOldCnt), parseInt(item.secondOldCnt), parseInt(item.thirdOldCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		this._chart_3_6_0.setData(data);
	},
	chart_3_7_0_reload : function(node) {
		var period = this._data.WplSexAge[0];
		var item = this._data.WplSexAge[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotEmpCnt.substr(0, 4)+'년 '+period.firstTotEmpCnt.substr(5, 1)+'분기';
		var second = period.secondTotEmpCnt.substr(0, 4)+'년 '+period.secondTotEmpCnt.substr(5, 1)+'분기';
		var third = period.thirdTotEmpCnt.substr(0, 4)+'년 '+period.thirdTotEmpCnt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstManEmpCnt), parseInt(item.secondManEmpCnt), parseInt(item.thirdManEmpCnt)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstWmnEmpCnt), parseInt(item.secondWmnEmpCnt), parseInt(item.thirdWmnEmpCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotEmpCnt), parseInt(item.secondTotEmpCnt), parseInt(item.thirdTotEmpCnt)]
				},
 			],
		};
		
		this._chart_3_7_0.setData(data);
	},
	chart_3_8_0_reload : function(node) {
		var period = this._data.WplSexAge[0];
		var item = this._data.WplSexAge[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotEmpCnt.substr(0, 4)+'년 '+period.firstTotEmpCnt.substr(5, 1)+'분기';
		var second = period.secondTotEmpCnt.substr(0, 4)+'년 '+period.secondTotEmpCnt.substr(5, 1)+'분기';
		var third = period.thirdTotEmpCnt.substr(0, 4)+'년 '+period.thirdTotEmpCnt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '상용직 남성',
					data: [parseInt(item.firstRglrManCnt), parseInt(item.secondRglrManCnt), parseInt(item.thirdRglrManCnt)]
				},
				{
					name: '상용직 여성',
					data: [parseInt(item.firstRglrWmnCnt), parseInt(item.secondRglrWmnCnt), parseInt(item.thirdRglrWmnCnt)]
				},
				{
					name: '일용직 남성',
					data: [parseInt(item.firstTmprManCnt), parseInt(item.secondTmprManCnt), parseInt(item.thirdTmprManCnt)]
				},
				{
					name: '일용직 여성',
					data: [parseInt(item.firstTmprWmnCnt), parseInt(item.secondTmprWmnCnt), parseInt(item.thirdTmprWmnCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotEmpCnt), parseInt(item.secondTotEmpCnt), parseInt(item.thirdTotEmpCnt)]
				},
 			],
		};
		
		this._chart_3_8_0.setData(data);
	},
	chart_4_1_0_reload : function(node) {
		var period = this._data.IndOalp[0];
		var item = this._data.IndOalp[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstAvgOalp.substr(0, 4)+'년 '+period.firstAvgOalp.substr(5, 1)+'분기';
		var second = period.secondAvgOalp.substr(0, 4)+'년 '+period.secondAvgOalp.substr(5, 1)+'분기';
		var third = period.thirdAvgOalp.substr(0, 4)+'년 '+period.thirdAvgOalp.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '공시지가',
					data: [parseInt(item.firstAvgOalp), parseInt(item.secondAvgOalp), parseInt(item.thirdAvgOalp)]
				},
 			],
		};
		
		this._chart_4_1_0.setData(data);
	},
	chart_4_1_1_reload : function(node) {
		var period = this._data.IndOalp[0];
		var item = this._data.IndOalp[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstIrdRt.substr(0, 4)+'년 '+period.firstIrdRt.substr(5, 1)+'분기';
		var second = period.secondIrdRt.substr(0, 4)+'년 '+period.secondIrdRt.substr(5, 1)+'분기';
		var third = period.thirdIrdRt.substr(0, 4)+'년 '+period.thirdIrdRt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '변동율',
					data: [parseInt(item.firstIrdRt), parseInt(item.secondIrdRt), parseInt(item.thirdIrdRt)]
				},
 			],
		};
		
		this._chart_4_1_0.setData(data);
	},
	chart_4_2_0_reload : function(node) {
		var period = this._data.AptHhCnt[0];
		var item = this._data.AptHhCnt[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotCnt.substr(0, 4)+'년 '+period.firstTotCnt.substr(5, 1)+'분기';
		var second = period.secondTotCnt.substr(0, 4)+'년 '+period.secondTotCnt.substr(5, 1)+'분기';
		var third = period.thirdTotCnt.substr(0, 4)+'년 '+period.thirdTotCnt.substr(5, 1)+'분기';
		
		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '비아파트',
					data: [parseInt(item.firstGitaCnt), parseInt(item.secondGitaCnt), parseInt(item.thirdGitaCnt)]
				},
				{
					name: '아파트',
					data: [parseInt(item.firstAptCnt), parseInt(item.secondAptCnt), parseInt(item.thirdAptCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		this._chart_4_2_0.setData(data);
	},
	chart_5_1_0_reload : function(node) {
		var period = this._data.SobiSexAge[0];
		var item = this._data.SobiSexAge[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotCnt.substr(0, 4)+'년 '+period.firstTotCnt.substr(5, 1)+'분기';
		var second = period.secondTotCnt.substr(0, 4)+'년 '+period.secondTotCnt.substr(5, 1)+'분기';
		var third = period.thirdTotCnt.substr(0, 4)+'년 '+period.thirdTotCnt.substr(5, 1)+'분기';

		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstManCnt), parseInt(item.secondManCnt), parseInt(item.thirdManCnt)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstWmnCnt), parseInt(item.secondWmnCnt), parseInt(item.thirdWmnCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotCnt), parseInt(item.secondTotCnt), parseInt(item.thirdTotCnt)]
				},
 			],
		};
		
		this._chart_5_1_0.setData(data);
	},
	chart_5_2_0_reload : function(node) {
		var period = this._data.SobiSexAge[0];
		var item = this._data.SobiSexAge[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstIestotCnt.substr(0, 4)+'년 '+period.firstIestotCnt.substr(5, 1)+'분기';
		var second = period.secondIestotCnt.substr(0, 4)+'년 '+period.secondIestotCnt.substr(5, 1)+'분기';
		var third = period.thirdIestotCnt.substr(0, 4)+'년 '+period.thirdIestotCnt.substr(5, 1)+'분기';

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '10~20대',
					data: [parseInt(item.firstIes1020Cnt), parseInt(item.secondIes1020Cnt), parseInt(item.thirdIes1020Cnt)]
				},
				{
					name: '30~40대',
					data: [parseInt(item.firstIes3040Cnt), parseInt(item.secondIes3040Cnt), parseInt(item.thirdIes3040Cnt)]
				},
				{
					name: '50~60대',
					data: [parseInt(item.firstIes5060Cnt), parseInt(item.secondIes5060Cnt), parseInt(item.thirdIes5060Cnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstIestotCnt), parseInt(item.secondIestotCnt), parseInt(item.thirdIestotCnt)]
				},
 			],
		};
		
		this._chart_5_2_0.setData(data);
	},
	chart_5_3_0_reload : function(node) {
		var period = this._data.SobiTmzn[0];
		var item = this._data.SobiTmzn[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotTmznCnt.substr(0, 4)+'년 '+period.firstTotTmznCnt.substr(5, 1)+'분기';
		var second = period.secondTotTmznCnt.substr(0, 4)+'년 '+period.secondTotTmznCnt.substr(5, 1)+'분기';
		var third = period.thirdTotTmznCnt.substr(0, 4)+'년 '+period.thirdTotTmznCnt.substr(5, 1)+'분기';

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '오전',
					data: [parseInt(item.firstMrnCnt), parseInt(item.secondMrnCnt), parseInt(item.thirdMrnCnt)]
				},
				{
					name: '오후',
					data: [parseInt(item.firstAftCnt), parseInt(item.secondAftCnt), parseInt(item.thirdAftCnt)]
				},
				{
					name: '저녁',
					data: [parseInt(item.firstEvnCnt), parseInt(item.secondEvnCnt), parseInt(item.thirdEvnCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotTmznCnt), parseInt(item.secondTotTmznCnt), parseInt(item.thirdTotTmznCnt)]
				},
 			],
		};
		
		this._chart_5_3_0.setData(data);
	},
	chart_5_4_0_reload : function(node) {
		var period = this._data.SobiDay[0];
		var item = this._data.SobiDay[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotDayCnt.substr(0, 4)+'년 '+period.firstTotDayCnt.substr(5, 1)+'분기';
		var second = period.secondTotDayCnt.substr(0, 4)+'년 '+period.secondTotDayCnt.substr(5, 1)+'분기';
		var third = period.thirdTotDayCnt.substr(0, 4)+'년 '+period.thirdTotDayCnt.substr(5, 1)+'분기';
		
		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '평일',
					data: [parseInt(item.firstWdayCnt), parseInt(item.secondWdayCnt), parseInt(item.thirdWdayCnt)]
				},
				{
					name: '금요일',
					data: [parseInt(item.firstFriCnt), parseInt(item.secondFriCnt), parseInt(item.thirdFriCnt)]
				},
				{
					name: '주말',
					data: [parseInt(item.firstWendCnt), parseInt(item.secondWendCnt), parseInt(item.thirdWendCnt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotDayCnt), parseInt(item.secondTotDayCnt), parseInt(item.thirdTotDayCnt)]
				},
 			],
		};
		
		this._chart_5_4_0.setData(data);
	},
	chart_5_5_0_reload : function(node) {
		var period = this._data.SobiSexAge[0];
		var item = this._data.SobiSexAge[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotAmt.substr(0, 4)+'년 '+period.firstTotAmt.substr(5, 1)+'분기';
		var second = period.secondTotAmt.substr(0, 4)+'년 '+period.secondTotAmt.substr(5, 1)+'분기';
		var third = period.thirdTotAmt.substr(0, 4)+'년 '+period.thirdTotAmt.substr(5, 1)+'분기';

		const data = {
			categories: [first, second, third],
			series: [
				{
					name: '남성',
					data: [parseInt(item.firstManAmt), parseInt(item.secondManAmt), parseInt(item.thirdManAmt)]
				},
				{
					name: '여성',
					data: [parseInt(item.firstWmnAmt), parseInt(item.secondWmnAmt), parseInt(item.thirdWmnAmt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotAmt), parseInt(item.secondTotAmt), parseInt(item.thirdTotAmt)]
				},
 			],
		};
		
		this._chart_5_5_0.setData(data);
	},
	chart_5_6_0_reload : function(node) {
		var period = this._data.SobiSexAge[0];
		var item = this._data.SobiSexAge[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstIestotAmt.substr(0, 4)+'년 '+period.firstIestotAmt.substr(5, 1)+'분기';
		var second = period.secondIestotAmt.substr(0, 4)+'년 '+period.secondIestotAmt.substr(5, 1)+'분기';
		var third = period.thirdIestotAmt.substr(0, 4)+'년 '+period.thirdIestotAmt.substr(5, 1)+'분기';

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '10~20대',
					data: [parseInt(item.firstIes1020Amt), parseInt(item.secondIes1020Amt), parseInt(item.thirdIes1020Amt)]
				},
				{
					name: '30~40대',
					data: [parseInt(item.firstIes3040Amt), parseInt(item.secondIes3040Amt), parseInt(item.thirdIes3040Amt)]
				},
				{
					name: '50~60대',
					data: [parseInt(item.firstIes5060Amt), parseInt(item.secondIes5060Amt), parseInt(item.thirdIes5060Amt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstIestotAmt), parseInt(item.secondIestotAmt), parseInt(item.thirdIestotAmt)]
				},
 			],
		};
		
		this._chart_5_6_0.setData(data);
	},
	chart_5_7_0_reload : function(node) {
		var period = this._data.SobiTmzn[0];
		var item = this._data.SobiTmzn[node+1];
		
		// 예외 추가
		if (typeof li == "undefined") return;
		
		var first = period.firstTotTmznAmt.substr(0, 4)+'년 '+period.firstTotTmznAmt.substr(5, 1)+'분기';
		var second = period.secondTotTmznAmt.substr(0, 4)+'년 '+period.secondTotTmznAmt.substr(5, 1)+'분기';
		var third = period.thirdTotTmznAmt.substr(0, 4)+'년 '+period.thirdTotTmznAmt.substr(5, 1)+'분기';

		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '오전',
					data: [parseInt(item.firstMrnAmt), parseInt(item.secondMrnAmt), parseInt(item.thirdMrnAmt)]
				},
				{
					name: '오후',
					data: [parseInt(item.firstAftAmt), parseInt(item.secondAftAmt), parseInt(item.thirdAftAmt)]
				},
				{
					name: '저녁',
					data: [parseInt(item.firstEvnAmt), parseInt(item.secondEvnAmt), parseInt(item.thirdEvnAmt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotTmznAmt), parseInt(item.secondTotTmznAmt), parseInt(item.secondTotTmznAmt)]
				},
 			],
		};
		
		this._chart_5_7_0.setData(data);
	},
	chart_5_8_0_reload : function(node) {
		var period = this._data.SobiDay[0];
		var item = this._data.SobiDay[node+1];
		
		var first = period.firstTotDayAmt.substr(0, 4)+'년 '+period.firstTotDayAmt.substr(5, 1)+'분기';
		var second = period.secondTotDayAmt.substr(0, 4)+'년 '+period.secondTotDayAmt.substr(5, 1)+'분기';
		var third = period.thirdTotDayAmt.substr(0, 4)+'년 '+period.thirdTotDayAmt.substr(5, 1)+'분기';
		
		var data = {
			categories: [first, second, third],
			series: [
				{
					name: '평일',
					data: [parseInt(item.firstWdayAmt), parseInt(item.secondWdayAmt), parseInt(item.thirdWdayAmt)]
				},
				{
					name: '금요일',
					data: [parseInt(item.firstFriAmt), parseInt(item.secondFriAmt), parseInt(item.thirdFriAmt)]
				},
				{
					name: '주말',
					data: [parseInt(item.firstWendAmt), parseInt(item.secondWendAmt), parseInt(item.thirdWendAmt)]
				},
				{
					name: '합계',
					data: [parseInt(item.firstTotDayAmt), parseInt(item.secondTotDayAmt), parseInt(item.thirdTotDayAmt)]
				},
 			],
		};
		
		this._chart_5_8_0.setData(data);
	},
}

var Func = {
	commonBaseDate : function(div, type) {
		var unit = '개';
		
		$('#textdesc').css('display', 'none');
		if(type == 1) {
			
		}
		else if(type == 2) {
			unit = '%'
			$('#textdesc').css('display', 'block');
		}
		else if(type == 3) {
			unit = '원'
		}
		else if(type == 4) {
			unit = '년';
		}
		else if(type == 5) {
			unit = '수,%';
		}
		else if(type == 6) {
			unit = 'ha당 명';
		}
		else if(type == 66) {
			unit = 'ha당 명 (일평균)';
		}
		else if(type == 7) {
			unit = '원,%';
		}
		else if(type == 8) {
			unit = '수';
		}
		else if(type == 9) {
			unit = '가구';
		}
		else if(type == 10) {
			unit = '점포 당(건)';
		}
		else if(type == 11) {
			unit = '점포 당(원)';
		}
		var basedate = '단위 : '+unit;
		div.find('.basedate').text(basedate);
		div.find('span').html($('#induM').find('.selected').text());
	},
	insertRow : function(fc, tbody, rowdata, props, highlite) {
		var tr = $('<tr>');
		if(highlite) {
			$(tr).addClass('highlite');	
		}
		
		$.each(props, function(col, prop) {
			var td = $('<td>');
			
			var value = rowdata[prop];
			value = Util.commaString(value, 0);
			
			if(col == 0) {
				td.attr('fc', fc);
				value = '<span class="link-span">'+value+'</span>';
			}
			else {
				td.css('text-align', 'right');
			}
			
			$(td).html(value).appendTo(tr);
		});
		
		$(tbody).append(tr);
	},
	addAddress : function(type, list) {
		var uid = '#tabcontents';
		var tabs = $(uid).find('div .tab-content-address-wrap');
		var tab = tabs[type=='address'?0:1];
		
		var texts = $(uid).find('div .text');
		var text = texts[type=='address'?0:1];

		for(var idx=0; idx<list.length; idx++) {
			var item = list[idx];
			var place = type=='address'?item.address_name:item.place_name;
			$(tab).append('<div onclick="Doc.btnAddressSelect(this);" x="'+item.x+'" y="'+item.y+'">'+place+'</div>')
		}
		var p = type=='address'?'주소':'장소';
		var label = p+' <label>'+$(tab).children('div').length+'건</label>';
		if($(tab).children('div').length == 0) {
			label = '검색 결과가 존재하지 않습니다';
		}

		$(text).html(label);

		tab = tabs[type=='address'?2:3];
		text = texts[type=='address'?2:3];
		for(var idx=0; idx<list.length; idx++) {
			var item = list[idx];
			
			var place = type=='address'?item.address_name:item.place_name;
			$(tab).append('<div onclick="Doc.btnAddressSelect(this);" x="'+item.x+'" y="'+item.y+'">'+place+'</div>')
		}
		
		label = p+' <label>'+$(tab).children('div').length+'건</label>';
		if($(tab).children('div').length == 0) {
			label = '검색 결과가 존재하지 않습니다';
		}
		
		$(text).html(label);
	},
	//장소검색.
	placPlacesSearchCB : function(keyword, page) {
		$.ajax({ //장소 검색  //"&size="+placPerPage
			url : "https://dapi.kakao.com/v2/local/search/keyword.json?query="+ encodeURIComponent("경기" + keyword)+"&page="+page,
			//한페이지당 10개씩 리턴 , 초기 페이지 1
			type : "GET",
			async: false,
			cache: false,
			headers : {"Authorization": "KakaoAK d81d33b83873cbf39442da772f7a4bec"},
			success : function(data){
				
				var list = [];
				for(var i=0; i<data.documents.length; i++){
				    if(data.documents[i].address_name.substr(0,2) == '경기') {
				    	list.push(data.documents[i]);
				    }
			    }
			    Func.addAddress('place', list);
			    
				//마지막 페이지가 아니라면
			    if(data.meta.is_end == false) {
				    Func.placPlacesSearchCB(keyword,page+1); //다음 페이지를 호츨
			    }
			    else {

			    }
	
			},
			error: function (){
				alert('검색 결과 중 오류가 발생했습니다.');
				return;
			}
		})	
	},
	//주소검색.
	placAddressSearchCB : function(keyword, page) {
		$.ajax({ //장소 검색  //"&size="+placPerPage
			url : "https://dapi.kakao.com/v2/local/search/address.json?query="+ encodeURIComponent("경기" + keyword)+"&page="+page,
			//한페이지당 10개씩 리턴 , 초기 페이지 1
			type : "GET",
			async: false,
			cache: false,
			headers : {"Authorization": "KakaoAK d81d33b83873cbf39442da772f7a4bec"},
			success : function(data) {
				var list = [];
				for(var i=0; i<data.documents.length; i++) {
				    if(data.documents[i].address_name.substr(0,2) == '경기') {
				    	list.push(data.documents[i]);
				    }
			    }
			    Func.addAddress('address', list);
			    
				//마지막 페이지가 아니라면
			    if(data.meta.is_end == false) {
				    Func.placAddressSearchCB(keyword,page+1); //다음 페이지를 호츨
			    }
			    else {
				
			    }
	
			},
			error: function (){
				alert('검색 결과 중 오류가 발생했습니다.');
				return;
			}
		})	
	},
	insertInduM : function(uid, item) {
		var div = $('<div>');
		div.attr('code', item.lfbtCd);
		div.html(item.lfbtNm);
		
		$(uid).append(div);
	},
	chartCommonOption(type, w, h) {
		const commonTheme = this.chartCommonTheme(type);
		const commonSeries = this.chartCommonSeries(type);
		
		const options = {
			//chart: { width: w==undefined?1192:w, height: h==undefined?250:h },
			chart: { width: 'auto', height: 250 },
			series: commonSeries,
			legend: { align: 'bottom' },
			exportMenu: { visible: false },
			yAxis: {
				label: {
					formatter: function(value) {
						return Util.commaString(value, 0);
					},
				},
			},
			xAxis: {
				height: 30,
				label: {
					rotatable: false,
				},
				
			},
			tooltip: {
				formatter: function(value) {
					return Util.commaString(value, 0);
				},
			},
			theme: commonTheme,
		};
		
		return options;
	},
	chartCommonSeries(type) {
		var series = null;
		
		series = {
			dataLabels: {
				visible: true,
				formatter: function(value) {
					return Util.commaString(value, 0);
				}
			},
		};

		return series;
	},
	chartCommonTheme(type) {
		var theme = null;
		var colors = [ '#5baef2', '#aab7c3', '#ff9400'];
		
		if(type == 'chart2') {
			colors = [ '#5baef2', '#aab7c3', '#ff9400', '#cdcdcd'];
		}
		
		theme = {
			legend: {
				label: {
					fontSize: 12, fontWeight: 700, color: '#000',
				},
			},
			xAxis: {
				label: {
					fontSize: 13, fontWeight: 700, color: '#000',
				},
			},
			yAxis: {
				label: {
					fontSize: 12, fontWeight: 300, color: '#000',
				},
				width: 0,
			},
			series: {
				barWidth: 70, colors: colors,
				dataLabels: {
					fontSize: 16, fontWeight: 700, color: '#000',
				},
			}
		};

		return theme;
	},
	openSingleRepo() {
		var repo = $('.single');
		var m_repo = $('.multi');
		
		repo.css('height', 60);
		
		// repo display 핸들링
		// px 는 number 로 준다
		repo.animate({ height:586 });
		
		repo.css('display', 'block');
		m_repo.css('display', 'none');
		
		// 중요한 부분, 의존성으로 인해 어긋나는 현상 방지
		if($('.map_button_list').css('display') == 'block') {
			ReportUI.hide();
		}
	},
	openMultiRepo() {
		var repo = $('.single');
		var m_repo = $('.multi');
		
		m_repo.css('height', 60);
		
		ReportUI.hide();
		
		repo.css('display', 'none');
		m_repo.css('display', 'block');
	},
}

var Doc = {
	load : function() {		
		//side event
		//SideUI.event($('#btnlefthandle'), 'resizeEvent');
		//sub menu show/hide
		SubmenuUI.event('#nav');
	
		ReportUI.event('#bottomreportmove', 0.8, 60);
		
		this.sr = new ReportSingleUI();
		this.sr.event('#bottomsinglereportmove', 634, 60);
	
		this.buttonEvent();
		
		// init
		ReportUI.hide();

		//api call
		this.call();
	},
	call : function() {
		//api call...
		
		//업종
		var params = {};
		params.lfbtClssCd = '0';
		Api.call('getUpjongList', params);
		
		//자치 시군
		Api.call('get_sgList', '');

		//기준분기
		Api.call('get_stdr_qt', '');
	},
	btnRepoHide : function() {
		var repo = $('.single');

		// px 는 number 로 준다
		if (repo.css("height") == '586px') {
			repo.animate({
				height:60
			})
		} else {
			repo.animate({
				height:586
			})
		}
		
		// 메뉴 + icon 연동위해 실행, 참조 report 는 display none 처리
		ReportUI.hide();
	},
	buttonEvent : function() {
		
		//생활밀접업종 선택
		$('#induL > div').on('click', function () {
			//class 제거
			$(this).parent().children('div').removeClass('selected');
			$(this).addClass('selected');
			
			var params = {};
			params.lfbtClssCd = $(this).attr('code');
			Api.call('getUpjongList', params);
		});

		//행정구역
		$('#sglist').change(function() {
			var params = {};
			params.sggcd = $(this).val();
			Api.call('get_sgdList', params);
			
			//지도 이동
			Gis_Link.selectAreaInfo($(this).val());
		});
		
		//행정읍면동 선택
		$('#sgdlist').change(function() {
			var code = $(this).val();
			if(code == '0') {
				code = $('#sglist').val();
			}
			
			
			//지도 이동
			Gis_Link.selectAreaInfo(code);
		});
		
		//search enter event
		$("#address").keydown(function(key) {
			if (key.keyCode == 13) {
				Doc.btnAddressSearch();
			}
		});
		
		//연도 선택시 분기 변경
		$('#selectYear').change(function() {
			const qt = View._yearqt.filter(y => y.year == $(this).val());

			$('#selectQu').empty();
			var qlist = qt[0].qu;
			for(var idx = 0; idx < qlist.length; idx++){                
		 		var option = $("<option value="+qlist[idx]+">"+qlist[idx]+"분기</option>");
		 		$('#selectQu').append(option);
			}
		});
		
		//보고서 popup
		$('.analyreport-popup-wrap').find('.report').click(function() {
			Doc.btnReportLoad(this);
		});
	},
	resizeEvent : function(show) {
		if(show) {
			
			
		}
	},
	btnClose : function(pid, cid, uid, show) {

		var h = $(pid).height()<110?324:80;
		if(show!=undefined && show)
			h = 324;
			
		var display = h>110?'block':'none';
		var text = h>110?'닫기 ▲':'펼치기 ▼';
		
		$(cid).css('display', 'block');
		
		$(pid).stop().animate({
			height: h 
			}, {
			duration: 200,
			complete: function () {
				$(cid).css('display', display);
				$(uid).html(text);
			}
		});
	},
	btnResultClose : function(pid, show) {

		var h = $(pid).height()<110?'100%':0;
		if(show!=undefined && show)
			h = '100%';

		$(pid).stop().animate({
			height: h 
			}, {
			duration: 200,
			complete: function () {
			}
		});
	},
	btnShow : function(uid, show) {
		var display = show?'block':'none';
		$(uid).css('display', display);
	},
	btnAnalysis : function(uid) {
		//선택 항목 있는지 확인..
		var u = $('#rtabcontents .tab-content-trd').find('.selected');
		
		if(u.length != 1) {
			alert('상권 주소를 선택하십시오');
			return;	
		}

		//업종 선택 여부 확인
		var sel = $('#induM').find('.selected');
		if(sel.length !== 1) {
			alert('업종을 선택하세요');
			return;
		}
		
		//분석
		var params = {};
		params.trdId = $(u[0]).attr('trdarId');
		params.lfbtCd =  sel.attr('code');

		Api.call('get_anlTrd', params, true);
	},
	btnAnalyreport : function(uid) {
		this._trdId = $(uid).parent().find('input').attr('trdId');
		
		if(this._trdId == null || this._trdId == undefined) {
			alert('상권을 선택하세요');
			return;
		}
		
		//업종선택여부 확인
		var sel = $('#induM').find('.selected');
		if(sel.length !== 1) {
			alert('업종을 선택하세요');
			return;
		}
		
		this._lfbtCd = sel.attr('code');
		
		$('.analyreport-popup-wrap').css('display', 'flex');
	},
	btnReportLoad : function(uid) {		
		let index = parseInt($(uid).attr("value"));
		
		$('.analyreport-popup-wrap').css('display', 'none');
		
		var url = '../trdarea/analyQuReport.do';
		
		if (index === 0) {
			// AI 리포트 - 요약
			url = '../trdarea/commDistAnalysisSummaryReport.do';
		} else if (index === 1) {
			// AI 리포트 - 상세
			url = '../trdarea/commDistAnalysisDetailReport.do';
		} else if (index === 2) {			
			//분기 간략보고서
			url = '../trdarea/analySimplyQuReport.do';
		} else if (index === 3) {
			//월 간략보고서			
			url = '../trdarea/analySimplyMnReport.do';
		} else if (index === 4) {
			//분기 종합보고서		
			url = '../trdarea/analyQuReport.do';
		} else if (index === 5) {
			//월 종합보고서	
			url = '../trdarea/analyMnReport.do';
		} else {
			return;
		}

		$('#mapReportModal').fadeIn();
		$('#mapReportModal').load(url);
	},
	btnCompareReport : function() {
		//상권비교 호출
		var input = $('.side-content-wrap').find('.areakeep').find('input');
		
		var trdId = [];
		for(var n=0; n<input.length; n++) {
			if($(input[n]).val() != '') {
				trdId.push($(input[n]).attr('trdId'));
			}
		}

		if(trdId.length<=0) {
			alert('비교상권을 선택하세요');
			return;
		}
		
		var sel = $('#induM').find('.selected');
		if(sel.length !== 1) {
			alert('업종을 선택하세요');
			return;
		}
		
		var params = {};
		for(var n=0; n<trdId.length; n++) {
			if(n==0) {
				params.trdId1 = trdId[n];
			}
			else if(n==1) {
				params.trdId2 = trdId[n];
			}
			else if(n==2) {
				params.trdId3 = trdId[n];
			}
		}
		
		params.svcIndutyCdM = sel.attr('code');
		Api.call('getTrdComp', params, true);
	},
	btnCompare : function(show) {
		Func.openSingleRepo();
	},
	btnCloseRepo : function(show) {
		if(show) {
			if(ReportUI.isdisplay()) {
				ReportUI.fold(false);
			}
			
			this.sr.display(true);
			this.sr.fold(true);
		}
		else {
			this.sr.display(false);

			if(ReportUI.isdisplay()) {
				ReportUI.fold(true);
			}
		}
	},
	btnAddressSearch : function() {
		
		var keyword = $("#address").val();
		if(keyword == '') {
			alert('주소 혹은 장소를 입력하세요');
			return;
		}
		
		var page = 1;
		
		$('#tabcontents').find('div .tab-content-address-wrap').empty();
		
		Func.placPlacesSearchCB(keyword, page);
		Func.placAddressSearchCB(keyword, page);
		
		var uid = $('.side-content-wrap > .search .close');
		$(uid).css('display', 'flex');
		
		Doc.btnClose('#searchbox', '#addresscontent', uid, true);
	},
	btnSearch : function() {
		//업종 선택 여부 확인
		var sel = $('#induM').find('.selected');
		if(sel.length !== 1) {
			alert('업종을 선택하세요');
			return;
		}
		
		//검색조건 선택여부 확인
		var params = {};
		var chkSum = 0;
		
		//opt 초기값
		var c = $('#selchoice > div').eq(1).find('input');
		
		// 닫혀있거나 검색 조건 설정하지 않았을 경우 '점포 수'가 default (jsp - checked)
		for(var n=0; n<c.length; n++) {
			params['opt'+(n+1)] = $(c[n]).is(":checked")?'1':'0';
		}
			
		var h = $('#selchoice').height();
		if(h > 100) {
			//조회조건..
			if($('#selchoice > div').eq(1).find('input:checked').length>3) {
				alert('최대 3개까지 선택 할 수 있습니다');
				return;
			}
		}
		
		// 선택 조건 0 개시 예외처리
		for(var n=0; n<6; n++) {
			chkSum += parseInt(params['opt'+(n+1)]);
		}
		if(chkSum == 0) { alert('선택 조건을 한 개 이상 체크해주세요 '); return; }
		
		
		//기준 분기
		var s = $('#selchoice > div').eq(0).find('select');
		params.stdrYyCd = $(s[0]).val();
		params.stdrQuCd = $(s[1]).val();
			
		params.sggCd = $('#sglist').val();
		params.dongCd = $('#sgdlist').val();
		params.lfbtCd = sel.attr('code');
		
		//검색결과 활성화..
		Doc.btnResultClose('#resultbox', true);
		
		//호출
		Api.call('getRnkTrdList', params);
	},
	btnChoiceSlide : function(uid, pid) {
		var h = $(pid).height();

		if(h > 50) {
			$(pid).stop().animate({
				height: 30
				}, {
				duration: 200,
				complete: function () {
					$(uid).html('▼');
				}
			});
		}
		else {
			$(pid).stop().animate({
				height: '100%'  
				}, {
				duration: 200,
				complete: function () {
					$(uid).html('▲');
				}
			});
		}
	},
	btnAreaPopupAction : function(action) {
		if(action == 'report') {
			
		}
		else if(action == 'save') {
			
		}
		else if(action == 'delete') {
			
		}
		else {
			this.btnHide('#areapopup');
		}
	},
	btnHide : function(uid) {
		$(uid).fadeOut();
	},
	btnAddressSelect : function(uid) {
		$(uid).parent().parent().parent().find('.tab-content-address-wrap > div').removeClass('selected');
		$(uid).addClass('selected');
		
		var x = $(uid).attr('x');
		var y = $(uid).attr('y');
		
		Gis_Link.moveXyMark(y, x);
		
	},
	tabSelected : function(nid, tabid, contentid) {
		var tabidx = $('#reporttab').find('.tabselected').index();
		var idx = $('#subreporttab').find('.tabselected').index();

	},
	btnTableSpan : function(uid) {
		var fc = $(uid).parent().attr('fc');
		
		//class remove
		$(uid).parent().parent().parent().find('tr').removeClass('highlite');
		$(uid).parent().parent().addClass('highlite');
		
		//chart 새로고침
		var index = $(uid).parent().parent().index();
		View[fc](index);
	},
	btnAreakeepClose : function(uid) {
		$(uid).parent().find('input').val('');
	},
	btnTrdAddressSelect : function(uid) {
		$('#rtabcontents .tab-content-trd').children('div').removeClass('selected');
		$(uid).addClass('selected');
		
		//gis 상권 이동
		Gis_Link.selectTrdarInfoById($(uid).attr('trdarid'));
	},
	btnAnalyreportClose : function() {
		$('.analyreport-wrap').fadeOut();
	},
	//gis연계 상권 보고서
	btnAnalyreportView : function(trdId) {
		this._trdId = trdId;
		
		//업종선택여부 확인
		var sel = $('#induM').find('.selected');
		if(sel.length !== 1) {
			alert('업종을 선택하세요');
			return;
		}
		
		this._lfbtCd = sel.attr('code');
		
		$('.analyreport-popup-wrap').css('display', 'flex');
	},
	//분석 영역 gis연계
	insertTrdInfo: function(trdId, wtk, trdName) {
		var input = $('.side-content-wrap').find('.areakeep').find('input');
		
		var result = false;
		for(var n=0; n<input.length; n++) {
			if($(input[n]).val() == '') {
				$(input[n]).attr('trdId', trdId);
				$(input[n]).attr('wtk', wtk);
				$(input[n]).val(trdName);
				result = true;
				break;
			}
		}
		
		if(!result) {
			alert('분석영역 보관은 최대 3개입니다');
		}
	},
}

$(document).ready(function() {
	Doc.load();
});