$(document).ready(function() {
	$('#cancel_reservation_form').submit(function(e) {
		if (!$('#cancel_confirm').is(':checked')) {
			alert('Please make sure to check the box if you are sure!')
			return false;
		}
		return true;
	});
});