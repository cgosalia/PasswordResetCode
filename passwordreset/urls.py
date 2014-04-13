'''
Created on Apr 07, 2014

@author: rkhapare
'''
##################################################################################################################
from django.conf.urls import *

##################################################################################################################
urlpatterns = patterns('members.views',
                        url(r'^$', 'login_view'),
#                         url('^signin/$', 'login_view'),
                        url('^blank/$', 'blank_view'),
                        url('^logout/$', 'logout_view'),
                        url('^signup/$', 'signup_view'),
                        url('^captcha/$', 'captcha_view'),
                        url('^otpgen/$', 'generate_otp_view'),
                        url('^otpvfy/$', 'verify_otp_view'),
                        url('^secque/$', 'furnish_securityQs_view'),
                        url('^repwd/$', 'change_password_view'),
)
##################################################################################################################