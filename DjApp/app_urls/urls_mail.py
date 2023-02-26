from django.urls import  path
from DjApp.managements import mail_sender 

urlpatterns = [
        
   # MANAGMENT MAİL SENDER
    path('send_verification_code_after_login/', mail_sender.send_verification_code_after_login, name="Send user verification code to email."),    
    path('get_verification/', mail_sender.verify_account, name="Check user verification code with email."),    
    path('contact_us/', mail_sender.contact_us, name="Send user data to us."),
       
]