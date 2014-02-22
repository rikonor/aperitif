import os, sys, datetime, time

from BaseHandler import BaseHandler
from models.models import *
from models.messages import *
from security import hashes
from handlers.AuthHandlers import *
from handlers.subscriptionHandlers import *
from handlers.MailHandlers import *

# So templates can src blobs
from google.appengine.api.images import get_serving_url
# For activation/invitation emails
from google.appengine.api import mail

#--------------------------------------------------------------
# MainPage handler
#--------------------------------------------------------------
class MainPage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            message_text = getMessage(self.request.get("message"))
            return self.render("index.html", message_text=message_text)

        return self.redirect("/home")

    def post(self):
        # Login
        email = self.request.get("email")
        password = self.request.get("password")
        userFind = User.query().filter(User.email==email).get()
        
        if not userFind:
            return self.redirect("/")
        
        pw_hash = userFind.pw_hash
        if not password or not hashes.valid_pw(email, password, pw_hash):
            return self.redirect("/")

        SetLoginCookies(self, userFind)
        return self.redirect("/home")

#--------------------------------------------------------------
# RegistrationContinue handler
#--------------------------------------------------------------
class RegistrationContinue(BaseHandler):

    def get(self):

        code = self.request.get("reg_code")
        reg_code = UserRegistrationCode.query(UserRegistrationCode.code==code).get()
        if not reg_code:
            return self.redirect("/?message=invalidcode")

        if not reg_code.uses < reg_code.max_uses:
            return self.redirect("/?message=invalidcode")
        
        return self.render("reg_continue.html", code=code)

    def post(self):
        # Get parameters (code, name, email, pw, etc.)
        # Validate params
        # Create new User and populate
        # Attach new user and code
        # Set cookies
        # Redirect to home

        code  = self.request.get("code")
        fname = self.request.get("first_name")
        lname = self.request.get("last_name")
        name = " ".join([fname, lname])
        phone = self.request.get("phone")
        email = self.request.get("email")
        aux_email = self.request.get("aux_email")
        password = self.request.get("password")
        password_repeat = self.request.get("password_repeat")

        # validation
        message_text = ""
        if not name:
            message_text = getMessage("regnameerror")
        if not message_text and not phone:
            message_text = getMessage("regphoneerror")
        if not message_text and not email:
            message_text = getMessage("regemailerror")
        if not message_text and not password:
            message_text = getMessage("regpasserror")
        if not message_text and not password or not password == password_repeat:
            message_text = getMessage("regpassrepeaterror")
        if message_text:
            return self.render("/reg_continue.html",
                    code=code,
                    fname=fname, lname=lname,
                    email=email, aux_email=aux_email,
                    phone=phone, message_text=message_text,
                    )

        reg_code = UserRegistrationCode.query(UserRegistrationCode.code==code).get()
        if not reg_code:
            return self.redirect("/")

        # ChecK that this name/email was not used before.
        userNamePresent  = User.query().filter(User.name==name).get()
        userEmailPresent = User.query().filter(User.email==email).get()
        if userNamePresent or userEmailPresent:
            return self.redirect("/")    

        # Create pw hash
        pw_hash = hashes.make_pw_hash(email, password)
        # Create new User and populate. 
        # Make empty subscription, save to db.
        u = User(name=name,pw_hash=pw_hash, phone=phone, email=email)
        u.used_codes.append(reg_code.key)
        u.rests.append(reg_code.rest)
        s = Subscription(typeOf='empty')
        u.put()
        # Attach user, code, rest and subscription.
        reg_code.users.append(u.key)
        reg_code.last_used = datetime.datetime.now()
        reg_code.uses = reg_code.uses + 1
        reg_code.put()
        rest = reg_code.rest.get()
        rest.users.append(u.key)
        rest.put()
        s.user = u.key
        s.rest = rest.key
        s.put()
        u.subscriptions.append(s.key)
        u.put()
        # Create and set cookies.
        SetLoginCookies(self, u)
        # Inactive (by default), send an activation email.
        SendActivationEmail(u)
        return self.redirect("/activation_required")

#--------------------------------------------------------------
# ActivationRequiredPage handler
#--------------------------------------------------------------
class ActivationRequiredPage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.render("activation_required.html")

        return self.redirect("/home")

    def post(self):
        user = Authenticate(self.request)
        if user:
            return self.redirect("/home")
        
        user = User.query().filter(User.email == self.request.get("email")).get()
        if not user:
            return self.redirect("/activation_required?message=emailnotfound")

        if not user.active:
            SendActivationEmail(u)
            return self.redirect("/activation_required?message=sentactivationemail")
        
#--------------------------------------------------------------
# ActivationHandler
#--------------------------------------------------------------
class ActivationHandler(BaseHandler):

    def get(self):
        token = self.request.get("token")
        token_id, token_date = token.split(",")

        user = User.getById(token_id)
        if not user or not token_date == "%s" % user.created.strftime("%f"):
            return self.redirect("/?message=activationerror")

        user.active = True
        user.put()
        time.sleep(0.1)
        # Create and set cookie.
        SetLoginCookies(self, user)
        return self.redirect("/subscription?id="+str(user.getUserSubscription().key.id()))
            
#--------------------------------------------------------------
# HomePage handler
#--------------------------------------------------------------
class HomePage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        user.last_visit = datetime.datetime.now()
        user.put()
        time.sleep(0.1)

        return self.render("home.html", user=user)

#--------------------------------------------------------------
# ContactPage handler
#--------------------------------------------------------------
class ContactPage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        message_text = getMessage(self.request.get("message"))        
        return self.render("contact.html",
            user=user, message_text=message_text)

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        subject = self.request.get("subject")
        message = self.request.get("user_message")
        if not message:
            return self.redirect("/contact?message=invalidmessage")

        SendContactEmail(user=user, subject=subject, message=message)
        return self.redirect("/contact")

#--------------------------------------------------------------
# AboutPage handler
#--------------------------------------------------------------
class AboutPage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        return self.render("about.html", user=user)
            
#--------------------------------------------------------------
# ProfilePage handler
#--------------------------------------------------------------
class ProfilePage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        message_text = getMessage(self.request.get("message"))
        return self.render("profile.html", user=user, message_text=message_text)
            
#--------------------------------------------------------------
# ProfileEditPage handler
#--------------------------------------------------------------
class ProfileEditPage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")
            
        return self.render("profile_edit.html", user=user)    

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        fname = self.request.get("first_name")
        lname = self.request.get("last_name")
        name  = " ".join([fname, lname])
        phone = self.request.get("phone")
        email = self.request.get("email")
        aux_email = self.request.get("aux_email")
        # TODO: Validate data

        user.name  = name
        user.phone = phone
        user.email = email
        user.aux_email = aux_email
        user.put()
        time.sleep(0.1)

        return self.redirect("/profile")
            
#--------------------------------------------------------------
# ProfileChangePassword handler
#--------------------------------------------------------------
class ProfileChangePassword(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        message_text = getMessage(self.request.get("message"))
        return self.render("profile_change_password.html", user=user, message_text=message_text)    

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        old_password = self.request.get("old_password")
        new_password = self.request.get("new_password")
        new_password_repeat = self.request.get("new_password_repeat")
        # TODO: Validate data
        if not new_password:
            return self.redirect("/profile/change_password?message=regpasserror")

        if not old_password or not hashes.valid_pw(user.email, old_password, user.pw_hash):
            return self.redirect("/profile/change_password?message=wrongpassword")

        if not new_password == new_password_repeat:
            return self.redirect("/profile/change_password?message=regpassrepeaterror")

        SetUserPassword(user, new_password)
        
        return self.redirect("/profile?message=passwordchanged")
            
#--------------------------------------------------------------
# InviteHandler
#--------------------------------------------------------------
class InviteHandler(BaseHandler):

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        invite_email = self.request.get("email")
        if not invite_email:
            return self.redirect("/profile?message=invalidinviteemail")

        if not user.invitations > 0:
            return self.redirect("/profile?message=nomoreinvites")

        # Get restaurant and invite email
        rest_id = self.request.get("rest")
        rest = Restaurant.getById(rest_id)
        if not rest:
            return self.redirect("/profile?message=restaurantnotfound")

        # Create a new UserRegistrationCode
        code = (user.name+" "+str(len(user.gen_codes)+1)).replace(" ","_")
        max_uses = 1
        UserRegistrationCode.createCode(code, max_uses, user.key, rest.key)
        # Send invitation
        SendInvitationEmail(user, rest, invite_email, code)
        # Decrease available invitations
        user.invitations = user.invitations-1
        user.put()
        time.sleep(0.1)

        return self.redirect("/profile?message=invitesuccess")

#--------------------------------------------------------------
# ReservePage handler
#--------------------------------------------------------------
class ReservePage(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        # TODO: Limit the number of reservations showing.
        message_text = getMessage(self.request.get("message"))
        reservations = user.reservations
        subscriptions = user.subscriptions
        return self.render("reserve.html", user=user, subscriptions=subscriptions, message_text=message_text)
    
#--------------------------------------------------------------
# ReserveEdit handler
#--------------------------------------------------------------
class ReserveEdit(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        reservation_id = self.request.get("id")
        reservation = Reservation.getById(reservation_id)
        if not reservation:
            return self.redirect("/reserve?message=reservationnotfound")

        return self.render("reserve_edit.html", user=user, reservation=reservation)

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        reservation_id = self.request.get("id")
        reservation = Reservation.getById(reservation_id)
        if not reservation:
            return self.redirect("/reserve?message=reservationnotfound")

        new_date = self.request.get("date")
        new_time = self.request.get("time")
        try:
            new_dt = datetime.datetime.strptime(" ".join([new_date, new_time]), "%m/%d/%Y %I:%M%p")
            reservation.dt = new_dt
            reservation.put()
            time.sleep(0.1)
            return self.redirect("/reserve/edit?id="+reservation_id)
        except:
            return self.redirect("/reserve/edit?id="+reservation_id+"&message=editfailed")

#--------------------------------------------------------------
# ReserveCancel handler
#--------------------------------------------------------------
class ReserveCancel(BaseHandler):

    def get(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        message_text = getMessage(self.request.get("message"))
        reservation_id = self.request.get("id")
        reservation = Reservation.getById(reservation_id)
        if not reservation:
            return self.redirect("/reserve?message=reservationnotfound")

        return self.render("reserve_cancel.html", user=user, reservation=reservation, message_text=message_text)    

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        reservation_id = self.request.get("id")
        reservation = Reservation.getById(reservation_id)
        if not reservation:
            return self.redirect("/reserve?message=reservationnotfound")

        cancel_confirm = self.request.get("cancel_confirm")
        if not cancel_confirm == 'on':
            return self.redirect("/reserve/cancel?id="+reservation_id+"&message=cancelfailed")

        new_id = cancelReservation(reservation)
        cancelledReservation = ReservationCancelled.getById(new_id)
        return self.redirect("/subscription/view?id="+str(cancelledReservation.subscription.id())+"&message=cancelsuccess")

#--------------------------------------------------------------
# RestaurantAdd handler - Add another restaurant to user's collection
#--------------------------------------------------------------
class RestaurantAdd(BaseHandler):

    def post(self):
        user = Authenticate(self.request)
        if not user:
            return self.redirect("/")

        reg_code = UserRegistrationCode.query(UserRegistrationCode.code==self.request.get("reg_code")).get()
        if not reg_code:
            return self.redirect("/reserve?message=invalidcode")
        
        if reg_code.uses >= reg_code.max_uses:
            return self.redirect("/reserve?message=maxuse")

        rest = reg_code.rest.get()
        if rest.key in user.rests:
            return self.redirect("/reserve?message=used")

        user.used_codes.append(reg_code.key)
        user.rests.append(rest.key)
        s = Subscription(typeOf='empty')
        user.put()
        # Attach user, code, rest and subscription.
        reg_code.users.append(user.key)
        reg_code.last_used = datetime.datetime.now()
        reg_code.uses = reg_code.uses + 1
        reg_code.put()
        rest.users.append(user.key)
        rest.put()
        s.user = user.key
        s.rest = rest.key
        s.put()
        user.subscriptions.append(s.key)
        user.put()
        return self.redirect("/reserve")

#--------------------------------------------------------------
# LogoutHandler
#--------------------------------------------------------------
class LogoutHandler(BaseHandler):

    def get(self):    
        ClearLoginCookies(self)
        return self.redirect("/")