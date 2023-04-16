from django.urls import  path
from DjApp.managements_controller import SMSController 

urlpatterns = [
        
    # MANAGMENT SMS SENDER
    path('send-verify-from-twilio/', SMSController.send_verification_code_with_twilio, name="send-verify-from-twilio"),    
    path('verify-twilio/', SMSController.verify_twilio, name="verify-twilio"), 
    
]