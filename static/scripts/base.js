$(document).ready(function() {
	$('.popupContainer').click(function() {
		$(this).find('.popup').show();
	});
	$('.popup').mouseleave(function() {
		$(this).hide();
	});
});