'''
Created on Apr 7, 2014

@author: Rohit
'''
###################################################################################################################
from django import forms
from captcha.fields import ReCaptchaField
from members.models import Member, MemberAnswers, SecurityQuestions
import datetime
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User

##################################################################################################################
class MemberLoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
           'password': forms.PasswordInput(),
        }
        
    def clean(self):
        cleaned_data = super(MemberLoginForm, self).clean()
        
        username = cleaned_data.get("username", None)
        password = cleaned_data.get("password", None)
        
        if not username:
            self._errors["username"] = self.error_class(["Please enter your username"])
            
        if not password:
            self._errors["password"] = self.error_class(["Please enter your password"])
            
        return cleaned_data

##################################################################################################################        
class MemberSignupForm1(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea(attrs={'cols': 32, 'rows': 5}))
    
    class Meta:
        model = Member
        exclude = ('user',)
        thisyear = datetime.datetime.now().year 
        widgets = {
            'dob': SelectDateWidget(years=range(thisyear-10, thisyear-60, -1)),
        }
    
    def clean(self):
        cleaned_data = super(MemberSignupForm1, self).clean()
        
        address = cleaned_data.get("address")
        dob = cleaned_data.get("dob")
                
        if not address:
            self._errors["address"] = self.error_class(["Please enter your address"])
        
        if not dob:
            self._errors["dob"] = self.error_class(["Please enter your birth date"])
            
        return cleaned_data
        
##################################################################################################################        
class MemberSignupForm2(forms.Form):
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(), required=True)
    repassword = forms.CharField(max_length=30, widget=forms.PasswordInput(), required=True)
    email = forms.EmailField(max_length=75)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        widgets = {
            'password': forms.PasswordInput(),
        }
        
    def clean(self):
        cleaned_data = super(MemberSignupForm2, self).clean()
        
        email = cleaned_data.get("email")
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        repassword = cleaned_data.get("repassword")
        first_name = cleaned_data.get("first_name")
        
        if not email:
            self._errors["email"] = self.error_class(["Please enter your email address for communication. It will never be shared/published"])
            
        if not username:
            self._errors["username"] = self.error_class(["Please enter your username"])
            
        if not password:
            self._errors["password"] = self.error_class(["Please enter your password"])
        
        if not repassword:
            self._errors["repassword"] = self.error_class(["Please enter the same password again"])
        
        if not password == repassword:
            self._errors["repassword"] = self.error_class(["Entered passwords do not match"])
            
        if not first_name:
            self._errors["first_name"] = self.error_class(["Please enter your first name for external communication. It will never be shared/published"])
            
        return cleaned_data
    
##################################################################################################################        
class SecurityQuestionAnswerForm(forms.Form):
    que1 = forms.ModelChoiceField(queryset=SecurityQuestions.objects.all(), required=True)
    que2 = forms.ModelChoiceField(queryset=SecurityQuestions.objects.all(), required=True)
    que3 = forms.ModelChoiceField(queryset=SecurityQuestions.objects.all(), required=True)
    ans1 = forms.CharField(max_length=20, required=True)
    ans2 = forms.CharField(max_length=20, required=True)
    ans3 = forms.CharField(max_length=20, required=True)
    
    def clean(self):
        cleaned_data = super(SecurityQuestionAnswerForm, self).clean()
        
        que1 = cleaned_data["que1"]
        ans1 = cleaned_data["ans1"]
        que2 = cleaned_data["que2"]
        ans2 = cleaned_data["ans2"]
        que3 = cleaned_data["que3"]
        ans3 = cleaned_data["ans3"]
        
        if que1 == que2 and que1 == que3:
            self._errors["que2"] = self.error_class(["Please select a different Security Question in this field"])
            self._errors["que3"] = self.error_class(["... and in this one too."])
        
        else:
            if que1 == que2:
                self._errors["que1"] = self.error_class(["Please select a different Security Question in this field"])
                self._errors["que2"] = self.error_class(["... or in this one."])
            
            if que1 == que3:
                self._errors["que1"] = self.error_class(["Please select a different Security Question in this field"])
                self._errors["que3"] = self.error_class(["... or in this one."])
            
            if que2 == que3:
                self._errors["que2"] = self.error_class(["Please select a different Security Question in this field"])
                self._errors["que3"] = self.error_class(["... or in this one."])
            
        return cleaned_data

###################################################################################################################
class CaptchaVerificationForm(forms.Form):
    captcha = ReCaptchaField()

##################################################################################################################
class OTPGenerationForm(forms.Form):
    email = forms.EmailField(max_length=75, required=False)
    phone = forms.CharField(max_length=13, required=False)
    
    def clean(self):
        cleaned_data = super(OTPGenerationForm, self).clean()
        
        email = cleaned_data.get("email")
        phone = cleaned_data.get("phone")
        
        if not email and not phone:
            self._errors["email"] = self.error_class(["Please enter your email address/phone for receiving One Time Password."])
            
        return cleaned_data

##################################################################################################################
class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=5, required=True)
    
##################################################################################################################
class SecurityQuestionForm(forms.ModelForm):
    answer = forms.CharField(max_length=20, required=True)
    
    class Meta:
        model = MemberAnswers
        exclude = ('member', 'question',)

##################################################################################################################
class ResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(), required=True)
    repassword = forms.CharField(max_length=30, widget=forms.PasswordInput(), required=True)
    
    class Meta:
        model = User
        fields = ('password', )
        widgets = {
            'password': forms.PasswordInput(),
        }
        
    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        
        password = cleaned_data.get("password")
        repassword = cleaned_data.get("repassword")
        
        if not password:
            self._errors["password"] = self.error_class(["Please enter your password"])
        
        if not repassword:
            self._errors["repassword"] = self.error_class(["Please enter the same password again"])
        
        if not password == repassword:
            self._errors["repassword"] = self.error_class(["Entered passwords do not match"])
            
        return cleaned_data
    
################################################################################################################## 
