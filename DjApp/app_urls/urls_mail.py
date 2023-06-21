from django.urls import path
from DjApp.controllers import MailController

urlpatterns = [

    # MANAGMENT MAİL SENDER
    path('send-verification-code-after-login/', MailController.send_verification_code_after_login,
         name="send-verification-code-after-login"),
    
    path('get-verification/', MailController.verify_account,
         name="get-verification"),
    
    path('contact-us/', MailController.contact_us, name="contact-us"),

]
