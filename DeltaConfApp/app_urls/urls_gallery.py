from django.urls import  path
from DeltaConfApp.controllers import GalleryController
from .. import views


urlpatterns = [
        
    # VIEWS GALLLERY 
    path('slide-photos/add/', GalleryController.add_slide_photo, name="add-slide-photo"),    
    path('slide-photos/add-many/', GalleryController.add_slide_photos, name="add-slide-photos"),    
    path('crate/', GalleryController.create_image_gallery, name="create-image-gallery"),    
    path('slide-photos/', views.get_slide_photos, name="slide-photos"),    
    path('galleries/', views.get_galleries, name="galleries"),    
   
]