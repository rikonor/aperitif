$(document).ready(function() {
	$("#datepicker").datepicker({
		'minDate': '0',
		'maxDate': '+1W'
    });
    $("#timepicker").timepicker({
    	'step': 30,
    	'minTime': '8:00am',
    	'maxTime': '0:00am'
    });
});