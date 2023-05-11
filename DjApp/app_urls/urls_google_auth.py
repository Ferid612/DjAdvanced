from django.urls import path
from DjApp.views import views_google_auth

urlpatterns = [
    path('google-logout/', views_google_auth.google_logout, 
         name="google_logout"),
   
    path('google-login-callback/', views_google_auth.google_login_callback,
         name="google_login_callback"),
]
