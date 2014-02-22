import os, sys, datetime, time

from handlers.BaseHandler import BaseHandler
from models.models import *
from models.messages import *
from security import hashes
from handlers.AuthHandlers import *
from handlers.MailHandlers import *
from handlers.paymentHandlers import paymentManager

#--------------------------------------------------------------
# SubscriptionHandler
#--------------------------------------------------------------
class SubscriptionHandler(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/reserve?message=subscriptionnotfound")

        if subscription.typeOf == 'empty':
            return self.redirect("/subscription/new?id="+self.request.get("id"))
        else:
            return self.redirect("/subscription/view?id="+self.request.get("id"))
            
#--------------------------------------------------------------
# SubscriptionNew handler
#--------------------------------------------------------------
class SubscriptionNew(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/reserve?message=subscriptionnotfound")

        return self.render("subscription_new.html", user=user, subscription=subscription)

    def post(self):
    	user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

    	# Get form info
    	stripeToken = self.request.get("stripeToken")
    	stype = self.request.get("subscription_type")
    	date = self.request.get("date")
    	time = self.request.get("time")
        subscription_id = self.request.get("id")
    	subscription = Subscription.getById(subscription_id)
    	# Call actual payment
    	stripe_customer_id = paymentManager.createStripeSubscription(
    		user=user,
    		token=stripeToken,
    		stype=stype,
    		subscription=subscription
    		)
    	# Assuming the payment was successful
    	# Save transaction and stripe_customer_id for later actions
    	transaction = Transaction(stripe_customer_id=stripe_customer_id, subscription=subscription.key, user=user.key)
    	transaction.put()
    	# Update the subscription details
    	subscription.typeOf = stype
    	subscription.start_date = datetime.datetime.strptime(" ".join([date, time]), "%m/%d/%Y %I:%M%p")
    	subscription.transaction = transaction.key
    	subscription.put()
    	# Update reservations (TODO)
    	updateReservations(subscription)
    	# Send Subscription Email
    	SubscriptionEmail(user=user, subscription=subscription)
    	return self.redirect("/reserve")

#--------------------------------------------------------------
# SubscriptionView handler
#--------------------------------------------------------------
class SubscriptionView(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        message_text = getMessage(self.request.get("message"))
        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/reserve?message=subscriptionnotfound")

        reservations = Reservation.query(Reservation.subscription == subscription.key).order(Reservation.dt).fetch()
        return self.render("subscription_view.html", user=user, subscription=subscription, reservations=reservations, message_text=message_text)

#--------------------------------------------------------------            
# SubscriptionEdit handler
#--------------------------------------------------------------
class SubscriptionEdit(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/reserve?message=subscriptionnotfound")

        return self.render("subscription_edit.html", user=user, subscription=subscription)

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/reserve?message=subscriptionnotfound")

        new_time = self.request.get("time")
        new_time = datetime.datetime.strptime(new_time, "%I:%M%p")
        new_date = self.request.get("date")
        if new_date:
            new_date = datetime.datetime.strptime(new_date, "%m/%d/%Y")
        if new_date:
            subscription.start_date = subscription.start_date.replace(
                month=new_date.month, day=new_date.day, year=new_date.year,
                hour=new_time.hour, minute=new_time.minute)
        else:
            subscription.start_date = subscription.start_date.replace(
                hour=new_time.hour, minute=new_time.minute)
        subscription.put()
        time.sleep(0.1)
        
        return self.redirect("/subscription/view?id="+subscription_id)

#--------------------------------------------------------------
# SubscriptionCancel handler
#--------------------------------------------------------------
class SubscriptionCancel(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/reserve?message=subscriptionnotfound")

        return self.render("subscription_cancel.html", user=user, subscription=subscription)    

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")
            
        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/reserve?message=subscriptionnotfound")

        cancelSubscription(subscription)
        return self.redirect("/reserve?message=subscriptioncancelled")

#--------------------------------------------------------------        
def SubscriptionChangeType(subscription, new_type):
    # Validate
    if new_type not in ['weekly, daily']:
        return None
    current_type = subscription.typeOf
    if current_type == new_type:
        return None

    # Cancel current
    reservations = []
    for reservation in subscription.reservations:
        reservations.append(reservation.get())
    for reservation in reservations:
        cancelReservation(reservation)

    # Change type
    subscription.typeOf = new_type

    # Update
    updateReservations(subscription)
#--------------------------------------------------------------        
def cancelSubscription(subscription):
    # Cancel current reservations
    reservations = []
    for reservation in subscription.reservations:
        reservations.append(reservation.get())
    for reservation in reservations:
        cancelReservation(reservation)

    # Change type
    subscription.typeOf = 'empty'

    # Cancel Stripe subscription
    stripe_customer_id = subscription.transaction.get().stripe_customer_id
    paymentManager.cancelStripeSubscription(stripe_customer_id)
    subscription.transaction = None

    # Save changes
    subscription.put()
    time.sleep(0.1)
#--------------------------------------------------------------
# updateReservations - Gets subscription ID and updates it
#--------------------------------------------------------------
# Each subscription must have its next 4 reservations made in advance
# Every time a reservation is attended, the next one will be made.
#--------------------------------------------------------------
def updateReservations(subscription):
	# Check subscription isn't empty
	if subscription.typeOf == "empty":
		return None
	# N = how many reservations in advance
	N_chart = {
		'weekly': 4,
		'daily':  5,
		}
	# d = time between each reservation
	d_chart = {
		'weekly': datetime.timedelta(days=7),
		'daily':  datetime.timedelta(days=1), 
		}
	N = N_chart[subscription.typeOf]
	d = d_chart[subscription.typeOf]
	
	now = datetime.datetime.now()
	start = subscription.start_date

	# Find start of update period (true_start)
	true_start = start
	while (true_start - now).days < 0:
		true_start = true_start + d

	# Get the reservation dates
	true_dates = [true_start+i*d for i in range(N)]

	# Check each date for a reservation, if there is none, make it
	reservations = Reservation.query(Reservation.subscription==subscription.key)
	for date in true_dates:
		dateD = datetime.datetime.strptime(date.strftime('%m/%d/%Y'),'%m/%d/%Y')
		dateDN= dateD + datetime.timedelta(days=1)
		checkExists = reservations.filter(Reservation.dt >= dateD).filter(Reservation.dt <= dateDN).get()
		if not checkExists:
			makeReservation(user=subscription.user, rest=subscription.rest, dt=date, subscription=subscription)
#--------------------------------------------------------------
def makeReservation(user, rest, dt, subscription=None):
    # TODO: Check reservation time is available.

    # Make a new reservation
    reservation = Reservation(user=user, rest=rest, dt=dt)
    if subscription: reservation.subscription = subscription.key
    reservation.put()

    # Attach the reservation to User, Rest and optionally Subscription
    user = user.get()
    user.reservations.append(reservation.key)
    user.put()
    rest = rest.get()
    rest.reservations.append(reservation.key)
    rest.put()
    if subscription:
    	subscription.reservations.append(reservation.key)
    	subscription.put()
    # Log
    print "Reservation created: %(user)s, %(rest)s, %(dt)s" % {'user': user.name, 'rest': rest.name, 'dt': dt}
#--------------------------------------------------------------
def passReservation(reservation):
    # Create a new ReservationPassed
    passedReservation = ReservationPassed(
        dt = reservation.dt,
        created = reservation.created,
        rest = reservation.rest,
        user = reservation.user,
        subscription = None,
        )
    if reservation.subscription:
        passedReservation.subscription = reservation.subscription
    passedReservation.put()
    # Detach (User, Rest, Subscription) from Reservation
    rest = reservation.rest.get()
    if reservation.key in rest.reservations:
        rest.reservations.remove(reservation.key)
    rest.put()
    user = reservation.user.get()
    if reservation.key in user.reservations:
        user.reservations.remove(reservation.key)
    user.put()
    if reservation.subscription:
        subscription = reservation.subscription.get()
        if reservation.key in subscription.reservations:
            subscription.reservations.remove(reservation.key)
        subscription.put()
    # Delete original Reservation
    reservation.key.delete()
    print "Reservation passed: %(user)s, %(rest)s, %(dt)s" % {'user': user.name, 'rest': rest.name, 'dt': passedReservation.dt}
    return str(passedReservation.key.id())
#--------------------------------------------------------------
def cancelReservation(reservation):
    # Create a new ReservationCancelled
    cancelledReservation = ReservationCancelled(
        dt = reservation.dt,
        created = reservation.created,
        rest = reservation.rest,
        user = reservation.user,
        subscription = None,
        )
    if reservation.subscription:
        cancelledReservation.subscription = reservation.subscription
    cancelledReservation.put()
    # Detach (User, Rest, Subscription) from Reservation
    rest = reservation.rest.get()
    if reservation.key in rest.reservations:
        rest.reservations.remove(reservation.key)
    rest.put()
    user = reservation.user.get()
    if reservation.key in user.reservations:
        user.reservations.remove(reservation.key)
    user.put()
    if reservation.subscription:
        subscription = reservation.subscription.get()
        if reservation.key in subscription.reservations:
            subscription.reservations.remove(reservation.key)
        subscription.put()
    # Delete original Reservation
    reservation.key.delete()
    print "Reservation cancelled: %(user)s, %(rest)s, %(dt)s" % {'user': user.name, 'rest': rest.name, 'dt': cancelledReservation.dt}
    return str(cancelledReservation.key.id())
#--------------------------------------------------------------