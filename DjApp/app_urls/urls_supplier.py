from django.urls import path
from DjApp.managements import suppliers
from DjApp.views import views_supplier

urlpatterns = [
    
    path('get_all_suppliers/',views_supplier.get_all_suppliers , name="Get alll supplier"),
    
    path('registration_of_supplier/',suppliers.registration_of_supplier , name="Create new supplier"),
    path('update_supplier/',suppliers.update_supplier_data , name="Update supplier data"),
    path('delete_supplier/',suppliers.delete_supplier , name="Delete supplier data"),
    
    path('add_supplier_address/',suppliers.add_supplier_address , name="Add supplier address data"),
    path('update_supplier_address/',suppliers.update_supplier_address , name="Update supplier adress data"),

]