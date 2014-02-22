from google.appengine.api import mail
from models.models import *

# Activation
# Invitation
# Contact
# Subscription
# PasswordRecovery

#--------------------------------------------------------------
def SendActivationEmail(user):
	# TODO: Change the FROM address.
	token = ",".join([str(user.key.id()), str(user.created.strftime("%f"))])

	message = mail.EmailMessage()

	message.sender  = "AperitifClub.com Account activation <rikonor@gmail.com>"
	message.subject = "[AperitifClub] Please activate your account"
	message.to = "%s <%s>" % (user.name, user.email)
	message.body = """
Dear %s,

Thank you for joining our exclusive patron service at AperitifClub.com
	
To activate your account please follow this link:
http://www.aperitif-club.appspot.com/activate?token=%s

Please let us know if you have any questions.

The AperitifClub.com Team
""" % (user.name.split()[0], token)

	print "Sending Activation email (%s), token=%s" %(user.email, token)
	message.send()
#--------------------------------------------------------------
def SendInvitationEmail(user, rest, invite_email, reg_code):
	message = mail.EmailMessage()

	message.sender  = "AperitifClub.com Invitation <rikonor@gmail.com>"
	message.subject = "[AperitifClub] %s sent you an invitation" % user.name
	message.to = "<%s>" % invite_email
	message.body = """
Hello,

%(user_name)s would like to invite you to join AperatifClub.com, an exclusive patron service,
and own a regular table at %(rest_name)s.

To register for an account please follow this link:
http://www.aperitif-club.appspot.com/reg_continue?reg_code=%(reg_code)s

Kindly contact us with any question, and enjoy your table!

Your patron service team,
Aperitif Club
""" % {'user_name': user.name, 'rest_name': rest.name, 'reg_code': reg_code}

	print "Sending Invitation email (%s), to=%s" %(user.email, invite_email)
	message.send()
#--------------------------------------------------------------
def SendContactEmail(user, subject, message):
	message = mail.EmailMessage()

	message.sender  = "AperitifClub.com - Contact message <rikonor@gmail.com>"
	message.subject = "[AperitifClub] %s wants to contact you" % user.name
	message.to = "<rikonor@gmail.com>"
	message.body = """
Hello Admin,

%(user_name)s has submitted the following contact form:
-------------------------------------------------------
Subject: %(subject)s

Message: %(message)s

-------------------------------------------------------
""" % {'user_name': user.name, 'subject': subject, 'message': message}

	print "Sending Contact Email (%s)" %(user.email)
	message.send()
#--------------------------------------------------------------
def SubscriptionEmail(user, subscription):
	message = mail.EmailMessage()

	message.sender  = "AperitifClub.com - Subscription Service <rikonor@gmail.com>"
	message.subject = "[AperitifClub] Congratulations! You now own a table at %s" % subscription.rest.get().name
	message.to = "<%s>" % user.email
	
	next_date = Reservation.query(Reservation.subscription==subscription.key).order(Reservation.dt).get().dt

	message.body = """
Hello %(user)s,

We would like to thank you for making a %(type)s subscription at %(rest)s.
Your table will be waiting for you on %(date)s at %(time)s.
You will recieve e-mail reminders of your reservations in advance, with the option of gifting them at your convenience.

Please feel free to contact us any time at PatronService@aperitifclub.com

Your patron service team,
Aperitif Club
""" % { 'user': user.name,
			'type': subscription.typeOf,
			'rest': subscription.rest.get().name,
			'date': next_date.strftime("%A, %b %d %Y"),
			'time': next_date.strftime("%I:%M%p")
			}

	print "Sending New Subscription Email (%s, %s, %s)" % (user.email, subscription.typeOf, subscription.rest.get().name)
	message.send()
#--------------------------------------------------------------
def SendPasswordRecoveryEmail(user):
	# TODO: Change the FROM address.
	token = ",".join([str(user.key.id()), str(user.created.strftime("%f"))])

	message = mail.EmailMessage()

	message.sender  = "AperitifClub.com Password Recovery Service <rikonor@gmail.com>"
	message.subject = "[AperitifClub] Password Recovery link"
	message.to = "%s <%s>" % (user.name, user.email)
	message.body = """
Dear %(user)s,

To reset your password please follow this link:
http://www.aperitif-club.appspot.com/reset_password?token=%(token)s

If you did not request this email,
please let us know at ak@slingshotops.com.

The AperitifClub.com Team
""" % {'user': user.name.split()[0], 'token': token}

	print "Sending Password Recovery email (%s), token=%s" %(user.email, token)
	message.send()
#--------------------------------------------------------------