from django.shortcuts import render, redirect
from django.conf import settings
import requests, random
from django.contrib.auth import authenticate, login, get_user_model
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.forms import AuthenticationForm

# Pobierz model CustomUser
CustomUser = get_user_model()

# Create your views here.

def home(request):
    user = request.user
    api_key = settings.API_KEY
    random_books = get_random_books(api_key, count=5)
    last_viewed_books = []

    if request.user.is_authenticated:
        pass

    return render(request, 'home.html', {'user': user, 'random_books': random_books, 'last_viewed_books': last_viewed_books})

def fetch_books(query, api_key, max_results=10):
    """ Fetching data from Google Books API"""
    base_url = 'https://www.googleapis.com/books/v1/volumes'
    params = {'q': query, 'key': api_key, 'maxResults': max_results}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        return None
    
def get_random_books(api_key, count=5):
    random_terms = ["fiction", "mystery", "science", "history", "biography", "travel", "cooking", "art", "poetry", "drama"]
    random_query = random.choice(random_terms)
    return fetch_books(random_query, api_key, max_results=count)

def books(request):
    query = request.GET.get('q', 'books') # Default search term
    api_key = settings.API_KEY
    books_data = fetch_books(query, api_key)
    return render(request, 'books.html', {'books': books_data, 'search_term': query})

def authors(request):
    query = request.GET.get('q', 'authors')
    api_key = settings.API_KEY
    authors_data = fetch_books(f'inauthor:{query}', api_key)
    return render(request, 'authors.html', {'authors': authors_data, 'search_term': query})

def genres(request):
    query = request.GET.get('q', 'genres')
    api_key = settings.API_KEY
    genres_data = fetch_books(f'subject:{query}', api_key)
    return render(request, 'genres.html', {'genres': genres_data, 'search_term': query})

def about(request):
    return render(request, 'about.html')

def error(request):
    return render(request, 'error.html', {'error': 'Something went wrong.'})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'error.html', {'error': 'Something went wrong.'})
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


class CustomLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'

def user_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Username or password incorrect.'})
        else:
            print(f"Form error: {form.errors}")
    else:
        form = CustomLoginForm(request)
    return render(request, 'login.html', {'form': form})