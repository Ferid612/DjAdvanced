from django.urls import  path
from DeltaConfApp.controllers import GalleryController
from .. import views


urlpatterns = [
        
    # VIEWS GALLLERY 
    path('add-slide-photo/', GalleryController.add_slide_photo, name="add-slide-photos"),    
    path('add-slide-photos/', GalleryController.add_slide_photos, name="add-slide-photos"),    
    path('create-image-gallery/', GalleryController.create_image_gallery, name="create-image-gallery"),    
    path('get-slide-photos/', views.get_slide_photos, name="get-slide-photos"),    
    path('get-galleries/', views.get_galleries, name="get-galleries"),    
   
]