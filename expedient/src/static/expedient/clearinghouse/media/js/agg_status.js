function get_status(am_id, url) {

	$.ajax({
		url: url,
		success: function(data) {
			$('img#status_'+am_id).attr("src", data);
		}
	});

}

