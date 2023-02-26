from django.contrib import admin
from django.urls import include, path
from DjApp.app_urls import urls_supplier, urls_inventory, urls_person
from DjApp.app_urls import urls_discount, urls_roles_and_groups, urls_mail, urls_sms, urls_location


urlpatterns = [
    
    path('supplier/', include(urls_supplier), name="Suppliers urls"),
    path('inventory/', include(urls_inventory), name="Inventory urls"),
    path('person/', include(urls_person), name="Inventory urls"),
    path('discount/', include(urls_discount), name="Discount urls"),
    path('roles_groups/', include(urls_roles_and_groups), name="Roles and groups urls"),
    path('mail/', include(urls_mail), name="Mail urls"),
    path('sms/', include(urls_sms), name="sms urls"),
    path('location/', include(urls_location), name="location urls"),

    
]