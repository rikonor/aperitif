$(document).ready(function() {
	var messageText = $('#messageText');
	if (messageText.text()) {
		var lines = messageText.text().split('\n');
		messageText.text("");
		for (var i = 0; i < lines.length; i++) {
			messageText.append("<span>"+lines[i]+"</span><br/><br/>");
		}
		$('#messageBox').show();
	}

	$('#messageOK').click(function() {
		$('#messageBox').hide();
	});
});