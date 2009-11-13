    <script src="http://www.java.com/js/deployJava.js"></script>
	
	<script language="JavaScript">
	    function addHiddenInput(form, id, name, val) {
	        var newIn = document.createElement("input");
	        newIn.name = name;
	        newIn.type = "hidden";
	        newIn.id = id;
	        newIn.value = val;
	        form.appendChild(newIn);
	    }
	    
        function doSubmit(form) {

        	var topoPanel = document.guiPlugin.getTopoPanel();

        	/* get the nodes */
            var nodes = topoPanel.getGraphNodes();
            
            /* for each node, send back its new x,y pos and whether or not it
             * is selected */
            for(var i = 0, len = nodes.length; i < len; i++) {
              var n = nodes[i];
              var is_sel = n.isSelected().toString();
              if(is_sel == "true") {
                addHiddenInput(form, "node_id_"+i, "node_id", n.getId());
              }
              addHiddenInput(form, "node_id_pos", "pos", n.getId()+":::"+n.getX()+","+n.getY());
            }

            // get the list of link_ids
            var links = topoPanel.getGraphLinks();
            for(var i=0, len=links.length; i<len; i++) {
                var l = links[i];
                if(l.isSelected().toString() == "true") {
                    addHiddenInput(form, "link_id_"+i, "link_id", l.getId());
                }
            }

            return true;
        }
        
        {% if confirm %}
        alert("Slice was reserved!");
        {% endif %}
        
    </script>
