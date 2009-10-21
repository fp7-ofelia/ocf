    <script src="http://www.java.com/js/deployJava.js"></script>
	
	<script language="JavaScript">
	    function addHiddenInput(id, name, val) {
	        var form = document.getElementById("sliceForm");
	        var newIn = document.createElement("input");
	        newIn.name = name;
	        newIn.type = "hidden";
	        newIn.id = id;
	        newIn.value = val;
	        form.appendChild(newIn);
	    }
	    
        function doSubmit(form) {
        	
            // get the list of node_ids
            var node_ids = guiPlugin.getNodeIDs();
            for(var i=0, len=node_ids.length; i<len; i++) {
                addHiddenInput("node_id_"+i, "node_id", node_ids[i]);
            }
            
            // get the list of link_ids
            var link_ids = guiPlugin.getLinkIDs();
            for(var i=0, len=link_ids.length; i<len; i++) {
                addHiddenInput("link_id_"+i, "link_id", link_ids[i]);
            }

            return true;
	    }
	</script>
