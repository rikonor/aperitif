import os, sys, datetime, time
from handlers.BaseHandler import BaseHandler
from models.models import *
from handlers.AdminAuth import AdminAuthenticate

# To get all model kinds
from google.appengine.ext.db.metadata import Kind

# These methods will permenantly delete DB data,
# and currently should only be used in development.

#--------------------------------------------------------------
# deleteReservation method
#--------------------------------------------------------------
def deleteReservation(reservation):
    # Detach (User, Rest, Subscription)
    rest = reservation.rest.get()
    if rest and reservation.key in rest.reservations:
        rest.reservations.remove(reservation.key)
    	rest.put()
    user = reservation.user.get()
    if user and reservation.key in user.reservations:
        user.reservations.remove(reservation.key)
    	user.put()
	if reservation.subscription:
		subscription = reservation.subscription.get()
		if subscription and reservation.key in subscription.reservations:
			subscription.reservations.remove(reservation.key)
			subscription.put()
    # Delete original Reservation
    reservation.key.delete()

def deleteReservationForSubscription(reservation):
    # Detach (User, Rest)
    # DO NOT Detach Subscription - Due to error
    rest = reservation.rest.get()
    if rest and reservation.key in rest.reservations:
        rest.reservations.remove(reservation.key)
    	rest.put()
    user = reservation.user.get()
    if user and reservation.key in user.reservations:
        user.reservations.remove(reservation.key)
    	user.put()
    reservation.key.delete()

def deleteReservationForUser(reservation):
    # Detach (User, Rest)
    # DO NOT Detach Subscription - Due to error
    rest = reservation.rest.get()
    if rest and reservation.key in rest.reservations:
        rest.reservations.remove(reservation.key)
    	rest.put()
    reservation.key.delete()
#--------------------------------------------------------------
# deleteSubscription method
#--------------------------------------------------------------
def deleteSubscription(subscription):
    # Detach (User) 
    # Delete Reservations, Transaction
    user = subscription.user.get()
    if user and subscription.key in user.subscriptions:
        user.subscriptions.remove(subscription.key)
    	user.put()
    if subscription.reservations:
    	[deleteReservationForSubscription(reservation.get()) for reservation in subscription.reservations if reservation.get()]
    if subscription.transaction:
		transaction = subscription.transaction.get()
		if transaction:
			transaction.key.delete()
    # Delete original Reservation
    subscription.key.delete()

def deleteSubscriptionForUser(subscription):
    # DO NOT Detach (User) - Due to error 
    # Delete Reservations, Transaction
    if subscription.reservations:
    	[deleteReservationForUser(reservation.get()) for reservation in subscription.reservations if reservation.get()]
    if subscription.transaction:
		transaction = subscription.transaction.get()
		if transaction:
			transaction.key.delete()
    # Delete original Reservation
    subscription.key.delete()
#--------------------------------------------------------------
# deleteUser method
#--------------------------------------------------------------
def deleteUser(user):
    # Detach (Restaurant, Used_codes) 
    # Delete (Subscriptions, Gen_codes)
    if user.rests:
    	for rest in user.rests:
    		rest = rest.get()
    		if user.key in rest.users:
        		rest.users.remove(user.key)
    			rest.put()
    if user.used_codes:
    	for used_code in user.used_codes:
    		used_code = used_code.get()
    		if user.key in used_code.users:
    			used_code.users.remove(user.key)
    			used_code.put()
    if user.subscriptions:
    	[deleteSubscriptionForUser(subscription.get()) for subscription in user.subscriptions if subscription.get()]
    if user.gen_codes:
    	[gen_code.delete() for gen_code in user.gen_codes if gen_code.get()]
    # Delete original Reservation
    user.key.delete()
#--------------------------------------------------------------
# deleteAllEntities method
#--------------------------------------------------------------
def deleteAllEntities():
	from models import models
	q = Kind.all()
	model_types = [k.kind_name for k in q]

	for model_type in model_types:
		model_type = getattr(models, model_type)
		model_type_objects = model_type.query().fetch()
		for obj in model_type_objects:
			obj.key.delete()
#--------------------------------------------------------------
