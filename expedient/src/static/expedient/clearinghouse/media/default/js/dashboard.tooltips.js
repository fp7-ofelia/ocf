$(document).ready(function() {
	/* add tooltip to question mark */
	$("img#perm_help").tooltip({
		tip: "div#perm_mgmt_help",
        position: "top center",
        cancelDefault: true,
        relative: true,
        offset: [0,110]
	});
	$("img#users_help").tooltip({
		tip: "div#user_mgmt_help",
        position: "top center",
        cancelDefault: true,
        relative: true,
        offset: [0,110]
	});

	$("img#notifications_help").tooltip({
		tip: "div#notifications_help",
        position: "top center",
        cancelDefault: true,
        relative: true,
        offset: [0,110]
            });
});

function closeTooltip(){
    $(".animatedTooltip").css("display","none");
}
