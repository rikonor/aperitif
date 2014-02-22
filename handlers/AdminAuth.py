# These handlers take care of Authenticating admins using cookies,
# as well as Logins and Logouts.
# *** Notice that currently, Signups are manual with the Interactive Console.

from BaseHandler import BaseHandler
from models.models import Admin
from security import hashes
from security.data_validation import *

from google.appengine.api import mail

#--------------------------------------------------------------
# User handlers
#--------------------------------------------------------------
def AdminAuthenticate(request):
        h = request.cookies.get('name_adm')
        admin_id = hashes.check_secure_val(h)
        if not admin_id:
        	return None
        admin = Admin.get_by_id(int(admin_id))
        return admin

class AdminLoginHandler(BaseHandler):

    def get(self):
        # Authenticate
        admin = AdminAuthenticate(self.request)
        if not admin:
            return self.render("/admin/admin_login.html")

        return self.redirect('/admin/home')

    def post(self):
        # Authenticate
        admin = AdminAuthenticate(self.request)

        username = self.request.get("username")
        password = self.request.get("password")

        # validate form
        if not username or not password:
        	return self.redirect("/admin/login")

        adminFind = Admin.query().filter(Admin.name==username).get()
        if not adminFind:
        	return self.redirect("/admin/login")

        adminFind = adminFind[0]
        pw_hash = adminFind.pw_hash
        # validate admin
        if not hashes.valid_pw(username, password, pw_hash):
            return self.redirect("/admin/login")

        # validation successful - set cookie headers
        admin_id = str(adminFind.key.id())
        secure_val = hashes.make_secure_val(admin_id)
        self.response.headers.add_header('Set-Cookie', str('name_adm=%s; Path=/' % secure_val))
        return self.redirect("/admin/home")
            

class AdminLogoutHandler(BaseHandler):

    def get(self):
        
        # clear cookies
        self.response.headers.add_header("Set-Cookie", "name_adm=; Path=/")
    	
        return self.redirect("/admin")

# Admin signup is done by admin-console. ("/_ah/admin/interactive/interactive")
def AddAdmin(name, password, email):
    # TODO: Validate the fields (check valid, no-duplicates).
    pw_hash = hashes.make_pw_hash(name, password)
    a = Admin(name=name,pw_hash=pw_hash,email=email)
    a.active = True
    a.put()

def ResetAdmins():
    pass
#----------------------------------------------------------------------