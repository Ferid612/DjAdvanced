from django.urls import path
from DjApp.views import views_search

urlpatterns = [
    path('search/', views_search.search_product, name="search"),
   ]