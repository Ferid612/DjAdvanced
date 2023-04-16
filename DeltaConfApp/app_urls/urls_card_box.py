from django.urls import path
from DeltaConfApp.controllers import CardBoxController
from .. import views

app_name = 'card-box'

urlpatterns = [
    path('create/', CardBoxController.create_card_box, name='create-card-box'),
    path('<int:pk>/update/', CardBoxController.update_card_box, name='update-card-box'),
    path('<int:pk>/delete/', CardBoxController.delete_card_box, name='delete-card-box'),
    path('<int:pk>/add-product-entry/', CardBoxController.add_product_entry_to_card_box, name='add-product-entry-to-card-box'),
    path('<int:pk>/delete-product-entry/', CardBoxController.delete_product_entry_from_card_box, name='delete-product-entry-from-card-box'),
    
    path('<int:pk>/get-card-box-entries/', views.get_card_box_entries, name='get-card-box-entries'),
]
