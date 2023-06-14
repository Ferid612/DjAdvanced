from django.urls import path
from DjApp.managements_controller import SupplierController
from DjApp.views import views_supplier

urlpatterns = [

    path('suppliers/', views_supplier.get_all_suppliers, 
         name="suppliers"),

    path('create-registration/', SupplierController.registration_of_supplier,
         name="create-registration"),
   
    path('update-profil-image/', SupplierController.update_profile_image,
         name="update-supplier-profil-image"),

    path('update/', SupplierController.update_supplier_data,
         name="update-supplier"),
    
    path('delete/', SupplierController.delete_supplier,
         name="delete-supplier"),
          
    path('update-address/', SupplierController.update_supplier_address,
         name="update-supplier-address"),

]
