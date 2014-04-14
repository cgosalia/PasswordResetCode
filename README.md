passwordreset
=============

prototype password-reset project having recaptcha, twilio-sms and negative-security-questionnaire



To check all the tables that will be created ...
python manage.py sqlall

To create the tables ...
python manage.py syncdb

To prepopulate SecurityQuestions ...
python manage.py loaddata initial_data.json


In the created database tables please make phone_no and email columns unique explicitly.

SecurityQuestions must be reloaded into the database after every update to the initial_data.json. 
Doing this will destroy all the existing data in that table and will sync it with the updated initial_data.json.
