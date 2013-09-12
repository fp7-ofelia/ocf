/**
	Highlight selected link and clear style from the rest.

	@param selected_link Link to be highlighted
	@param set_links the whole set of links, where highlighted
					 link is contained
*/
function highlightSelectedLink(selected_link, set_links) {
	$(set_links).removeClass("selected");
    $(selected_link).addClass("selected");
}

/**
	Invoke link highlighting for top navigation link set.
*/
function changeNavigationLinksColor() {
	$("#top_menu_options ul a").click(function() {
		highlightSelectedLink($(this), "#top_menu_options ul a");
	});
}

/**
	Check if current path corresponds to one of the given set of
	links and, if it does, highlight that link.

	@param set_links the whole set of links
	@param requested_path current path the browser points to
*/
function isSelectedLink(set_links, requested_path) {	
	$(set_links).each(function() {
		if ($(this).attr("href") == requested_path) {
			highlightSelectedLink($(this), "#top_menu_options ul a");
		}
	});
}

$(document).ready(function() {
	changeNavigationLinksColor();
});

