import os, sys, datetime, time

from handlers.BaseHandler import BaseHandler
from models.models import *
from handlers.AdminAuth import *

# Excel stuff
from openpyxl import Workbook
from openpyxl.cell import get_column_letter

class BackupCreate(BaseHandler):

	def get(self):
		pass

class BackupDownload(BaseHandler):

	def get(self):
		admin = AdminAuthenticate(self.request)
        if not admin:
            return self.redirect("/admin/login")

        return self.render("admin/admin_backup_download.html")

#--------------------------------------------------------------------
# Backup methods
#--------------------------------------------------------------------
def createBackup:
	# Create Excel Workbook
	pass
	# New worksheet (Users)


	# New worksheet (Codes)

	# ...