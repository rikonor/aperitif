import os, sys, datetime, time

from BaseHandler import BaseHandler
from models.models import *
from security import hashes
from handlers.AuthHandlers import *

from google.appengine.api import mail
import stripe

stripe.api_key = "sk_test_JspVXOKJl9w8qZ2T90k8lJKI"

class paymentManager:

	@staticmethod
	def createStripeSubscription(user, token, stype, subscription):
		customer = stripe.Customer.create(
			card = token,
			plan = stype.upper(),
			email= user.email,
			description= "%(type)s subscription (%(rest)s)." % {'type': stype.capitalize() ,'rest': subscription.rest.get().name}
		)
		return customer.id

	@staticmethod
	def cancelStripeSubscription(stripe_customer_id):
		customer = stripe.Customer.retrieve(stripe_customer_id)
		customer.cancel_subscription()
		

