/* For FlowSpace editing only */
$(document).ready(function() {
	if (document.URL.indexOf("flowspace") > -1) {
		/*
		// jQuery tools 1.2.3 (does not work as of 1.2.7)
		var numRows = Math.floor($("table.formtable>tbody>tr:nth-child>td:nth-child(3)").size()/2);
		*/
		var numRows = Math.floor($("table.formtable>tbody>tr>td:nth-child(3)").size()/2);
		for (index=1; index<=numRows; index++) {
			var labels = $("table.formtable>tbody>tr:nth-child(" + index + ")>td").find('label');
			var text = "";
			if (labels[0] != undefined && labels[1] != undefined) {
				text = labels[0].textContent;
				if (labels[0].textContent != labels[1].textContent) {
					text = "<ul class=\"fulltable_tooltip_list\"><li>" + text + "</li>";
					text = text + "<li>" + labels[1].textContent + "</li></ul>";
				}
			}
			if (text.length > 1) {
				$("table.formtable>tbody>tr:nth-child(" + index + ")>td")
				.closest("tr")
				.find("td:first-child>div#[id^='tooltip_help']")
				.html(text);
			} else {
				// No text --> remove question icon
				$("table.formtable>tbody>tr:nth-child(" + index + ")>td")
				.closest("tr")
				.find("td:first-child")
				.html("");
			}
    	}
	}
});
