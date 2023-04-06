from django.urls import  path
from DeltaConfApp.controllers import gallery


urlpatterns = [
        
    # VIEWS GALLLERY 
    path('add_slide_photo/', gallery.add_slide_photo, name="add_slide_photos"),    
    path('add_slide_photos/', gallery.add_slide_photos, name="add_slide_photos"),    
    path('create_image_gallery/', gallery.create_image_gallery, name="create_image_gallery"),    
    path('get_slide_photos/', gallery.get_slide_photos, name="get_slide_photos"),    
    path('get_galleries/', gallery.get_galleries, name="get_galleries"),    
   
]