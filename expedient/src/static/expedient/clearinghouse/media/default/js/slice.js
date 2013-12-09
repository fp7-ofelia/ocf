function getLoadingMsg(action, slice_started) {
    var grantedFlowspace = 0;
    if ($("[id^=grantedFlowspace][id$=Container]").length > 0 || 
        $(".grantedFlowspaceHeader").length > 0) {
            grantedFlowspace = 1;
        }

    var flowspaceWarning = 'confirmWrapper("';
    if (action == "start_update") {
        if (slice_started == 1) {
            if (grantedFlowspace) {
                flowspaceWarning += "Updating";
            }
        } else {
            return eval('showLoadingMsg("Loading...");');
        }
    } else if (action == "stop") {
        if (grantedFlowspace) {
            flowspaceWarning += "Stopping";
        }
    }
    if (grantedFlowspace) {
        flowspaceWarning += ' the slice will cause all granted flowspaces to be deleted in the Flowvisor, and require approval for new requests. Are you sure you want to ' + action + ' the slice?");';
        return eval(flowspaceWarning);
    } else {
        return eval('showLoadingMsg("Loading...");');
    }
}

function showLoadingMsg(message){
	//TODO:Show message
	 $.blockUI({
			/*message: message,*/
			css: { 
            border: 'none', 
            padding: '15px', 
		    backgroundColor: '#000', 
        	 	'-webkit-border-radius': '10px', 
        		'-moz-border-radius': '10px', 
       	    opacity: .5, 
 		    color: '#fff' 
		} });
}
function confirmWrapper(message){
	value = confirm(message);
	if (value){
		showLoadingMsg("Loading...");
	}
	return value;
}
$(document).ready(function() {
	$("#aggs_help_img").tooltip({
		tip: "#aggs_help_div"
	});
	$(".expandableTooltipable").tooltip({
		tip: "#expandableHelp"
	});
});
