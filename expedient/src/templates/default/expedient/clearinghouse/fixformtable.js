					.contents()
					.filter(function() {
						return this.nodeType == Node.TEXT_NODE && $(this).text().length > 1;
					})
					.each(function(index) {
						text = $(this).text();
                                                /* Show bubble only when text is available */
                                                if ($.trim(text)) {
						this.data = "";
							$(this)
					  		    .closest("tr")
							    .find("td:first-child")
							    .html(
								"<img id='tooltip_help_img_"+index+"' src='"+
								"{% url img_media 'question_mark_15x15.png' %}' />" +
								"<div id='tooltip_help_"+index+"' class='tooltip'>"+
								text+"</div>"
							    );
							$("img#tooltip_help_img_"+index).tooltip({
                                                	    tip: "div#tooltip_help_"+index,
                                                	    position: "top center",
                                           	         cancelDefault: true,
                                           	         relative: true,
                                           	         offset: [0,110]						
								});
						}
					})
