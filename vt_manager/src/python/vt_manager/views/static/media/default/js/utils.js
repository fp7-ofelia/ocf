

//Form submission
function confirmSubmit(msg){
	return confirm(msg);
}

//Progress Bars
function createProgressBar(div,slotsUsed,slotsAvailable,showtext){

//    $(div).progressBar({ max: 100, textFormat: 'fraction', callback: function(data) { if (data.running_value == data.value) { alert("Callback example: Target reached!"); } }} );
	//$(div).progressBar("88",{max:100})
	greenLimit = Math.round(0.0*slotsAvailable);
	blackLimit = Math.round(0.4*slotsAvailable);
	orangeLimit = Math.round(0.6*slotsAvailable);
	redLimit = parseInt(Math.round(0.7*slotsAvailable));
	
	//Create barImage
	barImage = {};
	barImage[greenLimit] =  '/static/media/default/images/progressbg_green.gif';
	barImage[blackLimit] =  '/static/media/default/images/progressbg_black.gif';
	barImage[orangeLimit] = '/static/media/default/images/progressbg_orange.gif';
	barImage[redLimit] =  '/static/media/default/images/progressbg_red.gif';

//	alert(dump(barImage));

	$(div).progressBar(slotsUsed,
		{
			max:slotsAvailable,	
			textFormat:'fraction',
			showText: showtext,
			boxImage: '/static/media/default/images/progressbar.gif',
			barImage: barImage ,
		}
	);
}
/**
 * Function : dump()
 * Arguments: The data - array,hash(associative array),object
 *    The level - OPTIONAL
 * Returns  : The textual representation of the array.
 * This function was inspired by the print_r function of PHP.
 * This will accept some data as the argument and return a
 * text that will be a more readable version of the
 * array/hash/object that is given.
 * Docs: http://www.openjs.com/scripts/others/dump_function_php_print_r.php
 */
function dump(arr,level) {
	var dumped_text = "";
	if(!level) level = 0;
	
	//The padding given at the beginning of the line.
	var level_padding = "";
	for(var j=0;j<level+1;j++) level_padding += "    ";
	
	if(typeof(arr) == 'object') { //Array/Hashes/Objects 
		for(var item in arr) {
			var value = arr[item];
			
			if(typeof(value) == 'object') { //If it is an array,
				dumped_text += level_padding + "'" + item + "' ...\n";
				dumped_text += dump(value,level+1);
			} else {
				dumped_text += level_padding + "'" + item + "' => \"" + value + "\"\n";
			}
		}
	} else { //Stings/Chars/Numbers etc.
		dumped_text = "===>"+arr+"<===("+typeof(arr)+")";
	}
	return dumped_text;
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


