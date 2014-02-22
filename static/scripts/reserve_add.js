$(function() {
    $("#datepickerContainer").datepicker({
    	minDate: 0
    });
    $("#timepicker").timepicker({
    	'step': 15,
    	'minTime': '8:00am',
    	'maxTime': '0:00am'
    });
    $("#durationpicker").timepicker({
    	'timeFormat': 'H:i',
    	'minTime': '0:00',
		'maxTime': '4:00',
    });
 });