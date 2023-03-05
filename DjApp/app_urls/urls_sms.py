from django.urls import  path
from DjApp.managements_controller import sms_sender 

urlpatterns = [
        
    # MANAGMENT SMS SENDER
    path('send_verify_from_twilio/', sms_sender.send_verification_code_with_twilio, name="Send verification sms to user."),    
    path('verify_twilio/', sms_sender.verify_twilio, name="Check user verification code with sms."), 
    
    
]