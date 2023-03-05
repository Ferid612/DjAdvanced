from django.contrib import admin
from django.urls import include, path
from DjApp.app_urls import urls_supplier, urls_inventory, urls_person, urls_discount, urls_comment_question_fag 
from DjApp.app_urls import urls_roles_and_groups, urls_mail, urls_sms, urls_location,urls_shopping, urls_apis


urlpatterns = [
    
    path('supplier/', include(urls_supplier), name="Suppliers urls"),
    path('inventory/', include(urls_inventory), name="Inventory urls"),
    path('person/', include(urls_person), name="Inventory urls"),
    path('discount/', include(urls_discount), name="Discount urls"),
    path('roles_groups/', include(urls_roles_and_groups), name="Roles and groups urls"),
    path('mail/', include(urls_mail), name="Mail urls"),
    path('sms/', include(urls_sms), name="SMS urls"),
    path('location/', include(urls_location), name="Location urls"),
    path('shopping/', include(urls_shopping), name="Shopping urls"),
    path('comments_question_fag/', include(urls_comment_question_fag), name="Comment type sections urls"),
    path('apis/', include(urls_apis), name="APİ's urls"),

    
    # path("", views_auth0_2.home, name="index"),
    # path("login", views_auth0_2.login, name="login"),
    # path("logout", views_auth0_2.logout, name="logout"),
    # path("callback", views_auth0_2.callback, name="callback"),
    
    
]