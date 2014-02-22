$(document).ready(function() {
	$('#cancel_subscription_form').submit(function(e) {
		if (!$('#cancel_confirm').is(':checked')) {
			alert('In order to cancel, check the box and click confirm cancellation.')
			return false;
		}
		return true;
	});
});