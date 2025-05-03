from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.books, name='books'),
    path('genres/', views.genres, name='genres'),
    path('about/', views.about, name='about'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('error/', views.error, name='error'),
]