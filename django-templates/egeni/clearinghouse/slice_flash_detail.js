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
        	
        	var topoPanel = guiPlugin.getTopoPanel();

        	/* get the nodes */
        	var nodes = topoPanel.getGraphNodes();
        	
        	/* for each node, send back its new x,y pos and whether or not it
        	 * is selected */
        	for(var i = 0, len = nodes.length; i < len; i++) {
        	  var n = nodes[i];
        	  var is_sel = n.isSelected().toString();
        	  if(is_sel == "true") {
        	    addHiddenInput("node_id_"+i, "node_id", n.getId());
        	  }
        	  addHiddenInput("node_id_x", "x-pos", n.getId()+":::"+n.getX());
        	  addHiddenInput("node_id_y", "y-pos", n.getId()+":::"+n.getY());
        	}

            // get the list of link_ids
            var links = topoPanel.getGraphLinks();
            for(var i=0, len=links.length; i<len; i++) {
            	var l = links[i];
            	if(l.isSelected().toString() == "true") {
            		addHiddenInput("link_id_"+i, "link_id", l.getId());
            	}
            }

            return true;
	    }
        
        {% if confirm %}
        alert("Slice was reserved!");
        {% endif %}
        
	</script>
