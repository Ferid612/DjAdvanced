from django.contrib import admin
from django.urls import include, path
from DjApp.app_urls import urls_fag_question_comment
from DjApp.app_urls import urls_supplier, urls_inventory, urls_person, urls_discount, urls_wishlist 
from DjApp.app_urls import urls_roles_and_groups, urls_mail, urls_sms, urls_location,urls_shopping, urls_apis, urls_google_auth


urlpatterns = [
    
    path('person/', include(urls_person),
         name="person-urls"),
    path('supplier/', include(urls_supplier),
         name="supplier-urls"),
    path('inventory/', include(urls_inventory),
         name="inventory-urls"), 
    path('wishlist/', include(urls_wishlist),
         name="wishlist-urls"),
    path('discount/', include(urls_discount),
         name="discount-urls"),
    path('roles_groups/', include(urls_roles_and_groups),
         name="roles-groups-urls"),
    path('mail/', include(urls_mail),
         name="mail-urls"),
    path('sms/', include(urls_sms),
         name="sms-urls"),
    path('location/', include(urls_location),
         name="location-urls"),
    path('shopping/', include(urls_shopping),
         name="shopping-urls"),
    path('comments_question_fag/', include(urls_fag_question_comment),
         name="fag-question-comment-urls"),
    path('apis/', include(urls_apis),
         name="apis-urls"),
    path('google_auth/', include(urls_google_auth),
         name="Google Authentication"),


    
    # path("", views_auth0_2.home,
    #    name="index"),
    # path("login", views_auth0_2.login,
    #    name="login"),
    # path("logout", views_auth0_2.logout,
    #    name="logout"),
    # path("callback", views_auth0_2.callback,
    #    name="callback"),
    
    
]