from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
import datetime, time

from security.hashes import ADMINS

# 1 User
# 2 Restaurant
# 3 UserRegistrationCode
# 4 Reservation
# 5 Admin
# 6 Address
# 7 Contact

#-----------------------------------------------------------------------------------
# User class
#-----------------------------------------------------------------------------------
class User(ndb.Model):
	# Properties
	name = ndb.StringProperty(required = True)
	pw_hash = ndb.StringProperty(required = True)
	phone   = ndb.StringProperty(required = True)
	email   = ndb.StringProperty(required = True)
	aux_email = ndb.StringProperty(default="")
	active	= ndb.BooleanProperty(default = False)
	invitations = ndb.IntegerProperty(default = 10)
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_visit = ndb.DateTimeProperty(auto_now_add = True)
	
	# References
	gen_codes    = ndb.KeyProperty(kind='UserRegistrationCode', repeated=True)
	used_codes   = ndb.KeyProperty(kind='UserRegistrationCode', repeated=True)
	rests        = ndb.KeyProperty(kind='Restaurant', repeated=True)
	subscriptions= ndb.KeyProperty(kind='Subscription', repeated=True)
	reservations = ndb.KeyProperty(kind='Reservation', repeated=True)

	@classmethod
	def getById(cls, id_x):
		if id_x.isdigit():
			return cls.get_by_id(int(id_x))
		if type(id_x) == 'int':
			return cls.get_by_id(id_x)

	def getReservations(self, rest=None):
		r = None
		if rest:
			r = Reservation.query(ndb.AND(Reservation.user == self.key,
										  Reservation.rest == rest.key)).order(+Reservation.dt).fetch()
		else:
			r = Reservation.query(Reservation.user == self.key).order(+Reservation.dt).fetch()
		return r

	def getNextReservation(self, rest=None):
		r = None
		if rest:
			r = Reservation.query(ndb.AND(Reservation.user == self.key,
										  Reservation.rest == rest.key)).order(+Reservation.dt).get()
		else:
			r = Reservation.query(Reservation.user == self.key).order(+Reservation.dt).get()
		return r

	def getUserSubscription(self, name=None):
		if self.subscriptions:
			if name:
				for subscription in self.subscriptions:
					if subscription.get().rest.get().name == name:
						return subscription.get() 
			else:
				return self.subscriptions[0].get()

#-----------------------------------------------------------------------------------
# Restaurant class (And RestOpenInterval)
#-----------------------------------------------------------------------------------
class Restaurant(ndb.Model):
	# Properties
	name    = ndb.StringProperty(required = True)
	address = ndb.StringProperty(required = True)
	phone   = ndb.StringProperty(required = True)
	email   = ndb.StringProperty(required = True)
	created = ndb.DateTimeProperty(auto_now_add = True)
	open_hours = ndb.TimeProperty(repeated = True)

	# References
	contacts 	 = ndb.KeyProperty(kind='Contact', repeated = True)
	users    	 = ndb.KeyProperty(kind='User', repeated = True)
	reservations = ndb.KeyProperty(kind='Reservation', repeated = True)

	def initHours(self):
		for h in xrange(8,24):
			self.open_hours.append(datetime.time(hour=h))

	def getHoursInfo(self):
		hoursInfo = []
		for h in xrange(8,24):
			hour = datetime.time(hour=h)
			if hour in self.open_hours:
				hoursInfo.append( (hour, True) )
			else:
				hoursInfo.append( (hour, False) )
		return hoursInfo

	def getOpenIntervals(self):
		intervals = []
		hoursInfo = self.getHoursInfo()
		i = 0
		while i < len(hoursInfo):
			if hoursInfo[i][1]:
				for j in range(i, len(hoursInfo)):
					if not hoursInfo[j][1]:
						intervals.append( (hoursInfo[i][0], hoursInfo[j][0]) )
						i = j
						break
			i = i+1
		return intervals

	def checkIfOpen(self, t):
		simpleT = datetime.time(hour=t.hour)
		if simpleT in self.open_hours:
			return True

	@classmethod
	def getById(cls, id_x):
		if id_x.isdigit():
			return cls.get_by_id(int(id_x))
		if type(id_x) == 'int':
			return cls.get_by_id(id_x)

#-----------------------------------------------------------------------------------
# UserRegistrationCode class
#-----------------------------------------------------------------------------------
class UserRegistrationCode(ndb.Model):
	# Properties
	code 	 = ndb.StringProperty(required = True)
	uses 	 = ndb.IntegerProperty(required = True, default=0)
	max_uses = ndb.IntegerProperty(required = True, default=1)
	last_used = ndb.DateTimeProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)

	# References
	rest    = ndb.KeyProperty(kind='Restaurant', required = True)
	issuer  = ndb.KeyProperty(required = True)
	users   = ndb.KeyProperty(kind='User', repeated=True)

	@classmethod
	def getById(cls, id_x):
		if id_x.isdigit():
			return cls.get_by_id(int(id_x))
		if type(id_x) == 'int':
			return cls.get_by_id(id_x)

	@staticmethod
	def createCode(code, max_uses, issuer_key, rest):
		# If code already exists, return None
		findCode = UserRegistrationCode.query(UserRegistrationCode.code==code).fetch()
		if not findCode:
			new_code = UserRegistrationCode(code=code, max_uses=max_uses,issuer=issuer_key, rest=rest)
			code_key = new_code.put()
			issuer = issuer_key.get()
			issuer.gen_codes.append(code_key)
			issuer.put()
			time.sleep(0.1)
			return True
#-----------------------------------------------------------------------------------
# Reservation class
#-----------------------------------------------------------------------------------
class ReservationAbstract(ndb.Model):
	# Properties
	table_n = ndb.StringProperty()
	dt = ndb.DateTimeProperty(required = True)
	created = ndb.DateTimeProperty(auto_now_add = True)

	# References
	rest = ndb.KeyProperty(kind='Restaurant', required = True)
	user = ndb.KeyProperty(kind='User', required = True)
	subscription = ndb.KeyProperty(kind='Subscription')

	def typeOf(self):
		return self.__class__.__name__

	@classmethod
	def getById(cls, id_x):
		if id_x.isdigit():
			return cls.get_by_id(int(id_x))
		if type(id_x) == 'int':
			return cls.get_by_id(id_x)

class Reservation(ReservationAbstract):
	pass

class ReservationCancelled(ReservationAbstract):
	pass

class ReservationGifted(ReservationAbstract):
	pass

class ReservationPassed(ReservationAbstract):
	pass
#-----------------------------------------------------------------------------------
# Admin class
#-----------------------------------------------------------------------------------
class Admin(ndb.Model):
	# Properties
	name = ndb.StringProperty(required = True)
	pw_hash = ndb.StringProperty(required = True)
	email   = ndb.StringProperty(required = True)
	active  = ndb.BooleanProperty(default = True)
	created = ndb.DateTimeProperty(auto_now_add = True)
	last_visit = ndb.DateTimeProperty()

	# References
	gen_codes = ndb.KeyProperty(kind='UserRegistrationCode', repeated=True)

#-----------------------------------------------------------------------------------
# Contact class
#-----------------------------------------------------------------------------------
class Contact(ndb.Model):
	# Properties
	name	 =	ndb.StringProperty(required=True)
	phone	 =	ndb.StringProperty()
	email 	 =	ndb.StringProperty()
	position = 	ndb.StringProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)

#-----------------------------------------------------------------------------------
# Subscription class
#-----------------------------------------------------------------------------------
class Subscription(ndb.Model):
	# Properties
	typeOf = ndb.StringProperty()
	start_date = ndb.DateTimeProperty()
	created = ndb.DateTimeProperty(auto_now_add = True)

	# References
	user = ndb.KeyProperty(kind='User', required=True)
	rest = ndb.KeyProperty(kind='Restaurant', required=True)
	reservations = ndb.KeyProperty(kind='Reservation', repeated=True)
	transaction = ndb.KeyProperty(kind='Transaction')

	@classmethod
	def getById(cls, id_x):
		if id_x.isdigit():
			return cls.get_by_id(int(id_x))
		if type(id_x) == 'int':
			return cls.get_by_id(id_x)
#-----------------------------------------------------------------------------------
# Transaction class
#-----------------------------------------------------------------------------------
class Transaction(ndb.Model):
	# Properties
	stripe_customer_id = ndb.StringProperty(required=True)

	# References
	subscription = ndb.KeyProperty(kind='Subscription', required=True)
	user = ndb.KeyProperty(kind='User', required=True)
#-----------------------------------------------------------------------------------