
function textinPopup(H,W,ID){ 
	$.get("/ori/common/popup.php?f=textinPopup&ID="+ID,
	function(data){
        popup(H,W,data);
	});
}

function pageinPopup(H,W,page){ 
alert(page);
$.get(page,
	function(data){
alert(page);
        popup(H,W,data);
	});
}

/***************************/
//@Author: Adrian "yEnS" Mato Gondelle
//@website: www.yensdesign.com
//@email: yensamg@gmail.com
//@license: Feel free to use it, but keep this credits please!					
/***************************/

//SETTING UP OUR POPUP
//0 means disabled; 1 means enabled;
var popupStatus = 0;

function popup(H, W, data){
		//centering with css
		//load popup
		centerPopup(H, W);
		loadPopup(data);
	//CLOSING POPUP
	//Click the x event!
	$("#popupwindowClose").click(function(){
		disablePopup();
	});
	//Click out event!
	$("#popupBackground").click(function(){
		disablePopup();
	});
	//Press Escape event!
	$(document).keypress(function(e){
		if(e.keyCode==27 && popupStatus==1){
			disablePopup();
		}
	});
}
//loading popup with jQuery magic!
function loadPopup(data){

	//loads popup only if it is disabled
	if(popupStatus==0){
		$("#popupBackground").css({
			"opacity": "0.7"
		});
		$("#popupBackground").fadeIn("slow");
		$("#popupWindow").html("<div id=popupWindowContents>"+data+"</div>");
		$("#popupWindow").prepend("<div id=popupwindowClose>&times</div>");
		$("#popupWindow")
			.fadeIn("slow");
		popupStatus = 1;
	}
}

//disabling popup with jQuery magic!
function disablePopup(){
	//disables popup only if it is enabled
	if(popupStatus==1){
		$("#popupBackground").fadeOut("slow");
		$("#popupWindow").fadeOut("slow");
		$("#popupWindowContents").fadeOut("slow");
		popupStatus = 0;
	}
}


    
 function centerPopup(H, W){
	//request data for centering
	if(H>1){
  	    H=Math.min(0.8, H/$(window).height());
	}
	if(W>1){
	    W=Math.min(0.8, W/$(window).width());
	}
    popupheight=$(window).height()*H;
    popupwidth=$(window).width()*W;
	
	$("#popupWindow").css({
		"height":popupheight,
		"width":popupwidth,
		"position": "fixed",
		"top": $(window).height()*(1-H)/2,
		"left": $(window).width()*(1-W)/2,
	});

    $("#popupwindowClose").css({
        "margin-left": $(window).height()*(1-H)/2,
    });
//$(function(){  
	$("#popupWindowContents").css({
		"height":popupheight,
		"width":popupwidth,
		"position": "fixed",
		"top": $(window).height()*(1-H)/2,
		"left": $(window).width()*(1-W)/2,
		"background-color":"white"
	});
//});
	//only need force for IE6
	$("#popupBackground").css({
		"height": $(window).height()
	});
}       
   
