from django.contrib import admin
from django.urls import include, path
from DeltaConfApp.app_urls import urls_gallery,urls_card_box

urlpatterns = [
    path('gallery/', include(urls_gallery), name="gallery_urls"),
    path('card_box/', include(urls_card_box), name="urls_card_box"),
        
]