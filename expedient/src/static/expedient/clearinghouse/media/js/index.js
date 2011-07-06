<script src="{% url js_media 'jquery.min.js' %}"></script>

<script type="text/javascript">
function showCreateMsgDiv() {
	$('#div_message_create').fadeIn();
}
function hideCreateMsgDiv() {
	$('#div_message_create').hide();
}
$(document).ready(function() {
	hideCreateMsgDiv();
});
</script>
