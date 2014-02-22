# These handlers take care of Authenticating users using cookies,
# as well as Logins, Logouts and Signups.

import os, sys, time, datetime

from handlers.BaseHandler import BaseHandler
from handlers.MailHandlers import *
from models.models import User
from models.messages import *
from security import hashes
from security.data_validation import *

from google.appengine.api import mail

#--------------------------------------------------------------
# User handlers
#--------------------------------------------------------------
def Authenticate(request):
    h = request.cookies.get('name')
    user_id = hashes.check_secure_val(h)
    if user_id:
        user = User.getById(user_id)
        if user and user.active:
            return user
#--------------------------------------------------------------
def SetLoginCookies(request, user):
    user_id = str(user.key.id())
    secure_val = hashes.make_secure_val(user_id)
    request.response.headers.add_header('Set-Cookie', str("name=%s; Path=/" % secure_val))
#--------------------------------------------------------------
def ClearLoginCookies(request):
    request.response.headers.add_header("Set-Cookie", "name=; Path=/")
#--------------------------------------------------------------
def SetUserPassword(user, new_password):
    user.pw_hash = hashes.make_pw_hash(user.email, new_password)
    user.put()
    time.sleep(0.1)
#--------------------------------------------------------------
class ForgotPasswordHandler(BaseHandler):

    def get(self):
        self.render("forgot_password.html")

    def post(self):
        email = self.request.get("email")
        user = User.query(User.email==email).get()
        if user:
            SendPasswordRecoveryEmail(user)
        self.redirect("/?message=passwordresetemail")
#--------------------------------------------------------------
class ResetPasswordHandler(BaseHandler):

    def get(self):
        token = self.request.get("token")
        try:
            user_id, recovery_token = token.split(",")    
        except:
            return self.redirect("/")

        user = User.getById(user_id)
        if not user or not recovery_token == "%s" % user.created.strftime("%f"):
            return self.redirect("/")

        return self.render("reset_password.html", token=token)
        
    def post(self):
        token = self.request.get("token")
        try:
            user_id, recovery_token = token.split(",")
        except:
            return self.redirect("/")

        user = User.getById(user_id)
        if not user or not recovery_token == "%s" % user.created.strftime("%f"):
            return self.redirect("/")
        
        # TODO: Validate password (6 chars etc.)
        new_password = self.request.get("password")
        new_password_repeat = self.request.get("password_repeat")
        if not new_password:
            return self.render("reset_password.html", token=token, message_text=getMessage("regpasserror"))

        if not new_password == new_password_repeat:
            return self.render("reset_password.html", token=token, message_text=getMessage("regpassrepeaterror"))

        SetUserPassword(user, new_password)
        return self.redirect("/?message=passwordreset")

#--------------------------------------------------------------
class LogoutHandler(BaseHandler):

    def get(self):
        ClearLoginCookies(self)
        return self.redirect("/")
#--------------------------------------------------------------