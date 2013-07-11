/* Zooming routines */

cur_zoom = 1;
zoom_in_active = false;
zoom_out_active = false;

function zoomIn(zoom){
    if(zoom_in_active == false && zoom_out_active == false){
	$("#link_zoom_in img").css("background-color", "#666");
	cur_zoom = cur_zoom + zoom;
	zoom_in_active = true;
    }

    else if(zoom_in_active == true){
	cur_zoom = cur_zoom - zoom;
	$("#link_zoom_in img").css("background-color", "");
	$("#target, svg, g").css("cursor", "move");
	zoom_in_active = false;
    }

    else{
	cur_zoom = cur_zoom + zoom + zoom;
	$("#link_zoom_out img").css("background-color", "");
	$("#link_zoom_in img").css("background-color", "#666");
	zoom_out_active = false;
	zoom_in_active = true;
    }
}

function zoomOut(zoom){
    if(zoom_out_active == false && zoom_in_active == false){
	if((cur_zoom - zoom) >0){
	    $("#link_zoom_out img").css("background-color", "#666");
            cur_zoom = cur_zoom - zoom;
	    zoom_out_active = true;
        }
	else{
	    $("#target, svg, g").css("cursor", "move");
	}
    }	
    else if(zoom_out_active == true){
	cur_zoom = cur_zoom + zoom;
	$("#link_zoom_out img").css("background-color", "");
	$("#target, svg, g").css("cursor", "move");
	zoom_out_active = false;
    }

    else{
	cur_zoom = cur_zoom - zoom;
	zoom_out_active = false;
        $("#link_zoom_in img").css("background-color", "");
	if((cur_zoom - zoom) > 0){
	    $("#link_zoom_out img").css("background-color", "#666");
	    zoom_out_active = true;
	}
	else{
	    $("#target, svg, g").css("cursor", "move");
	}
    }
}

$("#link_zoom_in").click(function(){
  $("#target, svg, g").css("cursor", "url({%url img_media 'zoomin.png' %}),auto");
});

$("#link_zoom_out").click(function(){
  $("#target, svg, g").css("cursor", "url({%url img_media 'zoomout.png' %}),auto" );
});


