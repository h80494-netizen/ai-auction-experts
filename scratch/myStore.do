
	
	
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta http-equiv="Content-Security-Policy"
	content="upgrade-insecure-requests" />
<title>경기도 상권분석지원 서비스</title>

<link rel="stylesheet" type="text/css"
	href="../../../pubcss/common/layout.css">
<link rel="stylesheet" type="text/css" href="../../../pubcss/reset.css">
<link rel="stylesheet" type="text/css" href="../../../pubcss/common/common.css">
<link rel="stylesheet" type="text/css" href="../../../pubcss/map/common.css">
<link rel="stylesheet" type="text/css" href="../../../pubcss/map/xeicon.min.css">

<script src="../../../js/lib/jquery-1.12.4.min.js"></script>
<script src="../../../js/lib/util.js"></script>
<script src="../../../js/api/apiService.js"></script>
<script src="../../../js/common/common.js"></script>
<script src="../../../js/map/commonui.js"></script>
<script src="../../../js/gmr/common/common.js"></script>

<!-- swiper -->
<link href="../../../pubcss/swiper/swiper.css" rel="stylesheet">
<script src="../../../js/swiper/swiper.min.js"></script>


<style>
.analyreport-popup-wrap {
	display: flex;
	gap: 8px;
}

.report {
	cursor: pointer;
	padding: 8px 5px;
	border: 1px solid #7EDDC8;
	border-radius: 8px;
	background: linear-gradient(to bottom, #B9F1E4 0%, #7EDDC8 100%);
	font-weight: normal;
	color: #004C3A;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	transition: all 0.25s ease;
}

.report:hover {
	background: linear-gradient(to bottom, #7EDDC8 0%, #34C6A3 100%);
	border-color: #34C6A3;
	transform: translateY(-2px);
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.report.active {
	background: linear-gradient(to bottom, #34C6A3 0%, #1E9E83 100%);
	color: #fff;
	border-color: #1E9E83;
	box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>


<!-- report popup -->
<link rel="stylesheet" type="text/css"
	href="../../../pubcss/reportPopup/reportPopup.css">
<script src="../../../js/reportPopup/reportPopup.js"></script>

<!-- chart -->
<link rel="stylesheet" href="../js/toastui/toastui-chart.min.css" />
<script src="../../../js/toastui/toastui-chart.min.js"></script>

<link rel="stylesheet" type="text/css" href="../../../pubcss/map/mystore/mystore.css?ver=202604080000">
<script src="../../../js/map/mystore/mystore.js?ver=202604090000"></script>
</head>
<!-- 구글 애널리틱스 -->
<!-- favicon link -->
<link rel="shortcut icon" type="image/png/ico" href="/images/icon/favicon.ico">

<!-- Google tag (gtag.js) -->
<script async
	src="https://www.googletagmanager.com/gtag/js?id=G-5WT2XJMPB5"></script>
<script>
	window.dataLayer = window.dataLayer || [];

	function gtag() {
		dataLayer.push(arguments);
	}

	gtag('js', new Date());
	gtag('config', 'G-5WT2XJMPB5');
	
/* 	
	function get_ga_clientid() {
		  var cookie = {};
		  document.cookie.split(';').forEach(function(el) {
		    var splitCookie = el.split('=');
		    var key = splitCookie[0].trim();
		    var value = splitCookie[1];
		    cookie[key] = value;
		  });
		return cookie["_ga"].substring(6);
	}
	 */
	//console.log(get_ga_clientid());
	
</script>



<div class='map3d-wrap layout-3d-wrap' id='layout3d'>
	<!-- loading bar 1 -->	
	 
<!DOCTYPE html>	
	
	
	
	<script>
		var roleCd; //Gis_Tool.js에서 공통으로 사용됨. 2025.01.07	
		$(document).ready(function() {
			roleCd = ",ROLE_READY";
			
			//roleCd = ",ROLE_GBSA,ROLE_GMRA";//2025.02.13 황재호 과장님 요청건 개발계 적용분
			
			var authCd = "";
			var mbrId = "guest";
			var mbrNm = "게스트";
			$("#mbrNm").html(mbrNm);
			
			if(mbrId == '' || mbrId == null || mbrId == 'undefined') {				
				leftMenuUI.login("bigsale"); //통큰세일 추가 //강제로 guest 정보를 셋팅 해줘야함.//종료 후 주석 원복
				//leftMenuUI.loginPopup(".loginpopup-wrap");	
			} else {
				leftMenuUI.setMenu(roleCd,3,authCd);
			}
		});
	</script>

	<!-- GNB -->
	<div class="left-wrap">
		<div class="left-menu leftNav" id="nav">
			<ul class="top_menu">

<!-- 					<div><img src="../../../images/map/ic_logo.png"></div> -->
<!-- 				</li> -->
				<!-- commonui.js 에서 조건부 렌더링 처리하므로 주석 처리 -->
				
			</ul>
			<ul class="bottom_menu">
				<!--
				<li>
					<div onclick="location.href='../../listSurveyUser.do'">
						<img src="../../../images/map/ic_btn_research.png">
						<div>리서치</div>
					</div>
				</li>
				-->
				<li>
					<div onclick="/help/getGuide.json">
						<img src="../../../images/map/ic_btn_help.png">
						<div>도움말</div>
					</div>
				</li>
			</ul>
		</div>
		<!-- 로그인 팝업 -->
	</div>
	<div style="display:none" class="loginpopup-wrap" id="loginpopup">
		<div class="loginpopup">
			<div class="logintitle">경기도 상권영향분석시스템</div>
			<div class="logintext">간편 로그인으로 시작하세요</div>
			<div class="loginbutton-wrap"><div onclick="leftMenuUI.login('guest')">비회원</div><div onclick="leftMenuUI.login('member')">회원</div></div>
			<div class="useage"><div onclick="leftMenuUI.join()">회원가입하러 가기&nbsp;<img src="../../../images/main/ic_signup.png"></div><div>이용안내</div></div>
		</div>
	</div>
	<!-- GNB : end -->
	
	<!-- 3d -->	
	<div class='map-wrap' id='map-wrap-3d'>		
		
		<div id='divide1' class='divide' style="position: relative; z-index: 10;">
			<div class="loadlayerMap_3D_1 loadlayer" style="display: none;"><div class="loader"></div></div>
			<div id='divGisSearch_3D_1' class='side-wrap'></div>
			<div id='divGisMap_3D_1' class="cls3dmap map-area"></div>
			<div id='divGisBtn_3D_1'  class='rightbutton-wrap' name='pos' style='top:30px; z-index: 1'></div>
			<div id='divGisLegend_3D_1' class='rightlegend-wrap'>
				<div style="width:100%; height: 100%;">
					<span style='background-color:#D5D5D5;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>
					<span style='background-color:#FAED7D;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>
					<span style='background-color:#FFBB00;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>
					<span style='background-color:#E0844F;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>
					<span style='background-color:#CC3D3D;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>
				</div>
			</div>
		</div>		 
		
		<div id='divide2' class='divide' style="display: none; position: relative; z-index: 11; border:1px blue;">
			<div class="loadlayerMap_3D_2 loadlayer" style="display: none"><div class="loader"></div></div>
			<div id='divGisSearch_3D_2' class='side-wrap3d' style="position:absolute;"></div>
			<div id='divGisMap_3D_2' class="cls3dmap map-area"></div>
			<div id='divGisBtn_3D_2'  class='rightbutton-wrap' name='pos' style='top:30px; z-index: 2'></div>
		</div>
		
		<div id='divide3' class='divide' style="display: none; position: relative; z-index: 12; border:1px blue;">
			<div class="loadlayerMap_3D_3 loadlayer" style="display: none"><div class="loader"></div></div>
			<div id='divGisSearch_3D_3' class='side-wrap'></div>
			<div id='divGisMap_3D_3' class="cls3dmap map-area"></div>
			<div id='divGisBtn_3D_3'  class='rightbutton-wrap' name='pos' style='top:30px; z-index: 3'></div>
		</div>
		
		<div id='divide4' class='divide' style="display: none; position: relative; z-index: 13; border:1px blue;">
		<div class="loadlayerMap_3D_4 loadlayer" style="display: none"><div class="loader"></div></div>
			<div id='divGisSearch_3D_4' class='side-wrap3d' style="position:absolute;"></div>
			<div id='divGisMap_3D_4' class="cls3dmap map-area"></div>
			<div id='divGisBtn_3D_4'  class='rightbutton-wrap' name='pos' style='top:30px; z-index: 4'></div>
		</div>
	</div>
</div>

<script>	
	$(document).ready(function() {
		//3D에서 MAIN MENU 클릭시 EXIT FULL SCREEN
		$('.map3d-wrap .left-menu .top_menu > li').click(function() {
			Biz_Comm.objExitScreen();
		});	
	});
</script>
<body>
	<!-- wrap// -->
	<div class="wrap">
		<!-- 추가 -->
		<input type='hidden' id='hdMapKey' value='divGisMap' />
		<!-- loading -->
		<div class="loadlayer">
			<div class="loader"></div>
		</div>
		<!-- //loading -->
		<!-- left 메뉴 -->
		 
<!DOCTYPE html>	
	
	
	
	<script>
		var roleCd; //Gis_Tool.js에서 공통으로 사용됨. 2025.01.07	
		$(document).ready(function() {
			roleCd = ",ROLE_READY";
			
			//roleCd = ",ROLE_GBSA,ROLE_GMRA";//2025.02.13 황재호 과장님 요청건 개발계 적용분
			
			var authCd = "";
			var mbrId = "guest";
			var mbrNm = "게스트";
			$("#mbrNm").html(mbrNm);
			
			if(mbrId == '' || mbrId == null || mbrId == 'undefined') {				
				leftMenuUI.login("bigsale"); //통큰세일 추가 //강제로 guest 정보를 셋팅 해줘야함.//종료 후 주석 원복
				//leftMenuUI.loginPopup(".loginpopup-wrap");	
			} else {
				leftMenuUI.setMenu(roleCd,3,authCd);
			}
		});
	</script>

	<!-- GNB -->
	<div class="left-wrap">
		<div class="left-menu leftNav" id="nav">
			<ul class="top_menu">

<!-- 					<div><img src="../../../images/map/ic_logo.png"></div> -->
<!-- 				</li> -->
				<!-- commonui.js 에서 조건부 렌더링 처리하므로 주석 처리 -->
				
			</ul>
			<ul class="bottom_menu">
				<!--
				<li>
					<div onclick="location.href='../../listSurveyUser.do'">
						<img src="../../../images/map/ic_btn_research.png">
						<div>리서치</div>
					</div>
				</li>
				-->
				<li>
					<div onclick="/help/getGuide.json">
						<img src="../../../images/map/ic_btn_help.png">
						<div>도움말</div>
					</div>
				</li>
			</ul>
		</div>
		<!-- 로그인 팝업 -->
	</div>
	<div style="display:none" class="loginpopup-wrap" id="loginpopup">
		<div class="loginpopup">
			<div class="logintitle">경기도 상권영향분석시스템</div>
			<div class="logintext">간편 로그인으로 시작하세요</div>
			<div class="loginbutton-wrap"><div onclick="leftMenuUI.login('guest')">비회원</div><div onclick="leftMenuUI.login('member')">회원</div></div>
			<div class="useage"><div onclick="leftMenuUI.join()">회원가입하러 가기&nbsp;<img src="../../../images/main/ic_signup.png"></div><div>이용안내</div></div>
		</div>
	</div>
	<!-- GNB : end -->

		<!-- side content -->
		<div class="side-wrap">
			<!-- 좌우 슬라이드 버튼 -->
			<div id="btnlefthandle" class="side-left-handle"></div>

			<!-- side content -->
			<div class="side-content-wrap">
				<!-- 내 점포 분석 -->
				<div class="search" id="searchbox">
					<div>내 점포 분석</div>
					<input id="address" type="text" placeholder='주소, 장소' /><img
						src="../../../images/map/btn_side_search.png"
						onclick="Doc.btnAddressSearch()">
					<div class="address-wrap" id="addresscontent">
						<div class="tab-wrap" id="tabs">
							<div
								onclick="ReportUI.tabselected(this, '#tabs', '#tabcontents')"
								class="tabselected">전체</div>
							<div
								onclick="ReportUI.tabselected(this, '#tabs', '#tabcontents')">
								주소</div>
							<div
								onclick="ReportUI.tabselected(this, '#tabs', '#tabcontents')">
								장소</div>
						</div>
						<div class="tab-content-wrap" id="tabcontents">
							<div style="display: block;">
								<div class="text">검색 결과가 존재하지 않습니다</div>
								<div class="tab-content-address-wrap"></div>
								<div class="text">검색 결과가 존재하지 않습니다</div>
								<div class="tab-content-address-wrap"></div>
							</div>
							<div>
								<div class="text">검색 결과가 존재하지 않습니다</div>
								<div class="tab-content-address-wrap"></div>
							</div>
							<div>
								<div class="text">검색 결과가 존재하지 않습니다</div>
								<div class="tab-content-address-wrap"></div>
							</div>
						</div>
					</div>
					<!-- 닫기 버튼 -->
					<div class="close"
						onclick="Doc.btnClose('#searchbox', '#addresscontent', this);">닫기
						▲</div>
				</div>
				<div>
					<div class="subtext">생활밀접업종 선택</div>
					<div class="induL-wrap" id="induL">
						<div code="0" class="selected">전체</div>
						<div code="1">소매업</div>
						<div code="2">서비스업</div>
						<div code="3">음식점</div>
					</div>
					<div class="induM-wrap">
						<div id="induM"></div>
					</div>

					<!-- 사용자 영역선택 -->
					<div class="subtext">사용자 영역 선택</div>
					<div class="userarea-wrap">
						<div>
							<div id='divUserCircle' class="userdraw">반경</div>
							<div id='divUserPolygon' class="userdraw">다각형</div>
						</div>
						<div>
							<div class="subtext">검색지점</div>
							<select id='select-dist'>거리지정
							</select>
							<div style="height: 5px;">&nbsp;</div>
							<input id='txt-dist' type='text'
								style="width: 228px; display: none;" />
						</div>
						<div class="analysis" onclick="Doc.btnAnalysis()">사용자선택영역 분석하기</div>
					</div>

					<!-- 20231031 추가 -->
					<hr class="gline">
					<input type="checkbox" class="moretoggle" id="moretoggle"><label
						for="moretoggle">더보기(비교분석)</label>
					<!-- 업종영역/상권비교 탭 //-->
					<div class="tabs">
						<input id="tab1" type="radio" name="tab_item" checked> <label
							class="tab_item" for="tab1">업종비교</label> <input id="tab2"
							type="radio" name="tab_item"> <label class="tab_item"
							for="tab2">영역비교</label>
						<div class="tab_content" id="tab1_content">
							<!-- 업종영역 -->
							<div class="subtext">비교할 업종(더블클릭)을 추가해 주세요(최대3개)</div>
							<div class="induarea-wrap">
								<div>
									<input type="text" readonly="">
									<div onclick="Doc.induareaClose(this)"></div>
								</div>
								<div>
									<input type="text" readonly="">
									<div onclick="Doc.induareaClose(this)"></div>
								</div>
								<div>
									<input type="text" readonly="">
									<div onclick="Doc.induareaClose(this)"></div>
								</div>
								<div class="inducompare" onclick="Doc.btnUpjongCompareReport()">업종비교<br><br>분석하기</div>
							</div>
						</div>
						<div class="tab_content" id="tab2_content">
							<!-- 상권비교 -->
							<!--  -->
							<!-- 분석영역 보관함 -->
							<div class="areakeeptitle">지도에서 사용자 영역을 추가해 주세요(최대3개)</div>
							<div class="areakeep">
								<div class="input_wrap">
									<input type="text" readonly />
									<div onclick="Doc.btnAreakeepClose(this)"></div>
								</div>
								<div onclick="Doc.btnAnalyreport(this)">상권보고서</div>
							</div>
							<div class="areakeep">
								<div class="input_wrap">
									<input type="text" readonly />
									<div onclick="Doc.btnAreakeepClose(this)"></div>
								</div>
								<div onclick="Doc.btnAnalyreport(this)">상권보고서</div>
							</div>
							<div class="areakeep">
								<div class="input_wrap">
									<input type="text" readonly />
									<div onclick="Doc.btnAreakeepClose(this)"></div>
								</div>
								<div onclick="Doc.btnAnalyreport(this)">상권보고서</div>
							</div>
							<!-- 상권비교 -->
							<div class="storecompare" onclick="Doc.btnTrdCompareReport()">사용자영역 비교분석하기</div>
							<!--  -->
							<div class="notice">
								<label>동일업종</label>으로 상권비교가 가능합니다
							</div>
						</div>
					</div>
					<!--// 업종영역/상권비교 탭 -->
					<!-- 20231031 추가 -->


				</div>
				<!--// 창업온도 -->

			</div>
			<!-- //side content -->
		</div>

		<!-- map area -->
		
    
<!-- roadview --> 
<div class="rvview" 
	style="width: 100%; height: 100%; top:0px; left:0px; position:absolute; display: none; z-index:111;">
	<div id='divRvViewer' class='map_box' style="width:100%; height:100%; z-index: 1111;"></div>
	<img alt="close" style="z-index:11111; cursor: 'pointer'; 
		 position:absolute; float: right; top: 20px; right: 20px;" class='rvclose' 
		 src="/images/gis/icon_close2.png">
</div>
		<div class="map-wrap">
			
<!DOCTYPE html>
<html>	
<script>var selectedValue = 300;</script> 			
<div class="map-area" id='divGisMap'></div>

<!-- 왼쪽상단 버튼 -->
<div class="leftbutton-wrap1">
	<div id='mapbutton' class="button"></div>
	<div class="h-menu">
		<div>
			<div>경기도</div>
			<div class="sg"><span></span>
				<div>
				</div>
			</div>
			<div class="sgd"><span></span>
				<div>
				</div>
			</div>
		</div>
	</div>
	<div class="v-menu">
		<div></div>
		<div id='btnMapTool_1'>
			<img src="../images/map/ic_map_area.png">
			상권영역
			<div>
				<div class="h-button" id='divDetailCode_1'>						
				</div>
			</div>
		</div>
		<div id='btnMapTool_2'>
			<img src="../images/map/ic_map_store.png">
			점포이력
			<div>
				<div class="h-button" id='divDetailCode_2'>
				</div>
			</div>
		</div>
		<div id='btnMapTool_3'>
			<img src="../images/map/ic_map_bld.png">
			시설물
			<div>
				<div class="h-button" id='divDetailCode_3'>
					<!-- 
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_1'>관공서</div>
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_2'>금융</div>
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_3'>병원</div>
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_4'>학교</div>
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_5'>유흥점</div>
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_6'>문화</div>
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_7'>호텔</div>
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_8'>지하철역</div>
					<div class='btnMapDetailTool btnMapDetailTool_3' id='3_9'>버스<br>정류장</div>
					 -->
				</div>
			</div>
		</div>
		<div id='btnMapTool_4'>					
			<img src="../images/map/ic_map_personroad.png">
			상존인구<br>(길단위)
			<div>
				<div class="box">
					<div class="select-wrap">
						<div>요일 
							<select id='selDay_road' class='selroad'></select>
						</div>
						<div>연령대 
							<select id='selAge_road' class='selroad'></select>
						</div>
						<div>시간대 
							<select id='selTime_road' class='selroad'></select>
						</div>
					</div>
					<div class="bustle-wrap">
						<div>적음<br>0</div>
						<!-- <div><img src="../images/map/ic_map_bustle.png"><span>일 평균/22.12 기준</span></div> -->
						<div><img src="../images/map/ic_map_bustle.png"><span>일 평균/23.09 기준</span></div> 
						<div>많음<br>9</div>
					</div>
				</div>
			</div>
		</div>
		<div id='btnMapTool_5'>					
			<img src="../images/map/ic_map_personbld.png">
			상존인구<br>(건물단위)
			<div>
				<div class="box">
					<div class="select-wrap">
						<div>요일 
							<select id='selDay_bldg' class='selbldg'></select>
						</div>
						<div>연령대 
							<select id='selAge_bldg' class='selbldg'></select>
						</div>
						<div>시간대 
							<select id='selTime_bldg' class='selbldg'></select>
						</div>
					</div>
					<div class="bustle-wrap">
						<div>적음<br>0</div>
						<!-- <div><img src="../images/map/ic_map_bustle.png"><span>일 평균/22.12 기준</span></div> -->
						<div><img src="../images/map/ic_map_bustle.png"><span>일 평균/23.09 기준</span></div>
						<div>많음<br>9</div>
					</div>
				</div>
			</div>
		</div>
		<div id='btnMapTool_6'>
			<img alt="heatmap_loading" src="/images/img_loading2.gif" id='btnMapTool_Loading6'
						style='position:absolute;  margin-left:10px; width:30px;height:30px; display: none;'/>
			<img src="../images/map/ic_map_info.png" />
			상권정보<br>(히트맵)
			<div>
				<div class="h-button">
				<!-- 
					<div class='btnMapDetailTool btnMapDetailTool_6' id='6_fpop'>길단위<br>유동인구</div>
				 -->
					<div class='btnMapDetailTool btnMapDetailTool_6' id='6_rpop'>주거인구</div>
					<div class='btnMapDetailTool btnMapDetailTool_6' id='6_wpop'>직장인구</div>
				</div>
			</div>
		</div>
		<div id='btnMapTool_7'>
			<img src="../images/map/ic_map_pay.png">
			경기도<br>지역화폐
			<div>
				<div class="h-button" id='divDetailCode_7'>
					<!-- 
					<div class='btnMapDetailTool btnMapDetailTool_7' id='7_1'>전체</div>
					<div class='btnMapDetailTool btnMapDetailTool_7' id='7_2'>외식업</div>
					<div class='btnMapDetailTool btnMapDetailTool_7' id='7_3'>서비스업</div>
					<div class='btnMapDetailTool btnMapDetailTool_7' id='7_4'>소매업</div>
					 -->
				</div>
			</div>
		</div>
		<div id='btnMapTool_8'>
			<img src="../images/map/ic_map_store.png">
				프랜차이즈
			<div>
				<div class="h-button" id='divDetailCode_8'>
					<!-- 
					<div class='btnMapDetailTool btnMapDetailTool_8' id='8_1'>전체</div>
					<div class='btnMapDetailTool btnMapDetailTool_8' id='8_2'>선택업종</div>
					<div class='btnMapDetailTool btnMapDetailTool_8' id='8_3'>외식업</div>
					<div class='btnMapDetailTool btnMapDetailTool_8' id='8_4'>서비스업</div>
					<div class='btnMapDetailTool btnMapDetailTool_8' id='8_5'>소매업</div>
					 -->
				</div>
			</div>
		</div>
		<!-- 통큰세일 이벤트 기간 노출 -->
		<!-- 종료 후 주석-->
	    <!-- 
	    <div id='btnMapTool_9'>
			<img src="../images/map/ic_map_bigsale.png">
			통큰세일
			<div>
				<div class="h-button" id='divDetailCode_9'>
				<div class='btnMapDetailTool btnMapDetailTool_9' id='9_1'>전체</div>					
				</div>
			</div>
		</div> 
		-->
		
	</div>			
</div>
<!-- //왼쪽 상단 버튼 -->

<div class="ajax_area" data-url="../../map/common/rightmenu.html">
	<!-- 오른쪽 지도 메뉴 -->
	<div class="rightbutton-wrap" name="pos">				
	  <div class="map-button rightmenu_open" id='mapToolList'>
	    <img src="../../../images/map/icon_bars.png">
	  </div>
	  <div class="map_button_list">
	  	<!-- 
	  	<div class="map-button" onclick="Gis_Link.selectedFeatureWKT()" id='curloc'>
	      <img src="../../../images/map/ic_map_pos_1.png">
	      <div class="tooltip">테스트</div>
	    </div>
	     -->
	    <div class="map-button clsBtnLocation_2D" id='curloc'>
	      <img src="../../../images/map/ic_map_pos_1.png">
	      <div class="tooltip">현위치 이동</div>
	    </div>
	    <div class="map-button clsBtnBasicLayer_2D" id='backmap'>
	      <img src="../../../images/map/ic_map_pos_2.png">
	      <div class="tooltip">배경지도</div>
	    </div>
	    <div class="map-button clsBtnTerrain_2D" id='terrain'>
	      <img src="../../../images/map/ic_map_pos_3.png">
	      <div class="tooltip">지형도</div>
	    </div>
	    <div class="map-button clsBtn3DMap_2D">
	      	<img src="../../../images/map/ic_map_pos_4.png">
	      	<div class="tooltip" style="z-index:1">3D지도</div>			      	
	      	<div id='mapBtn3DExtra' class='map-button-extra-2d' style="display:none; z-index:2;">
	      		<ul class=''
	      			style='display: flex; border: solid 1px #0068bd; background-color: #e5f8ff; font-size: 11px; color: #0068bd;'>
	      			<li onclick='Gis_Tool.move3DMapPage("compare")' data-section='1' class='now mapSectionBtn'
	      			style='width: 55px; line-height: 36px; text-align: center; border-left: solid 1px #0068bd; cursor: pointer;'
	      			>비교분석</li>
	      			<li onclick='Gis_Tool.move3DMapPage("location")' data-section='2' class='now mapSectionBtn'
	      			style='width: 55px; line-height: 36px; text-align: center; border-left: solid 1px #0068bd; cursor: pointer;'
	      			>입지분석</li>
	      		</ul>
	    	</div>
	    </div>
	    <div class="map-button clsBtnRoadview_2D" id='roadview'>
	      <img src="../../../images/map/ic_map_pos_5.png">
	      <div class="tooltip">로드뷰</div>
	    </div>
	    <div class="map-button clsBtnZoomin_2D" id='zoomin'>
	      <img src="../../../images/map/ic_map_pos_6.png">
	      <div class="tooltip">지도확대</div>
	    </div>
	    <div class="map-button clsBtnZoomout_2D" id='zoomout'>
	      <img src="../../../images/map/ic_map_pos_7.png">
	      <div class="tooltip">지도축소</div>
	    </div>
	    <div class="map-button clsBtnDist_2D" id='dist'>
	      <img src="../../../images/map/ic_map_pos_8.png">
	      <div class="tooltip">거리</div>
	    </div>
	    <div class="map-button clsBtnArea_2D" id='area'>
	      <img src="../../../images/map/ic_map_pos_9.png">
	      <div class="tooltip">면적</div>
	    </div>
	    <div class="map-button clsBtnClear_2D" id='clear'>
	      <img src="../../../images/map/ic_map_pos_10.png">
	      <div class="tooltip">초기화</div>
	    </div>
	  </div>
	</div>
	
	<!-- 오른쪽 지도 슬라이드 -->
	<div class="rightslide-wrap" id="mapslidelayer" style='right: -184px;'>
		<div class="rightslide-content-wrap">
			<div class="resulttext">상세이력 <label id='lblStoreDetailCnt'></label>건 조회</div>
			<div class="content" style='overflow-y:auto'>
				<img alt="detail_loading" id='map_detail_loading' style="display:none; position: absolute; margin-left: 30px; margin-top: 20px;" 
					 src="../images/gis/circle_loading.gif" />					
				<div id='divStoreDetail'>
				</div>
			</div>
		</div>
		<!-- 좌우 슬라이드 버튼 -->
		<div id="btnmapslidehandle" class="side-right-handle" style="top:0px;"></div>
	</div>
	<!-- //오른쪽 지도 슬라이드 -->
	
	<!-- 오른쪽 지도 메뉴 : end -->
</div><!-- 오른쪽 지도 메뉴 부분 (추후 개발 시 삭제) -->

		
	<link rel="stylesheet" type="text/css" href="/css/gis/custom.css">
	<!-- 추가 
	<link rel="stylesheet" type="text/css" href="../css/gis/style.css">
	<link rel="stylesheet" type="text/css" href="../css/gis/ol6.11.0.css">
	<link rel="stylesheet" type="text/css" href="../css/gis/ol-ext.css">
	-->

	<!-- gis start -->
	<!-- 
	 <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=e005882071b28ab151fb5cf1aeedae65&libraries=services"></script>
	-->
	<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey=6596115b1510b2b405aefc8ee34b2453&libraries=services"></script>
	
	<script src="/js/gis/lib/jsts/jsts.js"></script>
	<script src="/js/gis/lib/turf/turf.js"></script>
	<script src="/js/gis/lib/proj4js-2.4.3/dist/proj4.js"></script>
	<script src="/js/gis/lib/ol6.11.0/ol.js"></script>
	<script src="/js/gis/lib/ol-ext/ol-ext.js"></script>
	<!-- <script src="https://cdn.jsdelivr.net/npm/ol-ext@4.0.34/dist/ol-ext.js"></script>	 -->
	<!-- 
	<script src="https://openlayers.org/ol-cesium/olcesium.js"></script>
	<script src="https://cesium.com/downloads/cesiumjs/releases/1.90/Build/Cesium/Cesium.js"></script>
	  -->
	<script src="/js/gis/lib/cs1.83/Cesium.js"></script>
	<!--<script src="https://cdnjs.cloudflare.com/ajax/libs/cesium/1.83.0/Cesium.min.js"></script>	-->
	<script src="/js/gis/lib/ol-cesium-v2.13/olcesium.js"></script>
	<script src="/js/gis/lib/ol-dev.js?ver=20260408"></script>
	<script src="/js/gis/map/common/Biz_Comm.js"></script>
	<script src="/js/gis/map/common/Gis_Comm.js?ver=20251105"></script>
	<script src="/js/gis/map/common/Gis_Tool.js?ver=20251105"></script>
	<script src="/js/gis/map/common/Gis_Overlay.js"></script>
	<script src="/js/gis/map/common/Gis_Pop.js?ver=20251105"></script>
	<script src="/js/gis/map/common/Gis_SLD.js?ver=20250711"></script>
	<script src="/js/gis/map/common/Gis_Link.js"></script>
	<script src="/js/gis/map/common/Gis_Link_Event.js"></script>
	<script src="/js/gis/map/common/Gis_3D.js"></script>
	<script src="/js/gis/map/common/Gis_3D_UI.js"></script>
	<script src="/js/gis/map/common/Map_Btn_Comm.js"></script>
	<script>
		$(document).ready(function() {
			//기본 commonui이벤트 제거 (필수)
			$(document).off('click','.map-wrap .rightmenu_open');		
			$(document).off('click','.map_button_list .map-button');
			$(document).off('click','.mapSectionBtn');
			if($('.side-wrap').hasClass('noactive')) {
				$('.side-left-handle').trigger('click');
			}
			
			var mtype = 'mystore';
			Gis_Comm.getGisInfo().mtype = mtype;
			if(mtype == 'starttemp' || mtype == 'trdactivity' || mtype == 'tripactivity' || mtype == 'trdchange' ) {
				$('.leftbutton-wrap1').hide();
				$('.rightslide-wrap1').hide();			
			}else {
				$('.leftbutton-wrap1').show();
				Map_Btn.buttonEvent();				
				$('#mapbutton').trigger('click');
				//$('#btnmapslidehandle').hide();				
			}
			
			var mapId = $('#hdMapKey').val();
			Ol_Info_Com.getProjectManager().img.roadView = '/images/gis/map-pin.png';
			$('.rvclose').click(function() { $('.rvview').hide(); });
			Gis_Comm.initMap({mapId: mapId, divId: mapId, clickCallBack: function(e) {
				Gis_Comm.map2DClickEvent(e);	
				Gis_Link_Event.mapClickEvent(e);
			}, moveEndCallBack: function(params){ //{mapObj, event}
				Gis_Tool.moveEndEvent(params);	
				Gis_Link_Event.mapMoveEndEvent(params);
			}, moveStartCallBack: function(params) {
				Gis_Tool.moveStartEvent(params);
				//facility highlight 레이어 피처 unhighlight
				Gis_Comm.unselectHighlightFacFeature();
			}});		
			//$('.map-wrap .leftbutton-wrap .v-menu > div:nth-child(n+2) > div > .h-button > div').off('click');
			$('.map-wrap .leftbutton-wrap1 .v-menu > div:nth-child(n+2) > div > .h-button > div').click(function(e) {
				Gis_Tool.mapToolActive(this.id);
			});	
			if(mtype == 'trdarea' || mtype == 'myconsult' || mtype == 'mystore' || mtype == 'oldstore') {
				if(mtype == 'myconsult') {		
					Gis_Comm.mapZoomChangeEvent();
				}
				//상권정보 모두 visible(경기상권분석)
				Gis_Tool.mapToolActive("1_1");
				Gis_Tool.mapToolActive("1_2");
				Gis_Tool.mapToolActive("1_3");
				Gis_Tool.mapToolActive("1_4");
				Gis_Tool.mapToolActive("1_5");
				
				//통큰세일 url param 분기
				var promotion = '';
				if(promotion == 'bigsale'){Gis_Tool.mapToolActive("9_1");} //통큰세일 > 전체선택 >> 종료 후 주석
			}
			
			//지도조작도구 버튼 리스트
			$('#mapToolList').click(function() {Biz_Comm.btnMapToolAction();});
			//사이드
			$('.side-left-handle').click(function(){
				var mapObj   = Ol_Info_Com.getMapObj($('#hdMapKey').val());
				//사이즈 체크후 지도 사이즈  udpate
				var itvId = setInterval(function(){
					mapObj.updateSize();
					Gis_Comm.setAnalysisMapBtnLocation(); //분석버튼 위치세팅
					clearInterval(itvId);
				}, 150);				
			});
			
			//----사용자 영역선택 start--------------------------------		
			$('#divUserCircle').click(function(e){
				$('.userdraw').removeClass('active');
				$('#divUserCircle').addClass('active');
				$('#select-dist').prop('disabled', false);
				
				Ol_User_Draw_Ext.drawUserShape({mapId: $('#hdMapKey').val(),  radius: null,
												ids: { divDistId: 'select-dist', divCustomDistId: 'txt-dist' }, //custom dist radius정보 가져오기
												drawType: 'pointCircle',
												func: function(feature) { 
													$("#divUserCircle").removeClass("selected active");

													//click 이벤트와 중복되는 문제 (클릭보다 나중에 실행되야 함);
													var circleTimeId = setTimeout(function(){
														var mapId =  $('#hdMapKey').val();
														var vectorUserLayer = Ol_Layer_Comp.selectLayerByProps({mapId: mapId, prop: 'id', value: Ol_Info_Com.getProjectManager().name.layer.userDrawShape});
														var interaction = Gis_Comm.getUserDrawSelectInteraction(vectorUserLayer);
														interaction.getFeatures().clear();
														interaction.getFeatures().push(feature);
														var info = {
															nm: feature.props.text,
											        		featureId: feature.props.id,
											        		cnm : '사용자 영역',
											        		wkt : feature.props.wkt,
											        		area: feature.props.area.label, 
														}
														//info wkt 로 pwkt정보 조회
														var proj = Ol_Map_Comp.getProjection({mapId: $('#hdMapKey').val(), numyn: false});
														var geom = Ol_Geom_Com.wktToGeometry({wkt:info.wkt, src:proj, dest:proj});
														var arrCenter = turf.centerOfMass(turf.polygon(geom.getCoordinates())).geometry.coordinates;
														info.pwkt = 'POINT(' + arrCenter[0] + " " + arrCenter[1] + ')';
														if(feature.props.keyword.indexOf('draw,analysis,user') > -1){  //사용자 영역일 경우만
															feature.props.analysis = info;
														}
														Gis_Overlay.createAnalysisOverlay(info); 
														clearTimeout(circleTimeId);
													}, 150);																							
												},
												callBackOverlay: function(info) {
													if(info.close == 'Y') {													
														Gis_Overlay.removeOverlayByFId($('#hdMapKey').val(), info.featureId);
													}else {
														Gis_Overlay.createAnalysisOverlay(info);
														/*
														//info wkt 로 pwkt정보 조회
														var proj = Ol_Map_Comp.getProjection({mapId: $('#hdMapKey').val(), numyn: false});
														var geom = Ol_Geom_Com.wktToGeometry({wkt:info.wkt, src:proj, dest:proj});
														if(info.wkt.indexOf('MULTI') > -1) {
															geometry = turf.multiPolygon(geom.getCoordinates());
														}else {
															geometry = turf.polygon(geom.getCoordinates());
														}
														var arrCenter = turf.centerOfMass(geometry).geometry.coordinates;
														info.pwkt = 'POINT(' + arrCenter[0] + " " + arrCenter[1] + ')';
														if(!Ol_Util_Com.checkObjEmpty(info.feature) && 
															info.feature.props.keyword.indexOf('draw,analysis,user') > -1){ //사용자 영역일 경우만
															info.feature.props.analysis = info;
															info.feature.props.analysis.feature = null;
														}
														Gis_Overlay.createAnalysisOverlay(info);
														*/
													}
												}
											});
			});
			$('#divUserPolygon').click(function(e){
				$('.userdraw').removeClass('active');
				$('#divUserPolygon').addClass('active');
				$('#txt-dist').val('').hide();
				$('#select-dist option:eq(0)').prop('selected', true);
				$('#select-dist').prop('disabled', 'disabled');
				Ol_User_Draw_Ext.drawUserShape({mapId: $('#hdMapKey').val(),  radius: 0, drawType: 'polygon',
												func: function(feature) { //polygon draw end시 function  overlay생성
													//click 이벤트와 중복되는 문제 (클릭보다 나중에 실행되야 함);
													var polyTimeId = setTimeout(function(){					
														var mapId =  $('#hdMapKey').val();
														var vectorUserLayer = Ol_Layer_Comp.selectLayerByProps({mapId: mapId, prop: 'id', value: Ol_Info_Com.getProjectManager().name.layer.userDrawShape});
														var interaction = Gis_Comm.getUserDrawSelectInteraction(vectorUserLayer);
														interaction.getFeatures().clear();
														interaction.getFeatures().push(feature);
														var info = {
															nm: feature.props.text,
											        		featureId: feature.props.id,
											        		cnm : '사용자 영역',
											        		wkt : feature.props.wkt,
											        		area: feature.props.area.label,
														}
														//info wkt 로 pwkt정보 조회
														var proj = Ol_Map_Comp.getProjection({mapId: mapId, numyn: false});
														var geom = Ol_Geom_Com.wktToGeometry({wkt:info.wkt, src:proj, dest:proj});
														try {
															var arrCenter = turf.centerOfMass(turf.polygon(geom.getCoordinates())).geometry.coordinates;
															info.pwkt = 'POINT(' + arrCenter[0] + " " + arrCenter[1] + ')';
															if(feature.props.keyword.indexOf('draw,analysis,user') > -1){  //사용자 영역일 경우만
																feature.props.analysis = info;
															}
															Gis_Overlay.createAnalysisOverlay(info);
															Gis_Comm.setUserAreaSelectStyle();
														}catch (error) {
															Ol_Event_Comp.clearDrawEvent(mapId);
															alert("이벤트 충돌로 도형을 그리기에 실패하였습니다. 다시 시도해주시기 바랍니다.");
														}
														clearTimeout(polyTimeId);
													}, 150);
												},
												callBackOverlay: function(info) {
													if(info.close == 'Y') {													
														Gis_Overlay.removeOverlayByFId($('#hdMapKey').val(), info.featureId);
													}else {
														Gis_Overlay.createAnalysisOverlay(info); /// 팝업창 내용 넣는 곳
													}
												}
												/*
												callBackOverlay: function(info) {
													if(info.close == 'Y') {
														Gis_Overlay.removeOverlayByFId($('#hdMapKey').val(), info.featureId);
													}else {
														//info wkt 로 pwkt정보 조회
														var proj = Ol_Map_Comp.getProjection({mapId: $('#hdMapKey').val(), numyn: false});
														var geom = Ol_Geom_Com.wktToGeometry({wkt:info.wkt, src:proj, dest:proj});
														var geometry = null;
														if(info.wkt.indexOf('MULTI') > -1) {
															geometry = turf.multiPolygon(geom.getCoordinates());
														}else {
															geometry = turf.polygon(geom.getCoordinates());
														}
														var arrCenter = turf.centerOfMass(geometry).geometry.coordinates;
														info.pwkt = 'POINT(' + arrCenter[0] + " " + arrCenter[1] + ')';
														if(!Ol_Util_Com.checkObjEmpty(info.feature) && 
															info.feature.props.keyword.indexOf('draw,analysis,user') > -1){  //사용자 영역일 경우만
															info.feature.props.analysis = info;
															info.feature.props.analysis.feature = null;
														}
														Gis_Overlay.createAnalysisOverlay(info);	
													}
												}
												*/
											});
			});
			$('#select-dist').change(function(e) {
				if(Number(this.value) < 0) {
					$('#txt-dist').val('').show();	
				}else {
					$('#txt-dist').val('').hide();
				}
			});
			if(mtype == 'myconsult') {$('#2_select').hide();}			
		});
		//resize 도중 왼쪽 서치창 hide되는 문제 해결
		var chk3DMapTimeout = null;
		$(window).resize(function(){
			clearTimeout( chk3DMapTimeout );			
			chk3DMapTimeout = setTimeout(function() {				
				if($('.map3d-wrap').css('display') == 'block') { //3차원일경우
					//사이즈가 풀사이즈가 아닐경우 풀사이즈로
					//Biz_Comm.objFullScreen();
					$('#divGisSearch_3D_1').removeClass('noactive');
					Gis_3D_UI.searchFormView($('#btnlefthandle_3D_1'), 'btnlefthandle_3D_1', 'divGisSearch_3D_1', true);
					$('#divGisSearch_3D_3').removeClass('noactive');
					Gis_3D_UI.searchFormView($('#btnlefthandle_3D_3'), 'btnlefthandle_3D_3', 'divGisSearch_3D_3', true);					
				}else {
					//2차원 
					var mapId = $('#hdMapKey').val();
					if(!Ol_Util_Com.checkObjEmpty(mapId)) {						
						var mapObj = Ol_Info_Com.getMapObj(mapId);
						mapObj.updateSize();
						Gis_Comm.setAnalysisMapBtnLocation(); //분석버튼 위치세팅
					}
				}
			}, 200);
		});
		
		function drawUserShapeCustom(x, y, radius) {
			if(x !== 0 && y !== 0) {
				var mapId   = $('#hdMapKey').val(); 
				
				var projCode = Ol_Map_Comp.getProjection({mapId: mapId, numyn: false}); 
			    var coord    = ol.proj.transform([x, y], 'EPSG:4326', projCode); 
			    
				Ol_User_Draw_Event.callBackUserDrawStartCustom(mapId, coord, radius);
			}
		}

	</script>
</html>

			
    
<!-- 사용자 메뉴 -->
<div class="service_login_menu clear" id="userMenu">
  <ul class="service_menu">
    <li><a href="#" onclick="displayElement('serviceGuideModal')">제공정보 안내</a></li>
    <li><a href="#" onclick="displayElement('pageGuideModal')">이용방법</a></li>
    <li><a href="#" onclick="return false">서비스 신청</a></li>
  </ul>
  <div class="login_wrap">
    <button type="button" class="logout_btn" onClick="leftMenuUI.logOut()">로그아웃</button>
    <div class="login_info admin">
      <div class="info clear">
        <div class="profile"></div>
        <div class="name" id="mbrNm">홍길동</div>
        <div class="arrow"></div>
      </div>
      <div class="admin_menu_wrap">
        <!-- <ul class="admin_menu">
          <li><a href="#" onclick="return false">관리자 페이지</a></li>
        </ul> -->
      </div>
    </div>
  </div>
</div>
<!-- 사용자 메뉴 : end -->


			<!-- 보고서 layer -->
			<div class="report-wrap multi" style="display: none; height: 80%;"
				id="reportlayer">
				<div class="report-logo">
					<img src="../../../images/map/ic_report_compare.png">내 점포 분석
				</div>
				<div class="report-slide-button" id="bottomreportmove">
					<img src="../../../images/map/btn_report_center.png">
				</div>
				<div class="report-show-button" onclick="ReportUI.hide()">
					<i class="xi-angle-down"></i>
				</div>
				<div class="report-tab-wrap report-tab-count-4" id="reporttab">
					<div
						onclick="ReportUI.tabselected(this, '#reporttab', '#reportcontent', 'tabSelected')"
						class="tabselected">
						<div class="report-tab-tit">업종분석</div>
						<div class="report-white-line first"></div>
					</div>
					<div style="display: none;"
						onclick="ReportUI.tabselected(this, '#reporttab', '#reportcontent', 'tabSelected')">
						<div class="report-tab-tit">매출분석</div>
						<div class="report-white-line"></div>
					</div>
					<div
						onclick="ReportUI.tabselected(this, '#reporttab', '#reportcontent', 'tabSelected')">
						<div class="report-tab-tit">인구분석</div>
						<div class="report-white-line"></div>
					</div>
					<div
						onclick="ReportUI.tabselected(this, '#reporttab', '#reportcontent', 'tabSelected')">
						<div class="report-tab-tit">지역(배후지)분석</div>
						<div class="report-white-line"></div>
					</div>
					<div
						onclick="ReportUI.tabselected(this, '#reporttab', '#reportcontent', 'tabSelected')">
						<div class="report-tab-tit">매출분석</div>
						<div class="report-white-line"></div>
					</div>
				</div>

				<!-- report -->
				<div class="report-content-wrap" id="reportcontent">
					<!-- 업종분석 -->
					<div class="report-content report-content-1"
						style="display: block;">
						<!-- tab -->
						<div class="subtap-wrap" id="subreporttab1">
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab1', '#subreportcontent1', 'tabSelected')"
								class="tabselected">점포수</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab1', '#subreportcontent1', 'tabSelected')">개/폐업수(률)</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab1', '#subreportcontent1', 'tabSelected')">신생기업
								생존율</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab1', '#subreportcontent1', 'tabSelected')">평균
								영업기간</div>
						</div>
						<!-- //tab -->
						<div class="subtabcontent-wrap" id="subreportcontent1">
							<!-- 점포수 -->
							<div class="subtabcontent subtabcontent-1"
								style="display: block;">
								<div class="subtabcontent-tit">
									점포수 · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th style="border-left-width: 1px" scope="col">프랜차이즈</th>
													<th scope="col">일반점포</th>
													<th scope="col">점포수</th>
													<th style="border-left-width: 1px" scope="col">프랜차이즈</th>
													<th scope="col">일반점포</th>
													<th scope="col">점포수</th>
													<th style="border-left-width: 1px" scope="col">프랜차이즈</th>
													<th scope="col">일반점포</th>
													<th scope="col">점포수</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 개/폐업수 -->
							<div class="subtabcontent subtabcontent-2">
								<div class="subtabcontent-tit">
									개/폐업수(률) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="report-table-desc">관측대상이 다르고 관측갯수가 작을 수 있으므로
											개업률/폐업률 착시현상이 일어날 수 있음에 유의하세요.</div>
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th style="border-left-width: 1px" colspan="4"><span
														class="highlight">2019년 3분기</span></th>
													<th style="border-left-width: 1px" colspan="4"><span
														class="highlight">2020년 3분기</span></th>
													<th style="border-left-width: 1px" colspan="4"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th style="border-left-width: 1px" scope="col">개업수</th>
													<th scope="col">폐업수</th>
													<th scope="col">개업률</th>
													<th scope="col">폐업률</th>
													<th style="border-left-width: 1px" scope="col">개업수</th>
													<th scope="col">폐업수</th>
													<th scope="col">개업률</th>
													<th scope="col">폐업률</th>
													<th style="border-left-width: 1px" scope="col">개업수</th>
													<th scope="col">폐업수</th>
													<th scope="col">개업률</th>
													<th scope="col">폐업률</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 신생기업 생존율 -->
							<div class="subtabcontent subtabcontent-3">
								<div class="subtabcontent-tit">
									신생기업 생존율 · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="report-table-desc">관측대상이 다르고 관측갯수가 작을 수 있으므로
											개업률/폐업률 착시현상이 일어날 수 있음에 유의하세요.</div>
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">1년생존율</th>
													<th scope="col">3년생존율</th>
													<th scope="col">5년생존율</th>
													<th scope="col" style="border-left-width: 1px">1년생존율</th>
													<th scope="col">3년생존율</th>
													<th scope="col">5년생존율</th>
													<th scope="col" style="border-left-width: 1px">1년생존율</th>
													<th scope="col">3년생존율</th>
													<th scope="col">5년생존율</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 평균 영업기간 -->
							<div class="subtabcontent subtabcontent-4">
								<div class="subtabcontent-tit">
									평균 영업기간 · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 700px;">
											<colgroup>
												<col style="width: 28%">
												<col style="width: 24%">
												<col style="width: 24%">
												<col style="width: 24%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">평균영업기간</th>
													<th scope="col" style="border-left-width: 1px">평균영업기간</th>
													<th scope="col" style="border-left-width: 1px">평균영업기간</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>

							</div>
						</div>
					</div>
					<!-- //업종분석 -->
					<!-- 매출분석 -->
					<div class="report-content report-content-2">
						<!-- tab -->
						<div class="subtap-wrap" id="subreporttab2">
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab2', '#subreportcontent2', 'tabSelected')"
								class="tabselected">업종별 분기 매출액</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab2', '#subreportcontent2', 'tabSelected')">업종별
								연간 매출액</div>
						</div>
						<!-- //tab -->
						<div class="subtabcontent-wrap" id="subreportcontent2">
							<!-- 업종별 분기 매출액 -->
							<div class="subtabcontent subtabcontent-1"
								style="display: block;">
								<div class="subtabcontent-tit">
									업종별 분기 매출액 · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 28%">
												<col style="width: 24%">
												<col style="width: 24%">
												<col style="width: 24%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">매출액</th>
													<th scope="col" style="border-left-width: 1px">매출액</th>
													<th scope="col" style="border-left-width: 1px">매출액</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 업종별 연간 매출액 -->
							<div class="subtabcontent subtabcontent-2">
								<div class="subtabcontent-tit">
									업종별 연간 매출액 · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 28%">
												<col style="width: 24%">
												<col style="width: 24%">
												<col style="width: 24%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">매출액</th>
													<th scope="col" style="border-left-width: 1px">매출액</th>
													<th scope="col" style="border-left-width: 1px">매출액</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
						</div>
					</div>
					<!-- //매출분석 -->
					<!-- 인구분석 -->
					<div class="report-content report-content-3">
						<!-- tab -->
						<div class="subtap-wrap" id="subreporttab3">
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab3', '#subreportcontent3', 'tabSelected')"
								class="tabselected">
								성별<span>(상존)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab3', '#subreportcontent3', 'tabSelected')">
								연령별<span>(상존)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab3', '#subreportcontent3', 'tabSelected')">
								시간대별<span>(상존)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab3', '#subreportcontent3', 'tabSelected')">
								요일별<span>(상존)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab3', '#subreportcontent3', 'tabSelected')">
								성별<span>(주거)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab3', '#subreportcontent3', 'tabSelected')">
								연령별<span>(주거)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab3', '#subreportcontent3', 'tabSelected')">
								<!-- 성별<span>(직장)</span> -->
								<span>직장인구</span>
							</div>
							<!-- <div
								onclick="ReportUI.tabselected(this, '#subreporttab3', '#subreportcontent3', 'tabSelected')">
								직종별<span>(직장)</span>
							</div> -->
						</div>
						<!-- //tab -->
						<div class="subtabcontent-wrap" id="subreportcontent3">
							<!-- 성별(상존) -->
							<div class="subtabcontent subtabcontent-1"
								style="display: block;">
								<div class="subtabcontent-tit">
									성별(길단위) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
								<div class="subtabcontent-tit">
									성별(건물단위) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 연령별(상존) -->
							<div class="subtabcontent subtabcontent-2">
								<div class="subtabcontent-tit">
									연령별(길단위) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
								<div class="subtabcontent-tit">
									연령별(건물단위) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 시간대별(상존) -->
							<div class="subtabcontent subtabcontent-3">
								<div class="subtabcontent-tit">
									시간대별(길단위) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
								<div class="subtabcontent-tit">
									시간대별(건물단위) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 요일별(상존) -->
							<div class="subtabcontent subtabcontent-4">
								<div class="subtabcontent-tit">
									요일별(길단위) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
								<div class="subtabcontent-tit">
									요일별(건물단위) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 성별(주거) -->
							<div class="subtabcontent subtabcontent-5">
								<div class="subtabcontent-tit">
									성별(주거인구) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 연령별(주거) -->
							<div class="subtabcontent subtabcontent-6">
								<div class="subtabcontent-tit">
									연령별(주거인구) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">유소년</th>
													<th scope="col">생산가능</th>
													<th scope="col">노령</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">유소년</th>
													<th scope="col">생산가능</th>
													<th scope="col">노령</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">유소년</th>
													<th scope="col">생산가능</th>
													<th scope="col">노령</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 성별(직장) => 직장인구로 변경 -->
							<div class="subtabcontent subtabcontent-7">
								<div class="subtabcontent-tit">
									<!-- 성별(직장인구) -->직장인구 · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 직종별(직장) => 삭제 -->
							<!-- <div class="subtabcontent subtabcontent-8">
								<div class="subtabcontent-tit">
									직종별(직장인구) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											차트 스타일 반응형 위해서 필수
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위:개 | 기준일 2022년 02월 02일</div>
									</div>
									<div class="report-table">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 8.5%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
												<col style="width: 6.1%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="5" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="5" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="5" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">상용직 남성</th>
													<th scope="col">상용직 여성</th>
													<th scope="col">일용직 남성</th>
													<th scope="col">일용직 여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">상용직 남성</th>
													<th scope="col">상용직 여성</th>
													<th scope="col">일용직 남성</th>
													<th scope="col">일용직 여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">상용직 남성</th>
													<th scope="col">상용직 여성</th>
													<th scope="col">일용직 남성</th>
													<th scope="col">일용직 여성</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div> -->
						</div>
					</div>
					<!-- //인구분석 -->
					<!-- 지역(배후지)분석 -->
					<div class="report-content report-content-4">
						<!-- tab -->
						<div class="subtap-wrap" id="subreporttab4">
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab4', '#subreportcontent4', 'tabSelected')"
								class="tabselected">공시지가변동율</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab4', '#subreportcontent4', 'tabSelected')">가구세대</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab4', '#subreportcontent4', 'tabSelected')">소비트렌드</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab4', '#subreportcontent4', 'tabSelected')">아파트현황</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab4', '#subreportcontent4', 'tabSelected')">주요시설
								집객시설</div>
						</div>
						<!-- //tab -->
						<div class="subtabcontent-wrap" id="subreportcontent4">
							<!-- 공시지가변동율 -->
							<div class="subtabcontent subtabcontent-1"
								style="display: block;">
								<div class="subtabcontent-tit">
									<span class="ft_blue">공시지가</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 27%">
												<col style="width: 24%">
												<col style="width: 24%">
												<col style="width: 24%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="1" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="1" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="1" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">공시지가</th>
													<th scope="col" style="border-left-width: 1px">공시지가</th>
													<th scope="col" style="border-left-width: 1px">공시지가</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
								<div class="subtabcontent-tit">
									<span class="ft_blue">변동율</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 27%">
												<col style="width: 24%">
												<col style="width: 24%">
												<col style="width: 24%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="1" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="1" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="1" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">변동율</th>
													<th scope="col" style="border-left-width: 1px">변동율</th>
													<th scope="col" style="border-left-width: 1px">변동율</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 가구세대 -->
							<div class="subtabcontent subtabcontent-2">
								<div class="subtabcontent-tit">
									<span class="ft_blue">가구세대</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 가구 | 기준일 : 2021년 09년 30일</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
												<col style="width: 9.6%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">비아파트</th>
													<th scope="col">아파트</th>
													<th scope="col">총가구수</th>
													<th scope="col" style="border-left-width: 1px">비아파트</th>
													<th scope="col">아파트</th>
													<th scope="col">총가구수</th>
													<th scope="col" style="border-left-width: 1px">비아파트</th>
													<th scope="col">아파트</th>
													<th scope="col">총가구수</th>
												</tr>
											</thead>
											<tbody>
											</tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 소비트렌드 -->
							<div class="subtabcontent subtabcontent-4">
								<div class="subtabcontent-tit">
									<span class="ft_blue">소비트렌드</span>
								</div>
								<div class="basedate">단위 : %</div>
								<div class="graph-wrap graph-count-2">
									<div class="graph-box">
										<div class="graph-tit">
											<span class="ft_blue">전체 업종</span>
										</div>
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
									<div class="graph-box">
										<div class="graph-tit">
											<span class="ft_blue">소매 업종</span>
										</div>
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
									<div class="graph-box">
										<div class="graph-tit">
											<span class="ft_blue">서비스 업종</span>
										</div>
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
									<div class="graph-box">
										<div class="graph-tit">
											<span class="ft_blue">외식 업종</span>
										</div>
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
							</div>
							<!-- 아파트현황 -->
							<div class="subtabcontent subtabcontent-5">
								<div class="subtabcontent-tit">
									<span class="ft_blue">아파트현황</span>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 가구 | 기준일 : 2021년 09년 30일</div>
									</div>
									<div class="report-table report-table-blue">
										<table>
											<colgroup>
												<col style="width: 25%">
												<col style="width: 15%">
												<col style="width: 15%">
												<col style="width: 15%">
												<col style="width: 15%">
												<col style="width: 15%">
											</colgroup>
											<thead>
												<tr>
													<th>구분</th>
													<th>총가구수</th>
													<th>66㎡이하</th>
													<th>99㎡이하</th>
													<th>132㎡이하</th>
													<th>165㎡이하</th>
												</tr>
											</thead>
											<tbody>
												<tr>
													<td>아파트세대</td>
													<td>0</td>
													<td>0</td>
													<td>0</td>
													<td>0</td>
													<td>0</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div class="report-table report-table-blue">
										<table>
											<colgroup>
												<col style="width: 23%">
												<col style="width: 11%">
												<col style="width: 11%">
												<col style="width: 11%">
												<col style="width: 11%">
												<col style="width: 11%">
												<col style="width: 11%">
												<col style="width: 11%">
											</colgroup>
											<thead>
												<tr>
													<th>구분</th>
													<th>1억이하</th>
													<th>1억대</th>
													<th>2억대</th>
													<th>3억대</th>
													<th>4억대</th>
													<th>5억대</th>
													<th>6억이상</th>
												</tr>
											</thead>
											<tbody>
												<tr>
													<td>아파트가격대</td>
													<td>0</td>
													<td>0</td>
													<td>0</td>
													<td>0</td>
													<td>0</td>
													<td>0</td>
													<td>0</td>
												</tr>
											</tbody>
										</table>
									</div>
								</div>
								<div class="graph-wrap graph-count-2">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
							</div>
							<!-- 주요시설 집객시설 -->
							<div class="subtabcontent subtabcontent-6">
								<div class="subtabcontent-tit">
									<span class="ft_blue">주요시설 집객시설</span>
								</div>
								<div class="basedate">단위 : 개</div>
								<div class="graph-wrap graph-count-2">
									<div class="graph-box report-table-wrap">
										<div class="report-table report-table-blue">
											<table>
												<colgroup>
													<col style="width: 30%">
													<col style="width: 60%">
												</colgroup>
												<thead>
													<tr>
														<th>구분</th>
														<th>시설수</th>
													</tr>
												</thead>
												<tbody>
													<tr>
														<td>관공서</td>
														<td>14</td>
													</tr>
													<tr>
														<td>금융기관</td>
														<td>8</td>
													</tr>
													<tr>
														<td>병원</td>
														<td>5</td>
													</tr>
													<tr>
														<td>학교</td>
														<td>0</td>
													</tr>
													<tr>
														<td>유통점</td>
														<td>5</td>
													</tr>
													<tr>
														<td>영화/공연</td>
														<td>2</td>
													</tr>
													<tr>
														<td>숙박</td>
														<td>3</td>
													</tr>
													<tr>
														<td>교통시설</td>
														<td>9</td>
													</tr>
												</tbody>
											</table>
										</div>
									</div>
									<div class="graph-box">
										<div class="graph-chart-wrap" style="height: 380px;">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					<!-- //지역(배후지)분석 -->
					<!-- 소비분석 -->
					<div class="report-content report-content-5">
						<!-- tab -->
						<div class="subtap-wrap" id="subreporttab5">
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab5', '#subreportcontent5', 'tabSelected')"
								class="tabselected">
								성별<span>(건수)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab5', '#subreportcontent5', 'tabSelected')">
								연령별<span>(건수)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab5', '#subreportcontent5', 'tabSelected')">
								시간대별<span>(건수)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab5', '#subreportcontent5', 'tabSelected')">
								요일별<span>(건수)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab5', '#subreportcontent5', 'tabSelected')">
								성별<span>(금액)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab5', '#subreportcontent5', 'tabSelected')">
								연령별<span>(금액)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab5', '#subreportcontent5', 'tabSelected')">
								시간대별<span>(금액)</span>
							</div>
							<div
								onclick="ReportUI.tabselected(this, '#subreporttab5', '#subreportcontent5', 'tabSelected')">
								요일별<span>(금액)</span>
							</div>
						</div>
						<!-- //tab -->
						<div class="subtabcontent-wrap" id="subreportcontent5">
							<!-- 성별(건수) -->
							<div class="subtabcontent subtabcontent-1"
								style="display: block;">
								<div class="subtabcontent-tit">
									성별(건수) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="report-table-desc"></div>
										<div class="basedate">단위 : 점포당(건)</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 12.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 연령별(건수) -->
							<div class="subtabcontent subtabcontent-2">
								<div class="subtabcontent-tit">
									연령별(건수) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 점포당(건)</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 시간대별(건수) -->
							<div class="subtabcontent subtabcontent-3">
								<div class="subtabcontent-tit">
									시간대별(건수) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 점포당(건)</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 요일별(건수) -->
							<div class="subtabcontent subtabcontent-4">
								<div class="subtabcontent-tit">
									요일별(건수) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" id="trdAreaChart4_4_1"
												style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 점포당(건)</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4"></th>
													<th colspan="4"></th>
													<th colspan="4"></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 성별(금액) -->
							<div class="subtabcontent subtabcontent-5">
								<div class="subtabcontent-tit">
									성별(금액) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" id="trdAreaChart4_3_1"
												style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 점포당(원)</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 12.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
												<col style="width: 9.7%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="3" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">남성</th>
													<th scope="col">여성</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 연령별(금액) -->
							<div class="subtabcontent subtabcontent-6">
								<div class="subtabcontent-tit">
									연령별(금액) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" id="trdAreaChart4_5_1"
												style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 점포당(원)</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">10~20대</th>
													<th scope="col">30~40대</th>
													<th scope="col">50~60대</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 시간대별(금액) -->
							<div class="subtabcontent subtabcontent-7">
								<div class="subtabcontent-tit">
									시간대별(금액) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" id="trdAreaChart4_6_1"
												style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 점포당(원)</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">오전
														(00~11시)</th>
													<th scope="col">오후 (11~17시)</th>
													<th scope="col">저녁 (17~24시)</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
							<!-- 요일별(금액) -->
							<div class="subtabcontent subtabcontent-8">
								<div class="subtabcontent-tit">
									요일별(금액) · <span class="ft_blue">양식음식점</span>
								</div>
								<div class="graph-wrap graph-count-1">
									<div class="graph-box">
										<div class="graph-chart-wrap">
											<div class="graph-chart" id="trdAreaChart4_7_1"
												style="width: 100%; height: 100%;"></div>
											<!-- 차트 스타일 반응형 위해서 필수 -->
										</div>
									</div>
								</div>
								<div class="report-table-wrap">
									<div class="report-table-top clear">
										<div class="basedate">단위 : 점포당(원)</div>
									</div>
									<div class="report-table report-tableQu">
										<table style="min-width: 1000px;">
											<colgroup>
												<col style="width: 13.6%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
												<col style="width: 7.2%">
											</colgroup>
											<thead>
												<tr>
													<th rowspan="2">구분</th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2019년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2020년 3분기</span></th>
													<th colspan="4" style="border-left-width: 1px"><span
														class="highlight">2021년 3분기</span></th>
												</tr>
												<tr>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
													<th scope="col" style="border-left-width: 1px">주중
														(월~목)</th>
													<th scope="col">금요일</th>
													<th scope="col">주말 (토~일)</th>
													<th scope="col">합계</th>
												</tr>
											</thead>
											<tbody></tbody>
										</table>
									</div>
								</div>
							</div>
						</div>
					</div>
					<!-- //소비분석 -->
				</div>
			</div>
			<!-- //보고서 -->

			<!-- 상권비교분석보고서 -->
			<div style="height: 60px; display: none; min-height: 60px;"
				class="report-wrap single" id="reportsinglelayer">
				<div class="report-logo">
					<img src="../../../images/map/ic_report_compare.png">내 점포 분석
				</div>
				<div class="report-slide-button" id="bottomsinglereportmove">
					<img src="../../../images/map/btn_report_center.png">
				</div>
				<div class="report-show-button" onclick="Doc.btnRepoHide()">
					<i class="xi-angle-down"></i>
				</div>
				<div class="report-singlecontent-wrap" id="reportsinglecontent">
					<div>
						<div class="report-singlecontent-top">
							<div class="report-singlecontent-tit">업종 비교 분석</div>
							<div class="report-close-btn" onclick="Doc.btnCloseRepo()">
								<i class="xi-close"></i>
							</div>
						</div>
						<div class="report-singlecontent">
							<div class="report-table-wrap">
								<div class="report-table"></div>
							</div>
						</div>
					</div>
				</div>
			</div>
			<div id="singlereporttabletemp" style="display: none;">
				<table>
					<colgroup>
						<col style="width: 140px">
						<col style="width: *">
					</colgroup>
					<thead>
						<tr>
							<th colspan="2">동천로17길</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>상권유형</td>
							<td>골목상권(준주거지역)</td>
						</tr>
						<tr>
							<td>상권면적</td>
							<td>435.126m</td>
						</tr>
						<tr>
							<td>선택업종</td>
							<td>한식음식점</td>
						</tr>
						<tr>
							<td>창업온도</td>
							<td>
							<!-- <div class="report-table-temperature">
									<span style="background-color: #e86b00;"></span><span
										style="background-color: #fc933a;"></span><span
										style="background-color: #ffc798;"></span><span></span>
								</div> 
							-->
							</td>
						</tr>
						<tr>
							<td>점포수</td>
							<td>21</td>
						</tr>
						<tr>
							<td>3년생존율(%)</td>
							<td>0%</td>
						</tr>
						<tr>
							<td>평균영업기간(년)</td>
							<td>3.6년</td>
						</tr>
						<tr>
							<td>상존인구-길단위(명/ha)</td>
							<td>98,580</td>
						</tr>
						<tr>
							<td>상존인구-건물단위(명/ha)</td>
							<td>165,115</td>
						</tr>
						<tr>
							<td>주거인구(명/ha)</td>
							<td>154</td>
						</tr>
						<tr>
							<td>직장인구(명/ha)</td>
							<td>43</td>
						</tr>
						<tr>
							<td>매출(원/점포당)</td>
							<td>49,250,115</td>
						</tr>
					</tbody>
				</table>
			</div>
			<div id="reporttabletemp" style="display: none;">
				<div class="com_table_wrap">
					<table class="com_table">
						<colgroup>
							<col style="width: 30%">
							<col style="width: 40%">
							<col style="width: 30%">
						</colgroup>
						<thead>
							<tr>
								<th colspan="3">양식음식점</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td class="cate" rowspan="6">업종</td>
								<td>점포수</td>
								<td><b>15개</b></td>
							</tr>
							<tr>
								<td>점포수 증감율</td>
								<td><b>30.5%</b></td>
							</tr>
							<tr>
								<td>개업율</td>
								<td><b>10.3%</b></td>
							</tr>
							<tr>
								<td>폐업율</td>
								<td><b>0.9%</b></td>
							</tr>
							<tr>
								<td>프랜차이즈 점포수</td>
								<td><b>5개</b></td>
							</tr>
							<tr>
								<td>평균업력</td>
								<td><b>6년</b></td>
							</tr>
							<tr>
								<td class="cate" rowspan="4">매출</td>
								<td>전체매출(금액,증감율)</td>
								<td><b>12%</b></td>
							</tr>
							<tr>
								<td>점포당매출(금액,증감율)</td>
								<td><b>0.6%</b></td>
							</tr>
							<tr>
								<td>프랜차이즈매출액</td>
								<td><b>12,850,440</b></td>
							</tr>
							<tr>
								<td>건단가</td>
								<td><b>120,000</b></td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
			<!-- //상권비교분석보고서 -->
			<!-- 상권보고서(월/분기) 보고서 팝업 -->
			<div class="analyreport-popup-wrap">				
				<div class="report" style="cursor: pointer; font-weight: bold; color: #0068BD;" value="1">AI 활용 상권 분석 보고서(시범)</div>
				<div class="report" style="cursor: pointer" value="2">분기 간략 보고서</div>
				<div class="report" style="cursor: pointer" value="3">월 간략 보고서</div>
				<div class="report" style="cursor: pointer" value="4">분기 종합 보고서</div>
				<div class="report" style="cursor: pointer" value="5">월 종합 보고서</div>
			</div>
			<!-- //상권보고서(월/분기) 보고서 팝업 -->
		</div>

		<!-- 리포트 PDF 출력 모달 -->
		<div id="pdfPrintProcessModal" class="modal_wrap modal_long map_report_modal" style="display: none; z-index: 3000;">
			<div class="pdfProgress">
				<div class="pdfProgressContent">
					<label style="font-size: 1.5vw;">
						보고서를 PDF 파일로 생성 중입니다.
					</label>
					<label style="font-size: 1.2vw;">
						잠시만 기다려주십시오.
					</label>
					<div class="report-loader" style="margin-top: 1vh;"></div>
					<br>
					<label id="pdfPrintProgressStatus" style="font-size: 1.5vw; padding-top: 6px;">
						1 / 7 Page
					</label>
				</div>
			</div>
		</div>
		
		<!-- 리포트 이력 - 보고서 모달 : S -->
		<div id="mapReportModal"
			class="modal_wrap modal_long map_report_modal" style="display: none;">

		</div>
		<!-- //리포트 이력 - 보고서 모달 : S -->
		
    

		<!-- 제공정보 안내 -->
		<div id="serviceGuideModal" class="modal_wrap modal_long service_guide_modal" style="display: none;">
        <div class="modal_box">
            <div class="modal_head clear">
                <div class="head_logo clear">
                    <div class="logo_txt">경기도 상권분석지원 서비스</div>
                </div>
                <button type="button" class="modal_close"><img src="../../images/common/modal_close_wh.png" alt="닫기"></button><!-- // modal_close -->
            </div>
           <div class="modal_cont">
                <h2 class="modal_com_title">제공정보 안내</h2>
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>점포수</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 사업자등록번호 기반 경기도 소재 사업체 정보</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">사업자등록번호 : 국세청에 사업을 영위하기 위해 발급받는 사업체 구분번호</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">점포수 산식</div>
                        <div class="box_body"><div class="desc">당기 운영 점포수 + 폐업 점포수</div></div>
                    </div>
                </article><!-- // 점포수 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>개·폐업률</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 당기 개·폐업 사업체를 전체점포수로 나누고 100을 곱한 값</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">전체 점포수 : 폐업 이력이 존재하지 않거나 해당 기내 내 폐업일자가 있는 점포</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">개·폐업률 산식</div>
                        <div class="box_body"><div class="desc">(당기 개/폐업신고점포수 ÷ 전체점포수) X 100</div></div>
                    </div>
                </article><!-- // 개·폐업률 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>연차별 생존율</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 5년 전 신생기업 중 '기준 연도'까지 생존해 있는 기업의 비율을 의미함</div>
                        </div>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">(t)년도 생존율 산식</div>
                        <div class="box_body"><div class="desc">1년 생존율 : (t)년 신생기업 중 (t+1)년까지 생존한 기업수/(t)년 신생기업수*100<br> 5년 생존율 : (t)년 신생기업 중 (t+5)년까지 생존한 기업수/(t)년 신생기업수*100</div></div>
                    </div>
                </article><!-- // 연차별 생존율 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>신생기업 생존율</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 1 ~ 5년 전 신생기업 중 ‘기준 연도’까지 생존해 있는 기업의 비율을 의미함</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">생존은 기업체 신생 이후, t년까지 소멸되지 않고 지속적으로 존속한 경우를 의미함</li>
                            <li class="desc">당해 연도 기업의 1 ~ 5년 생존율은 신생년도가 다르므로 n년 생존율일 n-1년 생존율보다 작을 수 있음</li>
                            <li class="desc">개·폐업이 거의 없는 업종은 생존율이 지나치게 높거나 낮을 수 있음</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">(t)년도 생존율 산식</div>
                        <div class="box_body"><div class="desc">1년 생존율 : (t-1)년 신생기업 중 (t)년까지 생존한 기업수/(t-1)년 신생기업수*100<br> 5년 생존율 : (t-5)년 신생기업 중 (t)년까지 생존한 기업수/(t-5)년 신생기업수*100</div></div>
                    </div>
                </article><!-- // 신생기업 생존율 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>평균영업기간</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 점포의 개업일자와 폐업일자를 기준으로 기준으로 영업 지속 개월 수를 계산하고 평균하여 산출하는 정보</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">최근 10년 기준 : 현재시점으로부터 과거 10년간 개·폐업한 점포의 평균영업기간을 계산</li>
                            <li class="desc">최근 30년 기준 : 30년 전부터 현재까지 개·폐업한 점포의 평균영업기간을 계산</li>
                            <li class="desc">경기상권검색/내점포분석 메뉴에서는 최근 10년 기준으로 정보제공</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">평균영업기간 산식</div>
                        <div class="box_body"><div class="desc">영업기간의 (폐업신고일-개업신고일) 평균</div></div>
                    </div>
                </article><!-- // 평균영업기간 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>추정매출액</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 카드사의 카드승인금액을 기반으로 경기도의 보정비율을 곱하여 118개 생활밀접업종 매출액을 추정</div>
                        </div>
                    </div>
                    <div class="sky_table_wrap">
                        <table class="sky_table">
                            <colgroup>
                                <col style="width: 20%">
                                <col style="width: 20%">
                                <col style="width: 60%">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th>항목</th>
                                    <th>정보출처</th>
                                    <th>주요내용</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>보정비율</td>
                                    <td>경기도</td>
                                    <td>연별/자치구/행정동/기초단위구/업종별 보정비율</td>
                                </tr>
                                <tr>
                                    <td>카드승인금액</td>
                                    <td>BC</td>
                                    <td>월별/자치구/행정동/기초단위구/업종별 카드승인금액</td>
                                </tr>
                                <tr>
                                    <td>추정매출액</td>
                                    <td>경기도</td>
                                    <td>추정매출액 = 카드승인금액 ÷ 보정비율</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </article><!-- // 추정매출액 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>길단위 상존인구</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : KT 유동인구를 기반으로 10m 길이 단위로 생성된 길단위 상존인구</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">폭이 넓은 대로를 두 개의 라인으로 분리하고, 보행이 불가능한 지역(도로 중앙, 도로간의 경계, 교차로 등)을 제외</li>
                            <li class="desc">1ha(1만㎡)당 인구밀도와 인구수 두가지 형태로 정보 제공</li>
                        </ul>
                    </div>
                    <div class="half_box_wrap step_box_wrap">
                        <div class="half">
                            <div class="cont_box blue_box">
                                <div class="box_head">1 . 10m단위 도로 SHP 생성</div>
                                <div class="box_body">
                                    <div class="step_wrap">
                                        <div class="step_box">
                                            <div class="step_title">보행가능 도로 추출</div>
                                            <div class="step_desc">
                                                <div class="bold_txt">보행불가 도로 제외</div>
                                                <ul class="desc_wrap">
                                                    <li class="desc">자동차 전용도로 등 보행불가도로 제외</li>
                                                </ul>
                                            </div>
                                        </div>
                                        <div class="step_arrow"><i class="xi-angle-down"></i></div>
                                        <div class="step_box">
                                            <div class="step_title">보행라인 생성</div>
                                            <div class="step_desc float_desc">
                                                <div class="float">
                                                    <div class="bold_txt">도로분류</div>
                                                    <ul class="desc_wrap">
                                                        <li class="desc">광폭도로</li>
                                                        <li class="desc">일반도로</li>
                                                        <li class="desc">소로</li>
                                                    </ul>
                                                </div>
                                                <div class="float">
                                                    <div class="bold_txt">라인생성</div>
                                                    <ul class="desc_wrap">
                                                        <li class="desc">도로 기초라인 생성</li>
                                                        <li class="desc">광폭도로 : 양쪽 두갈래 라인 생성</li>
                                                        <li class="desc">일반도로 : 광폭도로/교차지점 삭제</li>
                                                        <li class="desc">소로 : 일반도로/광폭도로와 교차지점 삭제</li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="step_arrow"><i class="xi-angle-down"></i></div>
                                        <div class="step_box">
                                            <div class="step_title">10m 단위 도로 SHP 생성</div>
                                            <div class="step_desc">
                                                <div class="bold_txt">10m 단위 도로 SHP 생성</div>
                                                <ul class="desc_wrap">
                                                    <li class="desc">각 분류별 도로라인 별 10m 단위 도로 생성</li>
                                                    <li class="desc">중점생성 (도로포인트)</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div><!-- // half -->
                        <div class="half">
                            <div class="cont_box purple_box">
                                <div class="box_head">1 . 10m단위 도로 SHP 생성</div>
                                <div class="box_body">
                                    <div class="step_wrap">
                                        <div class="step_box">
                                            <div class="step_title">기초단위구별 그리드 단위 배분</div>
                                            <div class="step_desc">
                                                <ul class="desc_wrap">
                                                    <li class="desc">각 기초단위구 영역에 존재하는 그리드의 중심점 수를 계산</li>
                                                    <li class="desc">기초단위구별 상존인구를 그리드 중심점의 개수로 균등 배분</li>
                                                </ul>
                                            </div>
                                        </div>
                                        <div class="step_arrow"><i class="xi-angle-down"></i></div>
                                        <div class="step_box">
                                            <div class="step_title">도로 포인트별 상존인구 생성</div>
                                            <div class="step_desc">
                                                <ul class="desc_wrap">
                                                    <li class="desc">포인트별 반경 50m내 그리드 상존인구 생성</li>
                                                </ul>
                                            </div>
                                        </div>
                                        <div class="step_arrow"><i class="xi-angle-down"></i></div>
                                        <div class="step_box">
                                            <div class="step_title">세분화 데이터셋 구축</div>
                                            <div class="step_desc">
                                                <ul class="desc_wrap">
                                                    <li class="desc">상존인구 유형별 세분화 데이터셋 구축</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div><!-- // half -->
                    </div>
                </article><!-- // 길단위 상존인구 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>건물단위 상존인구</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 기존 길단위 상존인구 배분로직을 수정/보완하여 셀단위 유동인구를 건물단위로 배분</div>
                        </div>
                    </div>
                    <div class="full_blue_box">
                        <div class="title">건물단위 상존인구 구축</div>
                        <div class="half_box_wrap">
                            <div class="half">
                                <div class="wh_box clear">
                                    <div class="txt_wrap" style ="width:250px">
                                        <div class="box_title">1단계 (cell(50x50)>그리드 단위 집계)</div>
                                        <ul class="desc_wrap">
                                            <li class="desc" >각 그리드 영역에 포함되는<br> 셀의 합 계산</li>
                                            <!-- <li class="desc" >셀별 상존인구를 그리드 <br>중심점의 개수로 균등 배분</li> -->
                                        </ul>
                                    </div>
                                    <div class="img_wrap"><img src="../../images/common/service_guide1.png"></div>
                                </div>
                            </div>
                            <div class="half">
                                <div class="wh_box clear">
                                    <div class="txt_wrap">
                                        <div class="box_title">2단계 (그리드 > 건물 단위 배분)</div>
                                        <ul class="desc_wrap">
                                            <li class="desc">각 그리드에 존재하는 건물의 <br>연면적을 계산</li>
                                            <li class="desc">그리드별 상존인구를 그리드 내<br> 건물의 연면적 비율에 비례하여 배분</li>
                                        </ul>
                                    </div>
                                    <div class="img_wrap"><img src="../../images/common/service_guide2.png"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </article><!-- // 건물단위 상존인구 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>직장인구</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 종사자수 DB에서 산출하는 정보</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">1ha(1만㎡)당 인구밀도와 인구수 두가지 형태로 정보 제공</li>
                        </ul>
                    </div>
                </article><!-- // 직장인구 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>주거인구</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 국토지리정보원에서 제공하는 100mX100m 인구데이터에서 산출하는 정보</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">1ha(1만㎡)당 인구밀도와 인구수 두가지 형태로 정보 제공</li>
                        </ul>
                    </div>
                </article><!-- // 주거인구 -->
                <!-- <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>환산임대료 산식</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 최근 1년간 수집된 서울신용보증재단 내부자료를 기반으로 추정된 값</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">실제 시세와 오차가 있을 수 있으며, 임대료는 입지, 건물상태, 인지성에 따라 차이가 큼으로 현장 확인 필요</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">환산임대료 산식</div>
                        <div class="box_body"><div class="desc">(보증금 X 12%)/12 + 월세</div></div>
                    </div>
                </article> --><!-- // 환산임대료 산식 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>가구세대(공동주택)</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 국토교통부에서 제공된 공동주택 가격 정보를 이용하여 아파트및 비아파트의 세대수를 산출하는 정보</div>
                        </div>
                    </div>
                    <!-- <div class="purple_box">
                        <div class="box_head">가구세대 산식</div>
                        <div class="box_body"><div class="desc">공동주택 세대수 = 전체 세대수 - 아파트 세대수</div></div>
                    </div> -->
                </article><!-- // 가구세대 -->
               <!--  <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>소득정보</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 국민건강보험공단의 건강보험료 납부 20분위를 기준소득월액으로 환산하여 주거지 기반으로 소득분위(10분위)를 산출하는 정보</div>
                        </div>
                    </div>
                </article> --><!-- // 소득정보 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>아파트 정보</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 경기도 공간정보담당관에서 제공된 아파트 DB를 기반으로 산출하는 정보</div>
                        </div>
                    </div>
                </article><!-- // 아파트 정보 -->
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>주요 집객시설</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 경기도 소재 관공서, 금융기관, 병원, 학교, 유통점, 문화관광(영화관), 숙박시설, 교통(정류장, 지하철) 등 인구집중 유발시설 정보</div>
                        </div>
                    </div>
                </article><!-- // 주요 집객시설 -->
                 <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>소비 트렌드</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : KB국민카드사의 카드 소비를 기준으로 산출하는 정보</div>
                        </div>
                    </div>
                </article><!-- // 소비 트렌드  -->
               <!--  <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>소득정보</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 경기도 교통정책과에서 제공하는 스마트카드 정보를 기반으로 산출하는 정보</div>
                        </div>
                    </div>
                </article> --><!-- // 교통카드 정보 -->
               <!--  <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>금융비용 정보</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 소상공인이 사업을 영위하기 위해 차입한 차입금에 대한 이자비용<br> 한국신용정보원과 공동 작성 정보</div>
                        </div>
                    </div>
                    <div class="sky_table_wrap">
                        <table class="sky_table">
                            <colgroup>
                                <col style="width: 20%">
                                <col style="width: 20%">
                                <col style="width: 60%">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th>항목</th>
                                    <th>정보출처</th>
                                    <th>주요내용</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>대출잔액</td>
                                    <td>평균금리</td>
                                    <td>금융비용</td>
                                </tr>
                                <tr>
                                    <td>한국신용정보</td>
                                    <td>한국은행</td>
                                    <td>서울신보</td>
                                </tr>
                                <tr>
                                    <td>월별 대출 잔액</td>
                                    <td>월별 예금은행 가중평균금리(연 단위) (중소기업대출 잔액 기준)</td>
                                    <td>대출잔액 X 평균금리 ÷ 12(월 단위)</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </article> --><!-- // 금융비용 정보 -->
            </div>
        </div>
     </div>		
		
		
		
    <!-- <div id="serviceGuideModal" class="modal_wrap modal_long service_guide_modal" style="display: none;">
        <div class="modal_box">
            <div class="modal_head clear">
                <div class="head_logo clear">
                    <div class="logo_txt">경기도 상권분석지원 서비스</div>
                </div>
                <button type="button" class="modal_close"><img src="../../images/common/modal_close_wh.png" alt="닫기"></button>// modal_close
            </div>
           <div class="modal_cont">
                <h2 class="modal_com_title">제공정보 안내</h2>
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>점포수</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 사업자등록번호 기반 경기도 소재 사업체 정보</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">사업자등록번호 : 국세청에 사업을 영위하기 위해 발급받는 사업체 구분번호</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">점포수 산식</div>
                        <div class="box_body"><div class="desc">당기 운영 점포수 + 폐업 점포수</div></div>
                    </div>
                </article>// 점포수
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>개·폐업률</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 당기 개·폐업 사업체를 전체점포수로 나누고 100을 곱한 값</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">전체 점포수 : 폐업 이력이 존재하지 않거나 해당 기내 내 폐업일자가 있는 점포</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">개·폐업률 산식</div>
                        <div class="box_body"><div class="desc">(당기 개/폐업신고점포수 ÷ 전체점포수) X 100</div></div>
                    </div>
                </article>// 개·폐업률
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>연차별 생존율</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 5년 전 신생기업 중 '기준 연도'까지 생존해 있는 기업의 비율을 의미함</div>
                        </div>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">(t)년도 생존율 산식</div>
                        <div class="box_body"><div class="desc">1년 생존율 : (t)년 신생기업 중 (t+1)년까지 생존한 기업수/(t)년 신생기업수*100<br> 5년 생존율 : (t)년 신생기업 중 (t+5)년까지 생존한 기업수/(t)년 신생기업수*100</div></div>
                    </div>
                </article>// 연차별 생존율
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>신생기업 생존율</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 1 ~ 5년 전 신생기업 중 ‘기준 연도’까지 생존해 있는 기업의 비율을 의미함</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">생존은 기업체 신생 이후, t년까지 소멸되지 않고 지속적으로 존속한 경우를 의미함</li>
                            <li class="desc">당해 연도 기업의 1 ~ 5년 생존율은 신생년도가 다르므로 n년 생존율일 n-1년 생존율보다 작을 수 있음</li>
                            <li class="desc">개·폐업이 거의 없는 업종은 생존율이 지나치게 높거나 낮을 수 있음</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">(t)년도 생존율 산식</div>
                        <div class="box_body"><div class="desc">1년 생존율 : (t-1)년 신생기업 중 (t)년까지 생존한 기업수/(t-1)년 신생기업수*100<br> 5년 생존율 : (t-5)년 신생기업 중 (t)년까지 생존한 기업수/(t-5)년 신생기업수*100</div></div>
                    </div>
                </article>// 신생기업 생존율
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>평균영업기간</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 점포의 개업일자와 폐업일자를 기준으로 기준으로 영업 지속 개월 수를 계산하고 평균하여 산출하는 정보</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">최근 10년 기준 : 현재시점으로부터 과거 10년간 개·폐업한 점포의 평균영업기간을 계산</li>
                            <li class="desc">최근 30년 기준 : 30년 전부터 현재까지 개·폐업한 점포의 평균영업기간을 계산</li>
                            <li class="desc">경기상권검색/내점포분석 메뉴에서는 최근 10년 기준으로 정보제공</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">평균영업기간 산식</div>
                        <div class="box_body"><div class="desc">영업기간의 (폐업신고일-개업신고일) 평균</div></div>
                    </div>
                </article>// 평균영업기간
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>추정매출액</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 3개 카드사의 카드승인금액을 기반으로 경기도의 보정비율을 곱하여 100개 생활밀접업종 매출액을 추정</div>
                        </div>
                    </div>
                    <div class="sky_table_wrap">
                        <table class="sky_table">
                            <colgroup>
                                <col style="width: 20%">
                                <col style="width: 20%">
                                <col style="width: 60%">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th>항목</th>
                                    <th>정보출처</th>
                                    <th>주요내용</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>보정비율</td>
                                    <td>경기도</td>
                                    <td>연별/자치구/행정동/블록별/업종별 보정비율</td>
                                </tr>
                                <tr>
                                    <td>카드승인금액</td>
                                    <td>BC/KB/SH</td>
                                    <td>월별/자치구/행정도/블록별/업종별 카드승인금액</td>
                                </tr>
                                <tr>
                                    <td>추정매출액</td>
                                    <td>경기도</td>
                                    <td>추정매출액 = 카드승인금액 ÷ 보정비율</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </article>// 추정매출액
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>길단위 상존인구</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : KT 생활인구(내국인, 집계구)를 기반으로 10m 길이 단위로 생성된 길단위 상존인구</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">폭이 넓은 대로를 두 개의 라인으로 분리하고, 보행이 불가능한 지역(도로 중앙, 도로간의 경계, 교차로 등)을 제외</li>
                            <li class="desc">1ha(1만㎡)당 인구밀도와 인구수 두가지 형태로 정보 제공</li>
                        </ul>
                    </div>
                    <div class="half_box_wrap step_box_wrap">
                        <div class="half">
                            <div class="cont_box blue_box">
                                <div class="box_head">1 . 10m단위 도로 SHP 생성</div>
                                <div class="box_body">
                                    <div class="step_wrap">
                                        <div class="step_box">
                                            <div class="step_title">보행가능 도로 추출</div>
                                            <div class="step_desc">
                                                <div class="bold_txt">보행불가 도로 제외</div>
                                                <ul class="desc_wrap">
                                                    <li class="desc">자동차 전용도로 등 보행불가도로 제외</li>
                                                </ul>
                                            </div>
                                        </div>
                                        <div class="step_arrow"><i class="xi-angle-down"></i></div>
                                        <div class="step_box">
                                            <div class="step_title">보행라인 생성</div>
                                            <div class="step_desc float_desc">
                                                <div class="float">
                                                    <div class="bold_txt">도로분류</div>
                                                    <ul class="desc_wrap">
                                                        <li class="desc">광폭도로</li>
                                                        <li class="desc">일반도로</li>
                                                        <li class="desc">소로</li>
                                                    </ul>
                                                </div>
                                                <div class="float">
                                                    <div class="bold_txt">라인생성</div>
                                                    <ul class="desc_wrap">
                                                        <li class="desc">도로 기초라인 생성</li>
                                                        <li class="desc">광폭도로 : 양쪽 두갈래 라인 생성</li>
                                                        <li class="desc">일반도로 : 광폭도로/교차지점 삭제</li>
                                                        <li class="desc">소로 : 일반도로/광폭도로와 교차지점 삭제</li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="step_arrow"><i class="xi-angle-down"></i></div>
                                        <div class="step_box">
                                            <div class="step_title">10m 단위 도로 SHP 생성</div>
                                            <div class="step_desc">
                                                <div class="bold_txt">10m 단위 도로 SHP 생성</div>
                                                <ul class="desc_wrap">
                                                    <li class="desc">각 분류별 도로라인 별 10m 단위 도로 생성</li>
                                                    <li class="desc">중점생성 (도로포인트)</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>// half
                        <div class="half">
                            <div class="cont_box purple_box">
                                <div class="box_head">1 . 10m단위 도로 SHP 생성</div>
                                <div class="box_body">
                                    <div class="step_wrap">
                                        <div class="step_box">
                                            <div class="step_title">집계구 그리드 단위 배분</div>
                                            <div class="step_desc">
                                                <ul class="desc_wrap">
                                                    <li class="desc">각 집계구 영역에 존재하는 그리드의 중심점 수를 계산</li>
                                                    <li class="desc">집계구별 상존인구를 그리드 중심점의 개수로 균등 배분</li>
                                                </ul>
                                            </div>
                                        </div>
                                        <div class="step_arrow"><i class="xi-angle-down"></i></div>
                                        <div class="step_box">
                                            <div class="step_title">도로 포인트별 상존인구 생성</div>
                                            <div class="step_desc">
                                                <ul class="desc_wrap">
                                                    <li class="desc">포인트별 반경 50m내 그리드 상존인구 생성</li>
                                                </ul>
                                            </div>
                                        </div>
                                        <div class="step_arrow"><i class="xi-angle-down"></i></div>
                                        <div class="step_box">
                                            <div class="step_title">세분화 데이터셋 구축</div>
                                            <div class="step_desc">
                                                <ul class="desc_wrap">
                                                    <li class="desc">상존인구 유형별 세분화 데이터세 구축</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>// half
                    </div>
                </article>// 길단위 상존인구
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>건물단위 상존인구</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 기존 길단위 상존인구 배분로직을 수정/보완하여 상존인구를 건물단위로 배분</div>
                        </div>
                    </div>
                    <div class="full_blue_box">
                        <div class="title">건물단위 상존인구 구축</div>
                        <div class="half_box_wrap">
                            <div class="half">
                                <div class="wh_box clear">
                                    <div class="txt_wrap">
                                        <div class="box_title">1단계 (집계구 > 그리드 단위 배분)</div>
                                        <ul class="desc_wrap">
                                            <li class="desc">각 집계구 영역에 존재하는 그리드의<br> 중심점 수를 계산</li>
                                            <li class="desc">집계구별 상존인구를 그리드 <br>중심점의 개수로 균등 배분</li>
                                        </ul>
                                    </div>
                                    <div class="img_wrap"><img src="../../images/common/service_guide1.png"></div>
                                </div>
                            </div>
                            <div class="half">
                                <div class="wh_box clear">
                                    <div class="txt_wrap">
                                        <div class="box_title">2단계 (그리드 > 건물 단위 배분)</div>
                                        <ul class="desc_wrap">
                                            <li class="desc">각 그리드에 존재하는 건물의 <br>연면적을 계산</li>
                                            <li class="desc">그리드별 상존인구를 그리드 내<br> 건물의 연면적 비율에 비례하여 배분</li>
                                        </ul>
                                    </div>
                                    <div class="img_wrap"><img src="../../images/common/service_guide2.png"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </article>// 건물단위 상존인구
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>직장인구</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 국민건강보험공단의 직장건강보험 가입자 기반으로 작성된 직장인구 DB에서 산출하는 정보</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">1ha(1만㎡)당 인구밀도와 인구수 두가지 형태로 정보 제공</li>
                        </ul>
                    </div>
                </article>// 직장인구
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>주거인구</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 서울시 공간정보담당관에서 주민등록주소 기반으로 작성된 상주인구 DB에서 산출하는 정보</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">1ha(1만㎡)당 인구밀도와 인구수 두가지 형태로 정보 제공</li>
                        </ul>
                    </div>
                </article>// 주거인구
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>환산임대료 산식</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 최근 1년간 수집된 서울신용보증재단 내부자료를 기반으로 추정된 값</div>
                        </div>
                        <ul class="desc_wrap">
                            <li class="desc">실제 시세와 오차가 있을 수 있으며, 임대료는 입지, 건물상태, 인지성에 따라 차이가 큼으로 현장 확인 필요</li>
                        </ul>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">환산임대료 산식</div>
                        <div class="box_body"><div class="desc">(보증금 X 12%)/12 + 월세</div></div>
                    </div>
                </article>// 환산임대료 산식
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>가구세대</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 경기도 공간정보담당관에서 제공된 아파트 DB(아파트 세대수) 및 상주인구 DB(전체 세대수) 기반으로 아파트 세대수 및 비아파트 세대수를 산출하는 정보</div>
                        </div>
                    </div>
                    <div class="purple_box">
                        <div class="box_head">가구세대 산식</div>
                        <div class="box_body"><div class="desc">비아파트 세대수 = 전체 세대수 - 아파트 세대수</div></div>
                    </div>
                </article>// 가구세대
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>소득정보</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 국민건강보험공단의 건강보험료 납부 20분위를 기준소득월액으로 환산하여 주거지 기반으로 소득분위(10분위)를 산출하는 정보</div>
                        </div>
                    </div>
                </article>// 소득정보
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>아파트 정보</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 경기도 공간정보담당관에서 제공된 아파트 DB를 기반으로 산출하는 정보</div>
                        </div>
                    </div>
                </article>// 아파트 정보
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>주요 집객시설</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 경기도 소재 관공서, 금융기관, 병원, 학교, 유통점, 문화관광(영화관), 숙박시설, 교통(정류장, 지하철) 등 인구집중 유발시설 정보</div>
                        </div>
                    </div>
                </article>// 주요 집객시설
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>소득정보</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 경기도 교통정책과에서 제공하는 스마트카드 정보를 기반으로 산출하는 정보</div>
                        </div>
                    </div>
                </article>// 교통카드 정보
                <article class="guide_article">
                    <h3 class="cont_title"><i class="xi-down-circle"></i>금융비용 정보</h3>
                    <div class="guide_desc">
                        <div class="define">
                            <i class="xi-angle-right icon"></i><div class="desc">정의 : 소상공인이 사업을 영위하기 위해 차입한 차입금에 대한 이자비용<br> 한국신용정보원과 공동 작성 정보</div>
                        </div>
                    </div>
                    <div class="sky_table_wrap">
                        <table class="sky_table">
                            <colgroup>
                                <col style="width: 20%">
                                <col style="width: 20%">
                                <col style="width: 60%">
                            </colgroup>
                            <thead>
                                <tr>
                                    <th>항목</th>
                                    <th>정보출처</th>
                                    <th>주요내용</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>대출잔액</td>
                                    <td>평균금리</td>
                                    <td>금융비용</td>
                                </tr>
                                <tr>
                                    <td>한국신용정보</td>
                                    <td>한국은행</td>
                                    <td>서울신보</td>
                                </tr>
                                <tr>
                                    <td>월별 대출 잔액</td>
                                    <td>월별 예금은행 가중평균금리(연 단위) (중소기업대출 잔액 기준)</td>
                                    <td>대출잔액 X 평균금리 ÷ 12(월 단위)</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </article>// 금융비용 정보
            </div>
        </div>
     </div> -->
     <!-- 제공정보 안내 : end -->
     
		<!-- 내점포 분석 이용방법 -->
        <div id="pageGuideModal" class="modal_wrap modal_long page_guide_modal" style="display: none;">
            <div class="modal_box">
                <div class="modal_head clear">
                    <div class="head_logo clear">
                        <div class="logo_txt">경기도 상권분석지원 서비스<span class="ft_og">이용방법</span></div>
                    </div>
                    <button type="button" class="modal_close"><img src="../../../images/common/modal_close_wh.png" alt="닫기"></button><!-- // modal_close -->
                </div>
               <div class="modal_cont">
                    <div class="blue_title">내점포 분석 이용방법</div>
                    <div class="page_img"><img src="../../../images/map/page_guide_myStore.png" alt="페이지"></div>
                    <div class="page_guide_box">
                        <ul class="guide_list">
                            <li class="list">
                                <span class="number">1</span>
                                <span class="desc">내점포 검색 : 상호.주소 검색을 통한 빠른 위치 이동 제공</span>
                            </li>
                            <!-- <li class="list">
                                <span class="number">2</span>
                                <span class="desc">생활밀접업종 선택 : 해당 업종선택 -> 업종영역에 삽입</span>
                            </li> -->
                            <li class="list">
                                <span class="number">2</span>
                                <span class="desc">
                                생활밀접업종 선택 : 3개 대분류 서비스 및 118개 생활밀접업종 중 분석하고자 하는 업종 선택<br>
                                더블클릭시 더보기(비교분석) 업종비교 보관함에 저장됨. (최대 3개)
                                </span>
                            </li>
                            <li class="list">
                                <span class="number">3</span>
                                <span class="desc">사용자 영역 선택 : 반경 또는 다각형 선택<br>
                                - 반경: 반경선택 > 검색지점(300m 등) 선택  > 반경클릭 > 영역 설정할 지도 클릭<br>
                                - 다각형 : 다각형선택 > 영역 설정할 지도에 마우스(좌) 클릭하여 ‘포인트 TO 포인트’로 다각형 영역 설정 > 완료시 더블클릭
                                </span>
                            </li>
                            <li class="list">
                                <span class="number">4</span>
                                <span class="desc">지도 선택영역 클릭 -> 상권 분석 리스트 제공</span>
                            </li>
                            <li class="list">
                                <span class="number">5</span>
                                <span class="desc">업종비교 : 업종 보관함에 저장된 업종간의 상호 비교 기능제공 (최대 3개 업종)<br>
                                영역비교 : 사용자 선택 영역간 상호 비교 기능 제공 (최대 3개 영역)
                                </span>
                            </li>
                            <!-- <li class="list">
                                <span class="number">6</span>
                                <span class="desc">상권보고서 : 간략보고서, 종합보고서 제공</span>
                            </li> -->
                            <li class="list">
                                <span class="number">6</span>
                                <span class="desc">
                                보고서 : 분기 및 월간 간략, 종합보고서 제공<br>
                                보관 : 더보기(비교분석) 영역비교 리스트에 저장됨(최대 3개)<br>
                                삭제 : 영역 삭제, 영역비교 리스트에 저장된 정보도 삭제됨
                                </span>
                            </li>
                            <li class="list">
                                <span class="number">7</span>
                                <span class="desc">
                                    선택한 업종 및 영역에 대한 분석(업종/매출/인구/지역/소비분석) 정보 제공
                                </span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
         </div>
         <!-- 내점포 분석 이용방법 : end -->
         
         

	</div>
	<!--//wrap-->
</body>
<script>
	/*상권보고서 팝업 외부영역 클릭시  숨김  */
	$(document).mouseup(function(e) {
		if ($(".analyreport-popup-wrap").has(e.target).length === 0) {
			$(".analyreport-popup-wrap").hide();
		}
	});
</script>
</html>