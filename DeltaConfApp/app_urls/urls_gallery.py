from django.urls import  path
from DeltaConfApp.controllers import GalleryController, NewArrivalController
from .. import views


urlpatterns = [
        
    # VIEWS GALLLERY 
    path('all/', views.get_galleries, name="galleries"),    
    path('create/', GalleryController.create_image_gallery, name="create-image-gallery"),    
    
    path('slide-photos/add/', GalleryController.add_slide_photo, name="add-slide-photo"),    
    path('slide-photos/add-many/', GalleryController.add_slide_photos, name="add-slide-photos"),    
    path('slide-photos/', views.get_slide_photos, name="slide-photos"),
    
    
    path('new-arrival/add/', NewArrivalController.add_new_arrival, name="add-new-arrival"),    
    path('new-arrival/add-many/', NewArrivalController.add_new_arrivals, name="add-new-arrivals"),    
    path('new-arrival/update/<int:new_arrival_id>/', NewArrivalController.update_new_arrival, name="update-new-arrival"),    
    path('new-arrival/delete/<int:new_arrival_id>/', NewArrivalController.delete_new_arrival, name="delete-new-arrival"),    
    path('new-arrivals/', views.get_new_arrivals, name="new-arrivals"),
    
]