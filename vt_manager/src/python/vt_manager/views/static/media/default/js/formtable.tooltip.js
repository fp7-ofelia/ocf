if(     top.location != document.location) {
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
                $("table.formtable>tbody>tr>td.help_text")

                                .contents()
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
                                "<img id='tooltip_help_img_"+index+ "' src=" + url_img_question + ">" +
                                "<div id='tooltip_help_"+index+"' class='tooltip'>"+
                                text+"</div>"
                            )
                        ;
                        $("img#tooltip_help_img_"+index).tooltip({
                            tip: "div#tooltip_help_"+index,
                                                        position: "top center",
                                                        cancelDefault: true,
                                                        relative: true,
                                                        offset: [0,110]
                        });
                    });
            });

