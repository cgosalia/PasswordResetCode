'''
Created on Apr 06, 2014

@author: rkhapare
'''
##################################################################################################################
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import ForeignKey

##################################################################################################################
class Member(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    phone_no = models.CharField(max_length=13, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

##################################################################################################################    
class SecurityQuestions(models.Model):
    question = models.CharField(max_length=500, blank=False, null=False)
    
    def __unicode__(self):
        return u'%s' % (self.question)
    
##################################################################################################################
class MemberAnswers(models.Model):
    member = ForeignKey('Member', null=False)
    question = ForeignKey('SecurityQuestions', null=False)
    answer = models.CharField(max_length=20, blank=False, null=False)
    
    def __unicode__(self):
        return u'%s' % (self.answer)
    
##################################################################################################################