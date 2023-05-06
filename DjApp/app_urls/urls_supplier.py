from django.urls import path
from DjApp.managements_controller import SupplierController
from DjApp.views import views_supplier

urlpatterns = [

    path('suppliers/', views_supplier.get_all_suppliers, 
         name="suppliers"),

    path('registration-of-supplier/', SupplierController.registration_of_supplier,
         name="registration-of-supplier"),
    path('update-profil-image/', SupplierController.add_or_change_supplier_profile_image,
         name="update-supplier-profil-image"),

    path('update-supplier/', SupplierController.update_supplier_data,
         name="update-supplier"),
    path('delete-supplier/', SupplierController.delete_supplier,
         name="delete-supplier"),

    path('add-supplier-address/', SupplierController.add_supplier_address,
         name="add-supplier-address"),
    path('update-supplier-address/', SupplierController.update_supplier_address,
         name="update-supplier-address"),

]
