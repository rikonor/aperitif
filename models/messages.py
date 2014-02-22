messages = {
	"invalidmessage"	
		: "No message text detected.\nPlease add text to your message.",
	
	"wrongpassword"
		: "It seems this password is wrong.\nPlease try again.",

	"regnameerror"
		: "Please enter a full name.",
	"regemailerror"
		: "Please enter a valid email address.",
	"regphoneerror"
		: "Please enter a valid phone number.",
	"regpasserror"
		: "Please enter a valid password.",
	"regpassrepeaterror"
		: "You did not repeat your password correctly.",
	
	"passwordresetemail"
		: "Password reset email sent\nPlease check your email inbox.",
	"passwordreset"
		: "Password reset.",
	"passwordchanged"
		: "Password changed.",

	"usernotfound"		
		: "Error\nUser not found.",
	"usereditfailed"	
		: "Edit failed\nPlease make sure to put in a valid name, phone number and email.",
	"userchangepassfailed"
		: "Please enter a new password and make sure to reenter it correctly.",
	
	"inviteinvalidemail"	
		: "Invalid Email.\nPlease enter a valid Email address to invite.",
	"invitesuccess"
		: "Invitation email sent!",

	"restaddedalready"
		: "You are already registered to the restaurant this code refers too.",
	
	"restaurantnotfound"
		: "Error\nRestaurant not found.",
	"restauranteditfailed"
		: "Edit failed\nPlease try again.",

	"codenotfound"	
		: "Error\nCode not found.",
	"invalidcode"
		: "The code is invalid.\nKindly try again or contact us at PatronService@AperitifClub.com",
	"codemaxuses"
		: "The code is no longer active.\nKindly try again or contact us at PatronService@AperitifClub.com",
		
	"reservationnotfound"
		: "Error\nReservation not found.",
	"reservationeditfailed"
		: "Edit failed.\nPlease make sure to put in both a valid date and time.",
	"reservationcancelfailed"
		: "Cancellation failed.",
	
	"subscriptionnotfound"
		: "Error\nSubscription not found.",
	"subscriptioncanteditempty"
		: "Can't edit\nYou can't edit an empty subscription.",
	"subscriptioneditfailed"
		: "Edit failed\nPlease try again.",
}

def getMessage(message_code):
	if message_code in messages.keys():
		return messages[message_code]
	else:
		return ""