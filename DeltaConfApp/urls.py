from django.contrib import admin
from django.urls import include, path
from DeltaConfApp.app_urls import urls_gallery

urlpatterns = [
    path('gallery/', include(urls_gallery), name="Gallary urls"),    
]