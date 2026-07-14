var progressCnt = 0;

var shareDt = {
		stdrStr : '',
		stdrHt : '',		//반기
		stdrQt : '',		//분기
		stdrYy : '',		//년
		stdrYm : ''			//년월
	};
		
$(document).ready(function(){
	shareData.callHandler("/common/get_anly_stdr_ym.json", null, function(data){
		if(data != null){
			shareDt.stdrHt = data.stdrHt;
			shareDt.stdrQt = data.stdrQt;
			shareDt.stdrYy = data.stdrYy;
			shareDt.stdrYm = data.stdrYm;
			
			var reltDate = subStrDate(data.stdrYm);
			shareDt.stdrStr = reltDate['year'] + "년 " + reltDate['month'] + "월 기준"
		}
	});
});
	
if (!String.prototype.startsWith) {
	String.prototype.startsWith = function(searchString, position) {
		position = position || 0;
		return this.substr(position, searchString.length) === searchString;
	};
}

if (!String.prototype.endsWith) {
	String.prototype.endsWith = function(searchString, position) {
		var subjectString = this.toString();
		if (typeof position !== 'number' || !isFinite(position)
				|| Math.floor(position) !== position
				|| position > subjectString.length) {
			position = subjectString.length;
		}
		position -= searchString.length;
		var lastIndex = subjectString.indexOf(searchString, position);
		return lastIndex !== -1 && lastIndex === position;
	};
}

if (!String.prototype.includes) {
	String.prototype.includes = function(search, start) {
		'use strict';
		if (typeof start !== 'number') {
			start = 0;
		}

		if (start + search.length > this.length) {
			return false;
		} else {
			return this.indexOf(search, start) !== -1;
		}
	};
}

if (!Array.prototype.reduce) {
	Array.prototype.reduce = function(callback /* , initialValue */) {
		'use strict';
		if (this == null) {
			throw new TypeError(
					'Array.prototype.reduce called on null or undefined');
		}
		if (typeof callback !== 'function') {
			throw new TypeError(callback + ' is not a function');
		}
		var t = Object(this), len = t.length >>> 0, k = 0, value;
		if (arguments.length == 2) {
			value = arguments[1];
		} else {
			while (k < len && !(k in t)) {
				k++;
			}
			if (k >= len) {
				throw new TypeError(
						'Reduce of empty array with no initial value');
			}
			value = t[k++];
		}
		for (; k < len; k++) {
			if (k in t) {
				value = callback(value, t[k], k, t);
			}
		}
		return value;
	};
}
if (!Array.prototype.map) {
	Array.prototype.map = function(callback, thisArg) {
		var T, A, k;

		if (this == null) {
			throw new TypeError(' this is null or not defined');
		}

		var O = Object(this);

		var len = O.length >>> 0;

		if (typeof callback !== 'function') {
			throw new TypeError(callback + ' is not a function');
		}

		if (arguments.length > 1) {
			T = thisArg;
		}

		A = new Array(len);

		k = 0;

		while (k < len) {

			var kValue, mappedValue;

			if (k in O) {

				kValue = O[k];

				mappedValue = callback.call(T, kValue, k, O);

				A[k] = mappedValue;
			}
			k++;
		}

		return A;
	};
}

if (!String.prototype.trim) {
	String.prototype.trim = function() {
		return this.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '');
	};
}

if (!Array.prototype.filter) {
	  Array.prototype.filter = function(fun/*, thisArg*/) {
	    'use strict';

	    if (this === void 0 || this === null) {
	      throw new TypeError();
	    }

	    var t = Object(this);
	    var len = t.length >>> 0;
	    if (typeof fun !== 'function') {
	      throw new TypeError();
	    }

	    var res = [];
	    var thisArg = arguments.length >= 2 ? arguments[1] : void 0;
	    for (var i = 0; i < len; i++) {
	      if (i in t) {
	        var val = t[i];

	        if (fun.call(thisArg, val, i, t)) {
	          res.push(val);
	        }
	      }
	    }

	    return res;
	  };
	}

if (typeof Object.create != 'function') {
	Object.create = (function(undefined) {
		var Temp = function() {
		};
		return function(prototype, propertiesObject) {
			if (prototype !== Object(prototype) && prototype !== null) {
				throw TypeError('Argument must be an object, or null');
			}
			Temp.prototype = prototype || {};
			if (propertiesObject !== undefined) {
				Object.defineProperties(Temp.prototype, propertiesObject);
			}
			var result = new Temp();
			Temp.prototype = null;
			// Object.create(null)인 경우 모방
			if (prototype === null) {
				result.__proto__ = null;
			}
			return result;
		};
	})();
}

$.urlParam = function(name) {
	var results = new RegExp("[\?&]" + name + "=([^&#]*)").exec(window.location.href);
	if (results == null) {
		return null;
	} else {
		return results[1] || 0;
	}
}
var evtMng = $({}); 

function hideLoading(){
	$("#progress").hide();
}

var shareData = {
	showprogressbar : function(){
//		console.log('ShowProgressBar cnt : ', progressCnt);
		if(progressCnt < 2){
			$("#progress").show();
//			console.log("!!showProgress!!")
		}
	},
	hideprogressbar : function(){
//		console.log('HideProgressBar cnt : ', progressCnt);
		if(progressCnt == 0){
			$("#progress").hide();
//			console.log("!!hideProgress!!")
		}
	},
	
	callAjax : function(url, data, sucCallback, errCallBack){
		$.ajax({
			url : url,
			data : data,
			type : "POST",
			dataType : "json",
			contentType : "application/x-www-form-urlencoded",
			success : function(resp, url) {
				sucCallback(resp, url);
			},
			error : function(resp, status, err) {
				errCallBack(resp);
			}
		});
	},
	
	callHandler : function(url, data, callback, contentType, dataType, type, error, syncYn) {
		"use strict";
		var retData;
		type = type == "PUT" ? "POST" : type || "POST";
		dataType = dataType || 'json';
		contentType = contentType || "application/x-www-form-urlencoded";
		
		progressCnt++;
		this.showprogressbar();
		$.ajax({
			url : url,
			data : data,
			type : type,
			dataType : dataType || "json",
			async : syncYn == 'Y' ? false : true,
			contentType : contentType,
			success : function(resp, url) {
				progressCnt --;
				shareData.hideprogressbar();								
				if (typeof callback === "function") {
					callback(resp, url);
					return;
				} else {
					retData = resp;
				}
			},
			error : function(resp, status, err) {
				progressCnt --;
				shareData.hideprogressbar();
				if (typeof error === "function") {
					error(resp.responseText);
					return;
				} else {
					if (resp.responseText.indexOf("java.lang.Exception") > 0) {
						var respStr = resp.responseText;
						var tmpStr = respStr.substring(respStr.indexOf("java.lang.Exception"), respStr.length);
						var errStr = tmpStr.substring(tmpStr.indexOf(":") + 1, tmpStr.indexOf("<"));
							//console.log(errStr);
						}
					}

				var contentType = resp.getResponseHeader("Content-Type");
//              if (dataType == 'json' && resp.status === 200 && contentType.toLowerCase().indexOf("text/html") >= 0) {
				if (dataType == 'json' && resp.status === 200 && contentType.toLowerCase().indexOf("text/html") >= 0) {
                  // assume that our login has expired - reload our current page
                  //window.location.reload();
					retData = resp.responseText;
				}
			}
		});
		return retData;
	},
	callAsync : function(url, data, callback) {
		return this.callHandler(url, data, callback, null, null, null, null, 'Y');
	}
}


function drawDetailPieChart(options){
	var chart = AmCharts.makeChart( options.divid, {
		  "type": "pie",
		  "theme": "light",
		  "dataProvider": options.data,
		  "valueField": options.valueField,
		  "titleField": options.titleField,
		   "balloon":{
		   "fixedPosition":true
		  }
		} );
	return chart;
}

function drawRadarChart(options) {
	var defaultOptions = $.extend({}, options);
	var divid = defaultOptions.divid || "chart";
	var categoryField = defaultOptions.categoryField || "cat1";
	var valueField = defaultOptions.valueField || "value";
	var data = defaultOptions.data || [];

	var myChart = new AmCharts.AmRadarChart();
	myChart.dataProvider = data;
	myChart.categoryField = categoryField;
	myChart.startDuration = 2;
	myChart.valueAxes = [{"maximum":10, "minimum":0}];

	var graph = new AmCharts.AmGraph();
	graph.bullet = "circle";
	graph.balloonText = "[[date]]<br/>[[name]] : [[value]]";
	graph.lineColor = "#5B9BD5";
	graph.bulletSize = 5;
	graph.lineThickness = 1;
	graph.valueField = valueField;

	myChart.addGraph(graph);
	myChart.write(document.getElementById(divid));
}

function drawMultiColumnMixLine (options){
	var defaultOptions = $.extend({},options);
	var graphInfo = defaultOptions.graphInfo || [];
	var stacked = defaultOptions.stacked || false;
	var divid = defaultOptions.divid || "chart";
	var categoryField = defaultOptions.categoryField || "cat1";
	var defData = defaultOptions.data || [];
	var data = [];
	var rotate = defaultOptions.rotate || false;
	var newStack = defaultOptions.newStack || false;
	var legendYn;
	var legendPosition = defaultOptions.legendPosition || "right";
	var legendMaxColumns = defaultOptions.legendMaxColumns || 1;
		
	if(typeof defaultOptions.legendYn ==  undefined || defaultOptions.legendYn == null){
		legendYn = true;
	}else{
		legendYn = defaultOptions.legendYn;
	}
		
	var graphs = [];
	
	//데이터를 양쪽으로 보이게 하기 위해서 특정 순서 값을 음수로 만들기
	if(newStack){
		for(var i=0; i<defData.length; i++){
			var idx = 0;
			var idx2 = 0;
			var temp = {};
			for(key in defData[i]){
				if(!isNaN(defData[i][key]) && (idx == 0 || idx == 1) && key != categoryField){
					idx++;
					temp[key] = defData[i][key]*-1;
				}else{
					temp[key] = defData[i][key];
				}
		    }
			data.push(temp);
		}
	}else{
		data = defData;
	}
	
	for (var i = 0 ;i<graphInfo.length;i++){
		
		var grp = {
			"balloonText": "<b>[[title]]</b><br><span style='font-size:14px'>[[category]]: <b>[[value]]</b></span>",
	        "title": graphInfo[i].title,
	        "valueField": graphInfo[i].valueField,
	        "type": graphInfo[i].type,
	        "valueAxis": graphInfo[i].axisPos
	    }
		var ext = {};
		if(graphInfo[i].type == "column"){
			ext = {
		        "fillAlphas": 1,
		        "lineAlpha": 0.3,
		        "labelText": "[[value]]"
			};
			if(newStack && i!=0 && i%2 == 0)
				ext.newStack = true;
		}else{
			ext = {
			    "bullet": "round",
			    "bulletBorderAlpha": 1,
			    "bulletSize": 7,
			    "bulletColor": "#FFFFFF",
			    "useLineColorForBulletBorder": true,
			    "lineThickness": 2,
			    "lineAlpha": 1
			};		
		}
		grp = $.extend(grp,ext);
		
		if(newStack){
			var valueAbs = {
				"balloonFunction": function(item) {
			    	return "<b>"+item.graph.title+"</b><br><span style='font-size:14px'>"+item.category+": <b>"+Math.abs(item.values.value)+"</b></span>";
			    },
				"labelFunction": function(item) {
			      return Math.abs(item.values.value);
			    }
			}
			grp = $.extend(grp, valueAbs);
		}
		
		graphs.push(grp);
	}
	
	var v1Axis = {
        "id":"left",
        "axisAlpha": 0.3,
        "gridAlpha": 0.3
    };
	var v2Axis = {
        "id":"right",
        "axisAlpha": 0.3,
        "gridAlpha": 0,
        "position": "right"
    };
    if(stacked)
    	v1Axis.stackType = "regular";

    if(newStack){
    	v1Axis.labelFunction = function(value) {
    		return Math.abs(value);
    	}
    }
    
	var valueAxes = [v1Axis,v2Axis];
	var chartDataLegend;
	if(legendYn){
		chartDataLegend = { 
			"horizontalGap": 10,
			"maxColumns": legendMaxColumns,
			"position": legendPosition,
			"useGraphSettings": true,
			"markerSize": 10
		}
			
	}else{
		chartDataLegend = null;
	}
	
	var chartData = {
		    "type": "serial",
			"theme": "light",
			"rotate" : rotate,
		    "dataProvider": data,
		    "valueAxes": valueAxes,
		    "graphs": graphs,
		    "categoryField": categoryField,
		    "legend" : chartDataLegend,
		    "categoryAxis": {
		        "gridPosition": "start",
		        "axisAlpha": 0,
		        "gridAlpha": 0,
		        "position": "left"
		    },
		    "export": {
		    	"enabled": true
		     }
		};
	
	
	var chart = AmCharts.makeChart(divid, chartData);
	
	return chart;
}

function zoomableLineChart(options){
	var chartGraphs = [];
	var divid = options.divid;
	var dataProvider = options.data;
	var type = options.type || 'serial';
	var theme = options.theme || "light";
	var marginRight = options.marginRight || 80;
	var autoMarginOffset = options.autoMarginOffset || 20;
	var marginTop = options.marginTop || 7;
	var exportAble = options.exportAble;
	var categoryField = options.categoryField;
	if(exportAble == false || typeof exportAble == "undefinded"){
		exportAble = false;
	}else
		exportAble = true;
	var graphs = options.graphInfo;
	
	var graphData = [];
	for(var i=0; i < graphs.length; i++){
		
		var grp = {
			'id' : graphs[i]["valueField"],
			//'balloonText': "[[value]]",
			"bulletBorderAlpha": 1,
	        "bulletColor": "#FFFFFF",
	        "hideBulletsCount": 50,
	        "title" : graphs[i]["title"],
	        "valueField" : graphs[i]["valueField"],
			"useLineColorForBulletBorder": true
		}
		graphData.push(grp);
	}
	
	var chart = AmCharts.makeChart(divid,{
		"type": type,
	    "theme": theme,
	    "marginRight": marginRight,
	    "autoMarginOffset": autoMarginOffset,
	    "marginTop": marginTop,
	    "dataProvider": dataProvider,
	    "valueAxes": [{
	        "axisAlpha": 0.2,
	        "dashLength": 1,
	        "position": "left"
	    }],
	    "mouseWheelZoomEnabled": true,
	    "graphs": graphData,
	    "chartScrollbar": {
	        "autoGridCount": true,
	        "graph": "1grp",
	        "scrollbarHeight": 40
	    },
	    "chartCursor": {
	       "limitToGraph":"1grp"
	    },
	    'legend' : { 
				"horizontalGap": 10,
				"maxColumns": '4',
				"position": 'bottom',
				"useGraphSettings": true,
				"markerSize": 10
			},
	    "categoryField": categoryField,
	    "categoryAxis": {
//	        "parseDates": true,
	        "axisColor": "#DADADA",
	        "dashLength": 1,
	        "minorGridEnabled": true
	    },
	    "export": {
	        "enabled": exportAble
	    }
	}); 	
	chart.addListener("rendered", zoomChart);

	// this method is called when chart is first inited as we listen for "rendered" event
	function zoomChart() {
	    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
	    chart.zoomToIndexes(dataProvider.length - 40, dataProvider.length - 1);
	}
	zoomChart();	
	return chart;
	
}

// ClipReport Open Function
// reportName = "리포트 파일명", jsonParameter = "리포트 쿼리용 JSON 형식 파라미터"
function openReport(reportName, jsonParameter) {

//	 alert("jsonParameter.length = " + Object.keys(jsonParameter).length);
//	 alert("jsonParameter = " + JSON.stringify(jsonParameter));
	// 리포트 폼데이터 세팅
	var formData = "<form id='rptPstBx' name='rptPstBx' action='/ClipReport4/printReport.jsp' method='post' target='blank' accept-charset='UTF-8'>";
			formData += "<input type='hidden' name='rptName' value='" + reportName + "'>";
	for ( var key in jsonParameter) {
		formData += "<input type='hidden' name='" + key + "' value='" + jsonParameter[key] + "'>";
	}	
	formData += "</form>";	

//console.log(formData);
	$("body").append(formData);	
	$("#rptPstBx").submit();	
	$("#rptPstBx").remove();
}

function dataURIToBlob(dataURI) {
	var byteString = atob(dataURI.split(',')[1]);
    var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0]
    var ab = new ArrayBuffer(byteString.length);
    var ia = new Uint8Array(ab);
    for (var i = 0; i < byteString.length; i++)
    {
        ia[i] = byteString.charCodeAt(i);
    }    
    var bb = new Blob([ab], { "type": mimeString });
    return bb;
}

function subStrDate(date){
	var result = {};
	if(date.length == 6){
		if(date.substring(4,5) == "Q"){					//분기
			result['year'] = date.substring(0,4);
			result['month'] = date.substring(5,6);
		}else if(date.substring(4,5) == 'H'){			//반기
			result['year'] = date.substring(0,4);
			
			if(date.substring(5,6) == '1'){						//상반기
				result['half'] = "06";
			}else if(date.substring(5,6) == '2'){				//하반기
				result['half'] = "12";
			}
			
		}else{
			result['year'] = date.substring(0,4);
			result['month'] = date.substring(4,6);
		}
	}
	return result;
}



Date.prototype.format = function(f) {
    if (!this.valueOf()) return " ";
 
    var weekName = ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"];
    var d = this;
     
    return f.replace(/(yyyy|yy|MM|dd|E|hh|mm|ss|a\/p)/gi, function($1) {
        switch ($1) {
            case "yyyy": return d.getFullYear();
            case "yy": return (d.getFullYear() % 1000).zf(2);
            case "MM": return (d.getMonth() + 1).zf(2);
            case "dd": return d.getDate().zf(2);
            case "E": return weekName[d.getDay()];
            case "HH": return d.getHours().zf(2);
            case "hh": return ((h = d.getHours() % 12) ? h : 12).zf(2);
            case "mm": return d.getMinutes().zf(2);
            case "ss": return d.getSeconds().zf(2);
            case "a/p": return d.getHours() < 12 ? "오전" : "오후";
            default: return $1;
        }
    });
};
String.prototype.string = function(len){var s = '', i = 0; while (i++ < len) { s += this; } return s;};
String.prototype.zf = function(len){return "0".string(len - this.length) + this;};
Number.prototype.zf = function(len){return this.toString().zf(len);};

//숫자 타입에서 쓸 수 있도록 format() 함수 추가
Number.prototype.comma = function(){
	if(!Ol_Util_Com.checkObjEmpty(this)) {
		if(this==0) return 0;
		 
	    var reg = /(^[+-]?\d+)(\d{3})/;
	    var n = (this + '');
	 
	    while (reg.test(n)) n = n.replace(reg, '$1' + ',' + '$2');
	 
	    return n;	
	}else {
		return 0;
	}
};
 
// 문자열 타입에서 쓸 수 있도록 format() 함수 추가
String.prototype.comma = function(){
	if(!Ol_Util_Com.checkObjEmpty(this)) {
		var num = parseFloat(this);
	    if( isNaN(num) ) return "0";	 
	    return num.comma();	
	}else {
		return 0;
	}
};

String.prototype.stdrQt = function(){
	if(this.length != 6)
		return this;
	else if(this.startsWith('\''))
		return this;
	else
		return '\''+this.substring(2,4)+" "+this.substring(4,6);
}
String.prototype.stdrHt = function(){
	if(this.length != 6)
		return this;
	var year = this.substring(2,4);
	if(isNaN(year)){
		return this;
	}
	var bungi = this.substring(4,6) == 'H1'?'상반기':
				this.substring(4,6) == 'H2'?'하반기' : this.substring(4,6);
	return '\''+year +" "+ bungi;
}
String.prototype.stdrYm = function(){
	if(this.length != 6)
		return this;
	return this.substring(4,6)+'월';
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

var obCompare = function(a, b){
  var stack = [[a,b]], curr, i;
  while(curr = stack.pop()){
    a = curr[0], b = curr[1];
    if((!a || typeof a != "object") && a !== b) return false;
    if(a instanceof Array){
      if(!(b instanceof Array) || (i = a.length) != b.length) return false;
      while(i--) stack.push([a[i], b[i]]);
    }else{
      if(Object.keys(a).length != Object.keys(b).length) return false;
      for(i in a) if(a.hasOwnProperty(i)) stack.push([a[i], b[i]]);
    }
  }
  return true;
};
