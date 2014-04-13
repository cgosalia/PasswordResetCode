'''
Created on Apr 7, 2014

@author: Rohit
'''
###################################################################################################################
from django.core.context_processors import csrf
from django.contrib.auth import logout, login, authenticate
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.core.mail import EmailMessage
import random

from members.forms import MemberLoginForm, MemberSignupForm1, MemberSignupForm2,\
    CaptchaVerificationForm, OTPGenerationForm, OTPVerificationForm,\
    SecurityQuestionForm, SecurityQuestionAnswerForm, ResetPasswordForm
from members.models import Member, MemberAnswers, SecurityQuestions
from django.contrib.auth.models import User
from _mysql_exceptions import IntegrityError
from django_twilio.decorators import twilio_view
from twilio.rest import TwilioRestClient 
from passwordreset.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

##################################################################################################################
def add_csrf(request, ** kwargs):
    d = dict(user=request.user, ** kwargs)
    d.update(csrf(request))
    return d

##################################################################################################################
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('members.views.login_view'))

##################################################################################################################
def login_view(request):
    loginform = MemberLoginForm()
    
    mId = -1
    mFn = 'Guest'
    try:
        mId = request.session['member_id']
        mFn = request.session['member_fn']
        
    except:
        mId = -1
        mFn = 'Guest'

    message = None        
    try:
        message = request.session['message']
        del request.session['message']
        request.session.modified = True
        
    except:
        message = None
    
    if request.method == 'POST':
        keypress = request.POST['keypress']
        
        if keypress == 'sign(me)up':
            return HttpResponseRedirect(reverse('members.views.signup_view'))
        
        elif keypress == 'log(me)in':
            loginform = MemberLoginForm(request.POST)
            if loginform.is_valid():
                username = loginform.cleaned_data['username']
                password = loginform.cleaned_data['password']
                
                user = authenticate(username = username, password = password)
            
                if user is None:
                    loginform._errors["username"] = loginform.error_class(["Oops!!! Could not log(you)in. Please check your login credentials"])
            
                else:
                    if user.is_active:
                        login(request, user)
                        
#                         member = Member.objects.get(user_id=user.id)
                        print("Member %s mId#%d logged in." % (user.username, user.id))
                        
                        request.session['member_id'] = user.id
                        request.session['member_fn'] = user.first_name

                        return HttpResponseRedirect(reverse('members.views.blank_view'))

                    else:
                        loginform._errors["username"] = loginform.error_class(["Oops!!! Could not log(you)in. Please check your login credentials"])
#                         raise loginform.ValidationError("Oops! Could not log(you)in. Your account has been disabled.")
    
        elif keypress == 'forgot(my)username':
            request.session['request_type'] = 'FORGOT_USERNAME'
            print("Forgot username")
            
        elif keypress == 'forgot(my)password':
            request.session['request_type'] = 'FORGOT_PASSWORD'
            return HttpResponseRedirect(reverse('members.views.captcha_view'))
    
    dictionary = add_csrf(request, form=loginform, mId=mId, mFn=mFn, message=message, disableLogin=True)
    return render_to_response('login.html', dictionary)

##################################################################################################################
def blank_view(request):
    dictionary = add_csrf(request, mFn=request.session['member_fn'], disableLogin=True)
    return render_to_response('blank.html', dictionary)

##################################################################################################################
def signup_view(request):
    signupform1 = MemberSignupForm1()
    signupform2 = MemberSignupForm2()
    signupform3 = SecurityQuestionAnswerForm()
    
    mId = -1
    member = None
    try:
        mId = request.session['member_id']
        member = request.session['member']
    except:
        mId = -1
        member = None
    
    if request.method == 'POST':
        keypress = request.POST['keypress']
        
        if keypress == 'sign(me)up':
            isValidMemberSignupForm = False
            signupform1 = MemberSignupForm1(request.POST)
            signupform2 = MemberSignupForm2(request.POST)
            signupform3 = SecurityQuestionAnswerForm(request.POST)
            isValidMemberSignupForm = signupform1.is_valid() and signupform2.is_valid() and signupform3.is_valid()
            
            if isValidMemberSignupForm:
                username = signupform2.cleaned_data["username"]
                password = signupform2.cleaned_data["password"]
                email = signupform2.cleaned_data["email"]
                que1 = signupform3.cleaned_data["que1"]
                ans1 = signupform3.cleaned_data["ans1"]
                que2 = signupform3.cleaned_data["que2"]
                ans2 = signupform3.cleaned_data["ans2"]
                que3 = signupform3.cleaned_data["que3"]
                ans3 = signupform3.cleaned_data["ans3"]
                
                try:
                    print("Checking availability of entered username.")
                    newUser = User.objects.create_user(username, email, password)
                    newUser.first_name = signupform2.cleaned_data["first_name"]
                    newUser.last_name = signupform2.cleaned_data["last_name"]
                    #g = Group.objects.get(name=MEMBERS) 
                    #g.user_set.add(newUser)
                    newUser.save()
                    
                    if newUser.pk:
                        print("Signing up new user.")
                        phone = signupform1.cleaned_data["phone_no"]
                        address = signupform1.cleaned_data["address"]
                        dob = signupform1.cleaned_data["dob"]
                    
                        newMember = Member(user_id = newUser.id, phone_no = phone, address = address, dob = dob)
                        newMember.save()
                            
                        print("Created new member: %s_%s: mId#%d" % (newMember.user.first_name, newMember.user.last_name, newMember.user.id))

                        newMemberA1 = MemberAnswers(member=newMember, question=que1, answer=ans1)
                        newMemberA2 = MemberAnswers(member=newMember, question=que2, answer=ans2)
                        newMemberA3 = MemberAnswers(member=newMember, question=que3, answer=ans3)
                        newMemberA1.save()
                        newMemberA2.save()
                        newMemberA3.save()
                        
                        print("Recorded Security Question-Answers for Member :%s_%s" % (newMember.user.first_name, newMember.user.last_name))

                        request.session.flush()
#                         dictionary = add_csrf(request, form=MemberLoginForm())
                        return HttpResponseRedirect(reverse('members.views.login_view'))
                 
                    #else:
                        #raise forms.ValidationError('The username of your choice is unavailable. Please choose a different one.')
                
                except IntegrityError,e:
                    #raise signupform2.ValidationError('The username of your choice is unavailable. Please choose a different one.')
                    signupform2._errors["username"] = signupform2.error_class(["Oops!!! Cannot sign(you)up with this username. Please select a different one"])
                
#                 except Exception,e :
#                     signupform2._errors["username"] = signupform2.error_class(["Oops!!! Failed to sign(you)up. Please try again later"])
#                     print "Caught:", e
        
    request.session.flush()
    request.method = 'POST'
    dictionary = add_csrf(request, form1=signupform1, form2=signupform2, form3=signupform3, mId=mId, member=member, disableSignup=True)
    return render_to_response('registration.html', dictionary)

##################################################################################################################
def captcha_view(request):
    captchaform = CaptchaVerificationForm()
    
    requestType = None
    try:
        requestType = request.session['request_type']
    except:
        requestType = None
    
    request.session['request_source'] = 'UNKNOWN'
    if request.method == 'POST':
        print("Serving Captcha for %s request." % (requestType))
        keypress = request.POST['keypress']
        
        if keypress == 'validate':
            captchaform = CaptchaVerificationForm(request.POST)
            if captchaform.is_valid():
                print("Verified human.")
                request.session['request_source'] = 'HUMAN'
                return HttpResponseRedirect(reverse('members.views.generate_otp_view'))
                
            else:
                captchaform._errors["captcha"] = captchaform.error_class(["Oops!!! Could not validate captcha. Try your luck with a new one."])
    
    dictionary = add_csrf(request, form=captchaform, rTy=requestType, disableLogin=True)
    return render_to_response('forgot_password_step_1.htm', dictionary)

##################################################################################################################
def is_human(request):
    requestSource = 'UNKNOWN'
    try:
        requestSource = request.session['request_source']
        if requestSource == 'HUMAN':
            return True
    except:
        requestSource = 'UNKNOWN'
        
    return False

# @twilio_view
# def send_sms_view(request):
#     member = None
#     try:
#         member = request.session['member']
#     except:
#         member = None
#     
#     client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) 
#     
#     message = client.messages.create(
#                            to="17323972286", 
#                            from_="+16122948210", 
#                            body="Your OTP for verification is 231.",  
#     )
#     
#     msg = 'Hey %s, how are you today?' % (member)
#     r = Response()
#     r.message(msg)
    

##################################################################################################################
@twilio_view
def generate_otp_view(request):
    if not is_human(request):
        request.session['message'] = "Na Na Na!!! You cannot just skip over our verification steps."
        return HttpResponseRedirect(reverse('members.views.login_view'))
    
    otpForm = OTPGenerationForm
    
    requestType = None
    try:
        requestType = request.session['request_type']
    except:
        requestType = None
    
    if request.method == 'POST':
        keypress = request.POST['keypress']
        
        if keypress == 'Send OTP':
            otpForm = OTPGenerationForm(request.POST)
            if otpForm.is_valid():
                email = otpForm.cleaned_data["email"]
#                 emailWithQuotes = "'%s'" % (email)
                phone = otpForm.cleaned_data["phone"]
                
                member = None
                members = Member.objects.none()
                if email is not None and len(email) > 4:
                    members = Member.objects.filter(user__email=email)
                    
                elif phone is not None and len(phone) > 0:
                    members = Member.objects.filter(phone_no=phone)
                
                if members.count() == 0:
                    print("No registered user having entered email/phone.")
                    otpForm._errors["email"] = otpForm.error_class(["Oops!!! No registration matches entered email/phone."])
                    
                elif members.count() != 1:
                    print("Two users with same email/phone.")
                    request.session['message'] = "Oops!!! Could not find a unique email/phone. Please contact site admin."
                    return HttpResponseRedirect(reverse('members.views.login_view'))
                    
                else:
                    member = members[0]
                    
                if member is not None:
                    request.session['member_id'] = member.pk
                    request.session['member_fn'] = member.user.first_name
#                     request.session['member'] = member
                    otp = '{0:05}'.format(random.randint(1, 100000))
                    request.session['otp'] = otp
                    otpmsg = "Your OTP for verification is " + otp + "."
                    
                    if email is not None and len(email) > 4:
                        otpemail = EmailMessage(
                            subject = 'OTP for verification', 
                            body    = otpmsg, 
                            to      = [email],
                        )
                        otpemail.send()
                        print 'Sent mail ' + otpmsg
                        
                    if phone is not None and len(phone) > 0:
                        client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) 
                        client.messages.create(
                            to    = "+17323972286", 
                            from_ = "+16122948210", 
                            body  = otpmsg,  
                        )
                        print 'Sent SMS ' + otpmsg

                    return HttpResponseRedirect(reverse('members.views.verify_otp_view'))
                else:
                    print("Unable to verify email/phone ownership.")
                
            else:
                otpForm._errors["email"] = otpForm.error_class(["Oops!!! Could not verify your email/phone ownership."])
    
    mId = -1
    mFn = None
    try:
        mId = request.session['member_id']
        mFn = request.session['member_fn']
    except:
        mId = -1
        mFn = None
    
    dictionary = add_csrf(request, form=otpForm, rTy=requestType, mId=mId, mFn=mFn, disableLogin=True)
    return render_to_response('forgot_password_step_2_1.htm', dictionary)

##################################################################################################################
def verify_otp_view(request):
    if not is_human(request):
        request.session['message'] = "Na Na Na!!! You cannot just skip over our verification steps."
        return HttpResponseRedirect(reverse('members.views.login_view'))
    
    otpForm = OTPVerificationForm
    MAX_CHANCES_FOR_VERIFICATION = 3
    
    mId = -1
    storedOtp = -1
    requestType = None
    try:
        mId = request.session['member_id']
        requestType = request.session['request_type']
        storedOtp = request.session['otp']
    except:
        mId = -1
        storedOtp = -1
        requestType = None
    
    if mId != -1 and request.method == 'POST':
        keypress = request.POST['keypress']
        
        if keypress == 'Verify OTP':
            otpForm = OTPVerificationForm(request.POST)
            
            if otpForm.is_valid():
                otp = otpForm.cleaned_data["otp"]
                
                if otp == storedOtp:
                    print("Verified email/phone ownership.")
                    return HttpResponseRedirect(reverse('members.views.furnish_securityQs_view'))
                else:
                    print("Unable to verify email/phone ownership.")
                    chances = MAX_CHANCES_FOR_VERIFICATION
                    try:
                        chances = request.session['chances']
                    except:
                        chances = MAX_CHANCES_FOR_VERIFICATION
                    chances -= 1
                    request.session['chances'] = chances
        
                    if chances > 0:
                        otpForm._errors["otp"] = otpForm.error_class(["Oops!!! Wrong OTP. You have " + str(chances) + " more chance(s) left."])
                
            else:
                otpForm._errors["otp"] = otpForm.error_class(["Oops!!! Could not process you request. Please try later."])
    
    mId = -1
    mFn = None
    try:
        mId = request.session['member_id']
        mFn = request.session['member_fn']
    except:
        mId = -1
        mFn = None
        
    dictionary = add_csrf(request, form=otpForm, rTy=requestType, mId=mId, mFn=mFn, disableLogin=True)
    return render_to_response('forgot_password_step_2_2.htm', dictionary)

##################################################################################################################
def furnish_securityQs_view(request):
    if not is_human(request):
        request.session['message'] = "Na Na Na!!! You cannot just skip over our verification steps."
        return HttpResponseRedirect(reverse('members.views.login_view'))
    
    form = SecurityQuestionForm
    MAX_CHANCES_PER_QUESTION = 3
    
    mId = -1
    mFn = None
#     member = None
    requestType = None
    try:
        mId = request.session['member_id']
        mFn = request.session['member_fn']
#         member = request.session['member']
        requestType = request.session['request_type']
        
    except:
        mId = -1
        mFn = None
#         member = None
        requestType = None
        
    questionNumber = -1
    try:
        questionNumber = request.session['member_q']
    except:
        questionNumber = -1
        
    nextQuestion = True
    if mId > -1 and request.method == 'GET':
        memberAs = MemberAnswers.objects.filter(member_id=mId)
        qIds = memberAs.values_list('question', flat=True)
        memberQs = SecurityQuestions.objects.filter(pk__in=qIds)
        plaintextMemberAs = []
        plaintextMemberQs = []
        for memberA in memberAs:
            for memberQ in memberQs:
                if memberA.question == memberQ:
                    plaintextMemberAs.append(memberA.answer)
                    plaintextMemberQs.append(memberQ.question)
        
        request.session['member_As'] = plaintextMemberAs
        request.session['member_Qs'] = plaintextMemberQs
        questionNumber = -1                                 # reset questionNumber
        request.session['member_q'] = questionNumber
        
    # from this point on memberAs and memberQs are list of plaintext member-answers and member-questions respectively
    memberAs = []
    memberQs = []
    try:
        memberAs = request.session['member_As']
        memberQs = request.session['member_Qs']
    except:
        memberAs = []
        memberQs = []
    if mId > -1 and request.method == 'POST':
        keypress = request.POST['keypress']
        
        if keypress == 'submit':
            form = SecurityQuestionForm(request.POST)
            
            if form.is_valid():
                answer = form.cleaned_data["answer"]

                if memberAs[questionNumber] != answer:
                    nextQuestion = False
                else:
                    nextQuestion = True
                
            else:
                form._errors["answer"] = form.error_class(["Oops!!! Internal Error. Please contact Site Admin."])
    
    que = None
    if nextQuestion:
        questionNumber += 1
        request.session['member_q'] = questionNumber
        
        if questionNumber < len(memberQs):
            request.session['chances'] = MAX_CHANCES_PER_QUESTION
            que = memberQs[questionNumber]
        else:
            print "Passed Security Questionnaire."
            return HttpResponseRedirect(reverse('members.views.change_password_view'))
    else:
        que = memberQs[questionNumber]
        
        chances = MAX_CHANCES_PER_QUESTION
        try:
            chances = request.session['chances']
        except:
            chances = MAX_CHANCES_PER_QUESTION
        chances -= 1
        request.session['chances'] = chances
        
        if chances > 0:
            form._errors["answer"] = form.error_class(["Oops!!! Wrong answer. You have " + str(chances) + " more chance(s) left."])
        else:
            request.session['message'] = "Failed to authenticate your " + requestType + " request."
            return HttpResponseRedirect(reverse('members.views.login_view'))
        
    dictionary = add_csrf(request, form=form, rTy=requestType, mId=mId, mFn=mFn, que=que, disableLogin=True)
    return render_to_response('forgot_password_step_3.htm', dictionary)

##################################################################################################################
def change_password_view(request):
    if not is_human(request):
        request.session['message'] = "Na Na Na!!! You cannot just skip over our verification steps."
        return HttpResponseRedirect(reverse('members.views.login_view'))
        
    form = ResetPasswordForm
    
    mId = -1
    mFn = None
    requestType = None
    try:
        mId = request.session['member_id']
        mFn = request.session['member_fn']
        requestType = request.session['request_type']
        
    except:
        mId = -1
        mFn = None
        requestType = None
        
    if mId > -1 and request.method == 'POST':
        keypress = request.POST['keypress']
        
        if keypress == 'reset password':
            form = ResetPasswordForm(request.POST)
            
            if form.is_valid():
                password = form.cleaned_data["password"]

                member = Member.objects.get(user_id=mId)
                if member is not None:
                    member.user.set_password(password)
                    member.user.save()
                    print("Changed password of Member :%s_%s" % (member.user.first_name, member.user.last_name))
                    request.session['message'] = "Voila!!! Your password has been reset."
                    return HttpResponseRedirect(reverse('members.views.login_view'))
                    
                else:
                    form._errors["password"] = form.error_class(["Oops!!! Failed to reset you password. Please contact Site Admin."])
    
    dictionary = add_csrf(request, form=form, rTy=requestType, mId=mId, mFn=mFn, disableLogin=True)
    return render_to_response('reset_password.htm', dictionary)
    
##################################################################################################################