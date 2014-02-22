import os, sys, datetime, time
from handlers.BaseHandler import BaseHandler
from models.models import *
from models.messages import *
from handlers.AdminAuth import AdminAuthenticate
from handlers.subscriptionHandlers import *

# So templates can src image blobs
from google.appengine.api.images import get_serving_url

#--------------------------------------------------------------
# AdminHandler
#--------------------------------------------------------------
class AdminHandler(BaseHandler):

    def get(self):
        # Authenticate
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin/login")

        message_text = getMessage(self.request.get("message"))
        return self.render("admin/admin_home.html", admin=admin, message_text=message_text)

#--------------------------------------------------------------
# AdminHome handler
#--------------------------------------------------------------
class AdminHome(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        message_text = getMessage(self.request.get("message"))
        return self.render("admin/admin_home.html", admin=admin, message_text=message_text)
            
#--------------------------------------------------------------
# AdminRests handler
#--------------------------------------------------------------
class AdminRests(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        message_text = getMessage(self.request.get("message"))
        rests = Restaurant.query().order(Restaurant.name).fetch()
        return self.render("admin/admin_rests.html",
            admin=admin, rests=rests, message_text=message_text)
            
#--------------------------------------------------------------
# AdminRestAdd handler
#--------------------------------------------------------------
class AdminRestAdd(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        message_text = getMessage(self.request.get("message"))
        return self.render("admin/admin_rest_add.html",
            admin=admin, message_text=message_text)

    def post(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        name    = self.request.get("name")
        address = self.request.get("address")
        phone   = self.request.get("phone")
        email   = self.request.get("email")

        # TODO: Validate
        if name and address and phone and email:
            new_rest = Restaurant(name=name, address=address, phone=phone, email=email)
            new_rest.initHours()
            new_rest.put()
            time.sleep(0.1)
        return self.redirect("/admin/rests")
            
#--------------------------------------------------------------
# AdminRestView handler
#--------------------------------------------------------------
class AdminRestView(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        message_text = getMessage(self.request.get("message"))
        rest_id = self.request.get("id")
        rest = Restaurant.getById(rest_id)
        if not rest:
            return self.redirect("/admin/rests?message=restaurantnotfound")

        reservations = Reservation.query(Reservation.rest == rest.key).order(+Reservation.dt).fetch()
        return self.render("admin/admin_rest_view.html",
            admin=admin, rest=rest, reservations=reservations, message_text=message_text)        
            
#--------------------------------------------------------------
# AdminRestEdit handler
#--------------------------------------------------------------
class AdminRestEdit(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        rest_id = self.request.get("id")
        rest = Restaurant.getById(rest_id)
        if not rest:
            return self.redirect("/admin/rests?message=restaurantnotfound")

        return self.render("admin/admin_rest_edit.html", admin=admin, rest=rest)
            
    def post(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        rest_id = self.request.get("id")
        rest = Restaurant.getById(rest_id)
        if not rest:
            return self.redirect("/admin/rests?message=restaurantnotfound")

        # TODO: Validate
        rest.name    = self.request.get("name")
        rest.address = self.request.get("address")
        rest.phone   = self.request.get("phone")
        rest.email   = self.request.get("email")

        rest.put()
        time.sleep(0.1)
        
        return self.redirect("/admin/rests")    
#--------------------------------------------------------------
# AdminRestEditHours handler
#--------------------------------------------------------------
class AdminRestEditHours(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        rest_id = self.request.get("id")
        rest = Restaurant.getById(rest_id)
        if not rest:
            return self.redirect("/admin/rests?message=restaurantnotfound")

      	hoursInfo = rest.getHoursInfo()
        message_text = getMessage(self.request.get("message"))
        return self.render("admin/admin_rest_edit_hours.html",
        	admin=admin, rest=rest, hoursInfo=hoursInfo, message_text=message_text)

    def post(self):
    	admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        rest_id = self.request.get("id")
        rest = Restaurant.getById(rest_id)
        if not rest:
            return self.redirect("/admin/rests?message=restaurantnotfound")

        open_hours = []
        for h in xrange(8,24):
        	if self.request.get("hour"+str(h)):
        		open_hours.append(datetime.time(hour=h))
        rest.open_hours = open_hours
        rest.put()
        time.sleep(0.1)

        self.redirect("/admin/rests/edithours?id="+str(rest.key.id()))
#--------------------------------------------------------------
# AdminUsers handler
#--------------------------------------------------------------
class AdminUsers(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        message_text = getMessage(self.request.get("message"))
        users = User.query().order(User.name).fetch()
        return self.render("admin/admin_users.html",
            admin=admin, users=users, message_text=message_text)
            
#--------------------------------------------------------------
# AdminUserView handler
#--------------------------------------------------------------
class AdminUserView(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        user_id = self.request.get("id")
        user = User.getById(user_id)
        if not user:
            return self.redirect("/admin/users?message=usernotfound")

        cancelledReservations = ReservationCancelled.query(ReservationCancelled.user == user.key).order(ReservationCancelled.dt).fetch()
        return self.render("admin/admin_user_view.html",
            admin=admin, user=user, cancelledReservations=cancelledReservations)            
            
#--------------------------------------------------------------
# AdminUserEdit handler
#--------------------------------------------------------------
class AdminUserEdit(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        user_id = self.request.get("id")
        user = User.getById(user_id)
        if not user:
            return self.redirect("/admin/users?message=usernotfound")

        return self.render("admin/admin_user_edit.html",
            admin=admin, user=user)

    def post(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            self.redirect("/admin")

        user_id = self.request.get("id")
        user = User.getById(user_id)
        if not user:
            return self.redirect("/admin/users?message=usernotfound")

        # TODO: Validate
        user.name    = " ".join([self.request.get("first_name"), self.request.get("last_name")])
        user.phone   = self.request.get("phone")
        user.email   = self.request.get("email")

        user.put()
        time.sleep(0.1)

        return self.redirect("/admin/users")
            
#--------------------------------------------------------------
# AdminUserActivate handler
#--------------------------------------------------------------
class AdminUserActivate(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        user_id = self.request.get("id")
        user = User.getById(user_id)
        if not user:
            return self.redirect("/admin/users?message=usernotfound")

        user.active = True
        user.put()
        time.sleep(0.1)

        return self.redirect("/admin/users/view?id="+user_id)    
            
#--------------------------------------------------------------
# AdminUserResetInvitations handler
#--------------------------------------------------------------
class AdminUserResetInvitations(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        user_id = self.request.get("id")
        user = User.getById(user_id)
        if not user:
            return self.redirect("/admin/users?message=usernotfound")

        if user.invitations < 10:
            user.invitations = 10
            user.put()
            time.sleep(0.1) 

        return self.redirect("/admin/users/view?id="+user_id)            
            
#--------------------------------------------------------------
# AdminCodes handler
#--------------------------------------------------------------
class AdminCodes(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        message_text = getMessage(self.request.get("message"))
        rests = Restaurant.query().order(Restaurant.name).fetch()
        codes = UserRegistrationCode.query().order(-UserRegistrationCode.created).fetch()
        return self.render("admin/admin_codes.html",
            admin=admin, codes=codes, rests=rests, message_text=message_text)

    def post(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        rest = Restaurant.getById(self.request.get("rest"))
        code = self.request.get("code")
        max_uses = self.request.get("max_uses")
        if not max_uses:
            max_uses = 1
        else:
            max_uses = int(max_uses)
        if code and rest: # Check not empty
            UserRegistrationCode.createCode(code, max_uses, admin.key, rest.key)

        return self.redirect("/admin/codes")

#--------------------------------------------------------------
# AdminCodeEdit handler
#--------------------------------------------------------------
class AdminCodeEdit(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        code_id = self.request.get("id")
        code = UserRegistrationCode.getById(code_id)
        if not code:
            return self.redirect("/admin/codes?message=codenotfound")

        rests = Restaurant.query().order(Restaurant.name).fetch()
        return self.render("admin/admin_code_edit.html", admin=admin, code=code, rests=rests)            

    def post(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        code_id = self.request.get("id")
        code = UserRegistrationCode.getById(code_id)
        if not code:
            return self.redirect("/admin/codes?message=codenotfound")

        new_code = self.request.get("code")
        if not new_code:
            return self.redirect("/admin/code?message=editfailed")

        new_max_uses = self.request.get("max_uses")     
        if not new_max_uses:
            new_max_uses = 1
        else:
            new_max_uses = int(new_max_uses)

        code.code = new_code
        code.max_uses = new_max_uses
        code.put()
        time.sleep(0.1)

        self.redirect("/admin/codes")

#--------------------------------------------------------------
# AdminCodeDisable handler
#--------------------------------------------------------------
class AdminCodeDisable(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if admin:
            return self.redirect("/admin")

        code_id = self.request.get("id")
        code = UserRegistrationCode.getById(code_id)
        if not code:
            return self.redirect("/admin/codes?message=codenotfound")

        code.max_uses = 0
        code.put()
        time.sleep(0.1)

        return self.redirect("/admin/codes")   
            
#--------------------------------------------------------------
# AdminSubscriptionView handler
#--------------------------------------------------------------
class AdminSubscriptionView(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/admin/subscriptions?message=subscriptionnotfound")

        message_text = getMessage(self.request.get("message"))        
        reservations = Reservation.query(Reservation.subscription == subscription.key).order(+Reservation.dt).fetch()
        cancelledReservations = ReservationCancelled.query(ReservationCancelled.subscription == subscription.key).order(ReservationCancelled.dt).fetch()
        return self.render("admin/admin_subscription_view.html",
            admin=admin,
            subscription=subscription,
            reservations=reservations,
            cancelledReservations=cancelledReservations,
            message_text=message_text)    

#--------------------------------------------------------------
# AdminSubscriptionEdit handler
#--------------------------------------------------------------
class AdminSubscriptionEdit(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if subscription:
            return self.redirect("/admin/users?message=subscriptionnotfound")

        if subscription.typeOf == 'empty':
            return self.redirect("/admin/subscriptions/view?id="+subscription_id+"&message=subscriptioncanteditempty")

        return self.render("admin/admin_subscription_edit.html", admin=admin, subscription=subscription)
            
    def post(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/admin/subscriptions?message=subscriptionnotfound")

        new_time = self.request.get("time")
        new_time = datetime.datetime.strptime(new_time, "%I:%M%p")
        subscription.start_date = subscription.start_date.replace(hour=new_time.hour, minute=new_time.minute)
        subscription.put()
        time.sleep(0.1)

        return self.redirect("/admin/subscriptions/view?id="+subscription_id)
            
#--------------------------------------------------------------
# AdminSubscriptionEdit handler
#--------------------------------------------------------------
class AdminSubscriptionChangeType(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        subscription_id = self.request.get("id")
        subscription = Subscription.getById(subscription_id)
        if not subscription:
            return self.redirect("/admin/subscriptions?message=subscriptionnotfound")

        new_type = self.request.get("new_type")
        SubscriptionChangeType(subscription, new_type)

        return self.redirect("/admin/subscriptions/view?id="+subscription_id)
            
#--------------------------------------------------------------
# AdminReservationEdit handler
#--------------------------------------------------------------
class AdminReservationEdit(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        message_text = getMessage(self.request.get("message"))
        reservation_id = self.request.get("id")
        
        # normal
        reservation = Reservation.getById(reservation_id)
        if reservation:
            return self.render("admin/admin_reservation_edit.html",
                admin=admin, reservation=reservation, message_text=message_text)

        # cancelled 
        reservation = ReservationCancelled.getById(reservation_id)
        if reservation:
            return self.render("admin/admin_reservation_cancelled.html",
                admin=admin, reservation=reservation)

        # not found
        return self.redirect("/admin/reservations?message=reservationnotfound")

    def post(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")        

        reservation_id = self.request.get("id")
        reservation = Reservation.getById(reservation_id)
        if not reservation:
            return self.redirect("/admin/reservations?message=reservationnotfound")

        new_date = self.request.get("date")
        new_time = self.request.get("time")
        try:
            new_dt = datetime.datetime.strptime(" ".join([new_date, new_time]), "%m/%d/%Y %I:%M%p")
            reservation.dt = new_dt
            reservation.put()
            time.sleep(0.1)
            return self.redirect("/admin/reservations/edit?id="+reservation_id)
        except:
            return self.redirect("/admin/reservations/edit?id="+reservation_id+"&message=editfailed")
            
#--------------------------------------------------------------
# AdminReservationCancel handler
#--------------------------------------------------------------
class AdminReservationCancel(BaseHandler):

    def get(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        message_text = getMessage(self.request.get("message"))
        reservation_id = self.request.get("id")
        reservation = Reservation.getById(reservation_id)
        if not reservation:
            return self.redirect("/admin/reservations?message=reservationnotfound")

        return self.render("admin/admin_reservation_cancel.html", admin=admin, reservation=reservation, message_text=message_text)

    def post(self):
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin")

        cancel_confirm = self.request.get("cancel_confirm")
        if not cancel_confirm == 'on':
            return self.redirect("/admin/reservations/cancel?id="+reservation_id+"&message=cancelfailed")

        reservation_id = self.request.get("id")
        reservation = Reservation.getById(reservation_id)
        if not reservation:
            return self.redirect("/admin/reservations?message=reservationnotfound")

        new_id = cancelReservation(reservation)
        return self.redirect("/admin/reservations/edit?id="+new_id)
            
#--------------------------------------------------------------