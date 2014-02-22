#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handlers import *
from handlers.Aperitif import *
from handlers.AuthHandlers import *
from handlers.paymentHandlers import *
from handlers.subscriptionHandlers import *
from handlers.Admin import *
from handlers.AdminAuth import *

#This is the place where all of your URL mapping goes
route_list = [
	('/', MainPage),
	('/reg_continue', RegistrationContinue),
	('/activation_required', ActivationRequiredPage),
	('/activate', ActivationHandler),
	('/forgot_password', ForgotPasswordHandler),
	('/reset_password', ResetPasswordHandler),
	('/logout', LogoutHandler),
	('/home', HomePage),
	('/contact', ContactPage),
	('/about', AboutPage),
	('/profile', ProfilePage),
	('/invite', InviteHandler),
	('/profile/edit', ProfileEditPage),
	('/profile/change_password', ProfileChangePassword),
	('/reserve', ReservePage),
	('/reserve/edit', ReserveEdit),
	('/reserve/cancel', ReserveCancel),
	('/subscription', SubscriptionHandler),
	('/subscription/new', SubscriptionNew),
	('/subscription/view', SubscriptionView),
	('/subscription/edit', SubscriptionEdit),
	('/subscription/cancel', SubscriptionCancel),
	('/restaurant/add', RestaurantAdd),
	('/admin', AdminHandler),
	('/admin/home', AdminHome),
	('/admin/rests', AdminRests),
	('/admin/rests/view', AdminRestView),
	('/admin/rests/edit', AdminRestEdit),
	('/admin/rests/edithours', AdminRestEditHours),
	('/admin/rests/add', AdminRestAdd),
	('/admin/users', AdminUsers),
	('/admin/users/view', AdminUserView),
	('/admin/users/edit', AdminUserEdit),
	('/admin/users/activate', AdminUserActivate),
	('/admin/users/reset_invitations', AdminUserResetInvitations),
	('/admin/codes', AdminCodes),
	('/admin/codes/edit', AdminCodeEdit),
	('/admin/codes/disable', AdminCodeDisable),
	('/admin/subscriptions/view', AdminSubscriptionView),
	('/admin/subscriptions/edit', AdminSubscriptionEdit),
	('/admin/subscriptions/change_type', AdminSubscriptionChangeType),
	('/admin/reservations/edit', AdminReservationEdit),
	('/admin/reservations/cancel', AdminReservationCancel),
	('/admin/login', AdminLoginHandler),
	('/admin/logout', AdminLogoutHandler),
	]
