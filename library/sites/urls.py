from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.books, name='books'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('genres/', views.genres, name='genres'),
    path('about/', views.about, name='about'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('error/', views.error, name='error'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('loans/', views.loans, name='loans'),
    path('loans/return/<int:loan_id>/', views.return_book, name='return_book'),
    path('loans/<int:loan_id>/', views.loan_book, name='loan_book'),
    path('rate_book/<str:book_id>/', views.rate_book, name='rate_book'),
]