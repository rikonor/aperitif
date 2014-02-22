$(document).ready(function() {
	$('.form_page#choose_type').show();

	var sType = 'empty';
	var priceChart = {
		'empty': 0,
		'daily': 99900,
		'weekly': 24900,
		'flexible': 49900
	}

	$("#datepicker").datepicker({
  	minDate: 0,
  	maxDate: 30,
  });
  $("#timepicker").timepicker({
  	'step': 30,
  	'minTime': '8:00am',
  	'maxTime': '0:00am'
  });

	// Choose Type progression
	$('#subscription_type input').change(function() {
		sType = $('#subscription_type input[type=radio]:checked').val();
		$('.form_page#choose_datetime').show(speed="fast");
	});

	// Stripe button binding and token generator
	var handler = StripeCheckout.configure({
	    key: 'pk_test_IGa7qZrYR9sGSOaJa3nagNfZ',
	    image: '/square-image.png',
	    token: function(token, args) {
	      // Use the token to create the charge with a server-side script.
	      form = $('#new_subscription_form');
	      form.append('<input type="text" name="stripeToken" value="'+token.id+'" hidden/>');
	      $('#new_subscription_form').submit();
	    }
	});

  	document.getElementById('stripeButton').addEventListener('click', function(e) {
    // Open Checkout with further options
    	var packagePrice = priceChart[sType];
    	var dateP = $('#datepicker');
    	var timeP = $('#timepicker');
    	if (dateP.val() && timeP.val()) {
	    	handler.open({
	      		name: 'Aperitif Club',
	      		description: sType.charAt(0).toUpperCase()+sType.slice(1)+' Subscription ($'+packagePrice/100+')',
	      		amount: packagePrice,
	      		currency: 'usd',
	      		panelLabel: "Pay {{amount}}",
	      		billingAddress: false,
	      		email: $('form input[name=email]').val()
	    	});
	    } else {
	    	if (!dateP.val()) dateP.val("Please choose a date.");
	    	if (!timeP.val()) timeP.val("Please choose a time.");
	    }
    	e.preventDefault();
  	});
});