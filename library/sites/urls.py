from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('get-books/', views.get_api_data, name='get_books'),
    path('books/', views.get_api_data, name='books_list'),
    path('error/', views.get_api_data, name='error'),
]
