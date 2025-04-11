from django.shortcuts import render
from django.conf import settings
import requests

# Create your views here.

def home(request):
    return render(request, 'home.html')

def get_api_data(request):
    api_key = settings.API_KEY
    search_terms = "Harry Potter"
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={search_terms}&key={api_key}')

    if response.status_code == 200:
        data = response.json()
        books = data.get('items', [])
        return render(request, 'books_list.html', {'books': books})
    else:
        return render(request, 'error.html', {'error': 'Failed to retrieve data'})

# def get_api_data(request):
#     api_key = settings.API_KEY
#     search_terms = "Harry Potter"
#     response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={search_terms}&key={api_key}')
    
#     if response.status_code == 200:
#         data = response.json()
#         print(data)  # This will print the entire JSON response to the console
#         books = data.get('items', [])
#         return render(request, 'books_list.html', {'books': books})
#     else:
#         return render(request, 'error.html', {'error': 'Failed to retrieve data'})