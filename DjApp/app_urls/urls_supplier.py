from django.urls import path
from DjApp.managements_controller import suppliers
from DjApp.views import views_supplier

urlpatterns = [
    
    path('get_all_suppliers/',views_supplier.get_all_suppliers , name="Get all supplier"),
    
    path('registration_of_supplier/',suppliers.registration_of_supplier , name="Create new supplier"),
    path('add_or_change_supplier_profile_image/', suppliers.add_or_change_supplier_profile_image, name="Add profil image to supplier."),    
    
    path('update_supplier/',suppliers.update_supplier_data , name="Update supplier data"),
    path('delete_supplier/',suppliers.delete_supplier , name="Delete supplier data"),
    
    path('add_supplier_address/',suppliers.add_supplier_address , name="Add supplier address data"),
    path('update_supplier_address/',suppliers.update_supplier_address , name="Update supplier adress data"),

]