

//Form submission
function confirmSubmit(msg){
	return confirm(msg);
}

//Progress Bars
function createProgressBar(div,slotsUsed,slotsAvailable,showtext){

//    $(div).progressBar({ max: 100, textFormat: 'fraction', callback: function(data) { if (data.running_value == data.value) { alert("Callback example: Target reached!"); } }} );
	//$(div).progressBar("88",{max:100})
	$(div).progressBar(slotsUsed,
		{
			max:slotsAvailable,	
			textFormat:'fraction',
			showText:showtext,
			boxImage:'/static/media/images/progressbar.gif',
			barImage: {
				0:  '/static/media/images/progressbg_black.gif',
				(slotsAvailable*0.2):  '/static/media/images/progressbg_green.gif',
				(slotsAvailable*0.45):  '/static/media/images/progressbg_orange.gif',
				(slotsAvailable*0.8):  '/static/media/images/progressbg_red.gif',
			},
		}
	);
}

//Menu
$(document).ready(function(){
    	$(".menuimg,.submenuimg")
        	.mouseover(function() { 
	            var src = $(this).attr("src").replace("dark", "light");
    	        $(this).attr("src", src);
        	})
        	.mouseout(function() {
            	var src = $(this).attr("src").replace("light", "dark");
            	$(this).attr("src", src);
       	 	});
	});


	$(document).ready(function(){
		$(".experiments_sub_menu").hide();
		$("#experiments")
			.click(function() {
				$(".fs_req_sub_menu").hide();
				$(".admin_fs_sub_menu").hide();
				$(".experiments_sub_menu").toggle('normal');
				$(".profile_sub_menu").hide();
				$(".website_sub_menu").hide();
			});
	});

	$(document).ready(function(){
		$(".profile_sub_menu").hide();
		$("#profile")
			.click(function() {
				$(".profile_sub_menu").toggle('normal');
			});
	});


