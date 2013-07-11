/* Simple frame busting */
if(top.location != document.location) {
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
});

