$(document).ready(function() {
// Drag&Drop variables and functions
        
                var rd = REDIPS.drag;
                rd.init();
                
                rd.myhandler_cloned = function(target_cell){
                        var elem = document.getElementById(rd.obj.id);
                        var elemID = rd.obj.id;
                        if (elemID.substr(0,7) == "operand"){
                                elem.innerHTML = '<div class="xcloser"><a href="javascript:elem_delete(\''+elemID+'\')">&#10006;</a></div>' + "("+ elem.innerHTML+ ")";
                        }
                        else {
                                elem.innerHTML = elem.innerHTML + '<div class="xcloser"><a href="javascript:elem_delete(\''+elemID+'\')">&#10006;</a></div>';
                        };
			$("#"+rd.obj.id).toggleClass("selected");
                };

                rd.myhandler_dropped = function(target_cell){

                        target_cell.setAttribute("class", "single condcell");
                        var row = document.getElementById("cond_row");
                        // get target and source position (method returns positions as array)
                        // pos[0] - target table index
                        // pos[1] - target row index
                        // pos[2] - target cell (column) index
                        // pos[3] - source table index
                        // pos[4] - source row index
                        // pos[5] - source cell (column) index
                        var pos = rd.get_position();
			
                        if(pos[0] != pos[3]){
                                row.insertCell(target_cell.cellIndex).setAttribute("class", "single condcell blankCell");
                                row.insertCell(target_cell.cellIndex+1).setAttribute("class", "single condcell blankCell");
                        }
                        else if(pos[2] < pos[5]){
                                if(pos[3] != 0) {
                                        row.deleteCell(pos[5]+1);
                                        row.deleteCell(pos[5]);
                                };
                                row.insertCell(target_cell.cellIndex).setAttribute("class", "single condcell blankCell");
                                row.insertCell(target_cell.cellIndex+1).setAttribute("class", "single condcell blankCell");
                        }
                        else if(pos[2] > pos[5]){
                                row.insertCell(target_cell.cellIndex).setAttribute("class", "single condcell blankCell");
                                row.insertCell(target_cell.cellIndex+1).setAttribute("class", "single condcell blankCell");
                                if(pos[3] != 0) {
                                        row.deleteCell(pos[5]+1);
                                        row.deleteCell(pos[5]);
                                };
                        };
                        change_width();
                        cond_assign();
                };


                // This function allows to clone any number of elements and make them only droppable in the correct cell
                rd.myhandler_moved = function(){
                        $("#"+rd.obj.id).toggleClass("selected");
                };

                rd.myhandler_clicked = function (current){
                        if (current.parentNode.id == "cond_row"){
                                $("#"+rd.obj.id).toggleClass("selected");
                        };
                };

		rd.myhandler_dropped_before = function(){
		if (!checkMaxWidth()) {
			document.getElementById('exceptions').textContent = "WARNING. The Drag zone cannot admit more conditions. Please group some conditions and try again.";
			return false;
		}
		else {
			document.getElementById('exceptions').textContent = "";
		};
        };
}); // End document.ready()

        removeAdjacentCells = function(source_cell){
                var row = document.getElementById("cond_row");
                row.deleteCell(source_cell.cellIndex+1);
                row.deleteCell(source_cell.cellIndex);
        };

        cond_group = function(){
                var group = "";
                var text = "";
                if ( $("div.selected").length < 3 || $("div.selected").length > 4){
                        document.getElementById("exceptions").textContent = "Invalid condition: Missing operator, left condition or right condition";
                        return;
                }
                else if ($("div.selected").length == 3){
                        if ($("div.selected")[0].id.substr(0,7) == "operand" || $("div.selected")[0].id.substr(0,9) == "comp_cond"){
                                if ($("div.selected")[0].innerText == null){
                                        group =  $("div.selected")[0].textContent.replace("✖","");
                                }
                                else {
                                        group =  $("div.selected")[0].innerText.replace("✖","");
                                };
                        }
                        else {
                                document.getElementById("exceptions").textContent = "Invalid condition: Missing operator, left condition or right condition";
                                return;
                        };

                        if ($("div.selected")[1].id.substr(0,8) == "operator"){
                                if ($("div.selected")[1].innerText == null){
                                        text = $("div.selected")[1].textContent.replace("✖","");
                                }
                                else {
                                        text = $("div.selected")[1].innerText.replace("✖","");
                                };
                                group = "(" + group + ") " + text + " "; 
                        }
                        else {
                                document.getElementById("exceptions").textContent = "Invalid condition: Missing operator, left condition or right condition";
                                return;
                        };

                        if ($("div.selected")[2].id.substr(0,7) == "operand" || $("div.selected")[2].id.substr(0,9) == "comp_cond"){
                                if ($("div.selected")[2].innerText == null){
                                        text = $("div.selected")[2].textContent.replace("✖","");
                                }
                                else {
                                        text = $("div.selected")[2].innerText.replace("✖","");
                                };
                                group = group + "(" + text + ")";
                        }
                        else {
                                document.getElementById("exceptions").textContent = "Invalid condition: Missing operator, left condition or right condition";
                                return;
                        };
                        group = "(" + group + ")"

                        $("div.selected")[0].setAttribute('id',$("div.selected")[0].getAttribute('id'));
                        $("div.selected")[0].innerHTML = '<div class="xcloser"><A href="javascript:elem_delete(\''+$("div.selected")[0].getAttribute('id')+'\')">&#10006;</A></div>' + group;
                        $("div.selected")[0].setAttribute('className', 'drag operand');
                        elem_delete($("div.selected")[2].getAttribute('id'));
                        elem_delete($("div.selected")[1].getAttribute('id'));

                } 
                else if ($("div.selected").length == 4){
                        if ($("div.selected")[0].id.substr(0,3) == "not"){
                                if ($("div.selected")[0].innerText == null){
                                        text = $("div.selected")[0].textContent.replace("✖","");
                                }
                                else {
                                        text = $("div.selected")[0].innerText.replace("✖","");
                                };
                                group = text + " ";
                        }
                        else {
                                document.getElementById("exceptions").textContent = "Invalid condition: Missing operator, left condition or right condition";
                                return;
                        };

                        if ($("div.selected")[1].id.substr(0,7) == "operand" || $("div.selected")[1].id.substr(0,9) == "comp_cond"){
                                if ($("div.selected")[1].innerText == null){
                                        text = $("div.selected")[1].textContent.replace("✖","");
                                }
                                else {
                                        text = $("div.selected")[1].innerText.replace("✖","");
                                };
                                group = group + "(" + text + ")";
                        }
                        else {
                                document.getElementById("exceptions").textContent = "Invalid condition: Missing operator, left condition or right condition";
                                return;
                        };

                        if ($("div.selected")[2].id.substr(0,8) == "operator"){
                                if ($("div.selected")[2].innerText == null){
                                        text = $("div.selected")[2].textContent.replace("✖","");
                                }
                                else {
                                        text = $("div.selected")[2].innerText.replace("✖","");
                                };
                                group = group +" "+ text + " "; 
                        }
                        else {
                                document.getElementById("exceptions").textContent = "Invalid condition: Missing operator, left condition or right condition";
                                return;
                        };
                        if ($("div.selected")[3].id.substr(0,7) == "operand" || $("div.selected")[3].id.substr(0,9) == "comp_cond"){
                                if ($("div.selected")[3].innerText == null){
                                        text = $("div.selected")[3].textContent.replace("✖","");
                                }
                                else {
                                        text = $("div.selected")[3].innerText.replace("✖","");
                                };
                                group = "(" + group + "(" + text + ") )";
                        }
                        else {
                                document.getElementById("exceptions").textContent = "Invalid condition: Missing operator, left condition or right condition";
                                return;
                        };
                        $("div.selected")[1].setAttribute('id',$("div.selected")[1].getAttribute('id'));
                        $("div.selected")[1].innerHTML = '<div class="xcloser"><A href="javascript:elem_delete(\''+$("div.selected")[1].getAttribute('id')+'\')">&#10006;</A></div>' + group;
                        $("div.selected")[1].setAttribute('className', 'drag operand');
                        elem_delete($("div.selected")[3].getAttribute('id'));
                        elem_delete($("div.selected")[2].getAttribute('id'));
                        elem_delete($("div.selected")[0].getAttribute('id'));
                };
//              REDIPS.drag.init();
                rd.init();
                cond_assign();
        };
        cond_assign = function(){
                var row = document.getElementById("cond_row");
                var text = "";
                var content = "";
                for (var i = 0; i < row.cells.length; i++){
                        if (row.cells[i].innerText == null){
                                content = row.cells[i].textContent.replace("✖","").replace("\n","");
                        }
                        else {
                                content = row.cells[i].innerText.replace("✖","").replace("\n","")
                        };
                        if (content.length > 0){
                                text = text + content + " ";
                        };
                };
                text = text.substr(0,text.length-1);
                document.getElementById("finalCond").value = text;
                displayRule();
        };

        cond_limpia = function(){
                for ( var i = 0; i < arguments.length; i++ ){
                        REDIPS.drag.delete_object(arguments[i]);
                };
        };

        elem_delete = function(elemID){
                cell = document.getElementById(elemID).parentNode;
                removeAdjacentCells(cell);
                cond_limpia(elemID);
                change_width();
                cond_assign();
        };

        change_width = function(){
                var row = document.getElementById("cond_row");
                width = 100/row.cells.length;
                for (var i = 0; i < row.cells.length; i++){
                        row.cells[i].setAttribute("style","width:"+width+"%")
                };
        };

	check_cond_grouped = function(){
		if ($("td.single").length == 3){
			return "True";
		}else{
			return "False";
		};
	};

	checkMaxWidth = function() {
		var row = document.getElementById("cond_row");
		var dragDiv = document.getElementById("drag");
		
		return (row.offsetWidth <= dragDiv.offsetWidth * 0.95);
	};

