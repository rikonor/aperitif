$(document).ready(function() {
	$("#datepicker").datepicker({
    });
    $("#timepicker").timepicker({
    	'step': 30,
    	'minTime': '8:00am',
    	'maxTime': '0:00am'
    });
});