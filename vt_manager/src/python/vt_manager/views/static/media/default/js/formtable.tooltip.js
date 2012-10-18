<<<<<<< HEAD
		if(	top.location != document.location) {
=======
if(     top.location != document.location) {
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
                top.location = document.location;
            }
            /**
             * Move the help text in formtable classes to a new separate column.
             */
            $(document).ready(function() {
                /* add a column at the beginning for the help icons */
                $("table.formtable_noborder>tbody>tr," +
                "table.formtable>tbody>tr")
                    .prepend("<td />");
                $("table.formtable_noborder>thead>tr," +
                "table.formtable>thead>tr")
                    .prepend("<td />");

                /* find help text and replace with image and tooltip */
<<<<<<< HEAD
//                $("table.formtable_noborder>tbody>tr>td:nth-child(3)")
//                
//				.contents()
//                    .filter(function() {
//                        return this.nodeType == Node.TEXT_NODE && $(this).text().length > 1;
//                    })
//                    .each(function(index) {
//                        text = $(this).text();
//                        this.data = "";
//                        $(this)
//                            .closest("tr")
//                            .find("td:first-child")
//                            .html(
//                                "<img id='tooltip_help_img_"+index+"' src='/static/media/images/question_mark_15x15.png' />" +
//                                "<div id='tooltip_help_"+index+"' class='tooltip'>"+
//                                text+"</div>"
//                            )
//                        ;
//                        $("img#tooltip_help_img_"+index).tooltip({
//                            tip: "div#tooltip_help_"+index
//                        });
//                    })
//
//				;
//
//                $("table.formtable_noborder>tbody>tr>td:nth-child(2)")
//
//                .contents()
//                    .filter(function() {
//                        return this.nodeType == Node.TEXT_NODE && $(this).text().length > 1;
//                    })
//                    .each(function(index) {
//                        text = $(this).text();
//                        this.data = "";
//                        $(this)
//                            .closest("tr")
//                            .find("td:first-child")
//                            .html(
//                                "<img id='tooltip_help_img_"+index+"' src='/static/media/images/question_mark_15x15.png' />" +
//                                "<div id='tooltip_help_"+index+"' class='tooltip'>"+
//                                text+"</div>"
//                            )
//                        ;
//                        $("img#tooltip_help_img_"+index).tooltip({
//                            tip: "div#tooltip_help_"+index
//                        });
//                    })
//
//                ;


                $("table.formtable>tbody>tr>td.help_text")
                
				.contents()
=======
                $("table.formtable>tbody>tr>td.help_text")

                                .contents()
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
                    .filter(function() {
                        return this.nodeType == Node.TEXT_NODE && $(this).text().length > 1;
                    })
                    .each(function(index) {
                        text = $(this).text();
                        this.data = "";
                        $(this)
                            .closest("tr")
                            .find("td:first-child")
                            .html(
<<<<<<< HEAD
                                "<img id='tooltip_help_img_"+index+"' src='/static/media/images/question_mark_15x15.png'/>" +
=======
                                "<img id='tooltip_help_img_"+index+ "' src=" + url_img_question + ">" +
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
                                "<div id='tooltip_help_"+index+"' class='tooltip'>"+
                                text+"</div>"
                            )
                        ;
                        $("img#tooltip_help_img_"+index).tooltip({
                            tip: "div#tooltip_help_"+index,
<<<<<<< HEAD
							position: "top center",
							cancelDefault: true,
							relative: true,
							offset: [0,110]
                        });
                    })

;

//                $("table.formtable>tbody>tr>td:nth-child(2)")
//
//                .contents()
//                    .filter(function() {
//                        return this.nodeType == Node.TEXT_NODE && $(this).text().length > 1;
//                    })
//                    .each(function(index) {
//                        text = $(this).text();
//                        this.data = "";
//                        $(this)
//                            .closest("tr")
//                            .find("td:first-child")
//                            .html(
//                                "<img id='tooltip_help_img_"+index+"' src='/static/media/images/question_mark_15x15.png'/>" +
//                                "<div id='tooltip_help_"+index+"' class='tooltip'>"+
//                                text+"</div>"
//                            )
//                        ;
//                        $("img#tooltip_help_img_"+index).tooltip({
//                            tip: "div#tooltip_help_"+index
//                        });
//                    })
//
//;


=======
                                                        position: "top center",
                                                        cancelDefault: true,
                                                        relative: true,
                                                        offset: [0,110]
                        });
                    });
>>>>>>> 8973dbcd3e450399738a5324ba6d9057bc126156
            });

