from django.shortcuts import render, redirect
from django.conf import settings
import requests
import random
from django.contrib.auth import login, get_user_model
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Book, Loan, Review
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

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

    return render(
        request,
        "home.html",
        {
            "user": user,
            "random_books": random_books,
            "last_viewed_books": last_viewed_books,
        },
    )


def fetch_books(query, api_key, max_results=10):
    """Fetching data from Google Books API"""
    
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "key": api_key, "maxResults": max_results}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        return None

def get_random_books(api_key, count=5):
    random_terms = [
        "fiction",
        "mystery",
        "science",
        "history",
        "biography",
        "travel",
        "cooking",
        "art",
        "poetry",
        "drama",
    ]
    random_query = random.choice(random_terms)
    return fetch_books(random_query, api_key, max_results=count)


def books(request):
    query = request.GET.get("q", "books")
    api_key = settings.API_KEY
    books_data = fetch_books(query, api_key)

    if request.method == "POST" and request.user.is_authenticated:
        external_id = request.POST.get("book_id")  # Get the external_id from the form
        book = get_object_or_404(Book, external_id=external_id)  # Query by external_id

        if book.available_copies > 0:
            due_date = timezone.now().date() + timezone.timedelta(weeks=2)
            Loan.objects.create(
                user=request.user, book=book, due_date=due_date, status="borrowed"
            )
            book.available_copies -= 1
            book.save()
            messages.success(request, f"You've successfully borrowed {book.title}")
            return redirect("loans")
        else:
            messages.error(request, "No available copies of this book")

    return render(request, "books.html", {"books": books_data, "search_term": query})


def genres(request):
    api_key = settings.API_KEY
    selected_genre = request.GET.get("q")
    popular_genres = [
        "fiction",
        "mystery",
        "science fiction",
        "fantasy",
        "thriller",
        "romance",
        "history",
        "biography",
        "horror",
        "comedy",
    ]
    books_data = None
    search_term = None

    if selected_genre:
        books_data = fetch_books(f"subject:{selected_genre}", api_key, max_results=10)
        search_term = selected_genre
        context = {
            "popular_genres": popular_genres,
            "books": books_data,
            "search_term": search_term,
        }
    else:
        context = {"popular_genres": popular_genres}

    return render(request, "genres.html", context)


def about(request):
    return render(request, "about.html")


def error(request):
    return render(request, "error.html", {"error": "Something went wrong."})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegistrationForm()
    return render(request, "register.html", {"form": form})


class CustomLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password"].widget.attrs["placeholder"] = "Password"


def user_login(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                return render(
                    request,
                    "login.html",
                    {"form": form, "error": "Username or password incorrect."},
                )
        else:
            print(f"Form error: {form.errors}")
    else:
        form = CustomLoginForm(request)
    return render(request, "login.html", {"form": form})


# ------------------------------------------------------------------------------------------


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == "POST" and request.user.is_authenticated:
        # Check if book is available
        if book.available_copies > 0:
            due_date = timezone.now().date() + timezone.timedelta(weeks=2)
            # Create a new loan
            Loan.objects.create(
                user=request.user, book=book, due_date=due_date, status="borrowed"
            )
            # Update available copies of the book
            book.available_copies -= 1
            book.save()
            messages.success(request, f"You've successfully borrowed {book.title}")
            return redirect("loans")
        else:
            messages.error(request, "No available copies of this book")

    return render(
        request, "book_detail.html", {"book": book}
    )


@login_required
def loans(request):
    user_loans = (
        Loan.objects.filter(user=request.user)
        .select_related("book")
        .order_by("-loan_date")
    )
    return render(request, "loans.html", {"loans": user_loans})


@login_required
def return_book(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)
    if loan.status != "returned":
        loan.status = "returned"
        loan.return_date = timezone.now().date()
        loan.book.available_copies += 1
        loan.book.save()
        loan.save()
        messages.success(request, f"You have successfully returned {loan.book.title}")
    return redirect("loans")


def loan_book(request, book_id):
    # Pobranie książki
    book = get_object_or_404(Book, id=book_id)

    # Sprawdzenie, czy książka jest dostępna
    if book.available_copies <= 0:
        messages.error(request, "No available copies to borrow.")
        return redirect("books")

    # Sprawdzenie, czy użytkownik jest zalogowany
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to borrow a book.")
        return redirect("login")

    # Tworzenie nowego wypożyczenia
    due_date = timezone.now().date() + timezone.timedelta(
        weeks=2
    )  # Ustalenie terminu zwrotu na 2 tygodnie
    loan = Loan.objects.create(
        user=request.user,
        book=book,
        due_date=due_date,
        status="borrowed",
    )

    # Zmniejszenie dostępnych kopii książki
    book.available_copies -= 1
    book.save()

    messages.success(
        request,
        f"You've successfully borrowed {book.title}. Please return it by {due_date}.",
    )
    return redirect("loans")


@login_required
def rate_book(request, book_id):
    # Use external_id (which you just added) to find the book
    book = get_object_or_404(Book, external_id=book_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        if rating:
            # Create or update the review
            review, created = Review.objects.get_or_create(user=request.user, book=book)
            review.rating = int(rating)
            review.save()

            messages.success(request, "Your rating has been submitted!")
        else:
            messages.error(request, "Please select a rating.")

        return redirect('books')  # Redirect back to the books list page

    return HttpResponse("Invalid request", status=400)

@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, external_id=book_id)

    if request.method == 'POST':
        comment = request.POST.get('review_text')
        rating = request.POST.get('rating')

        if comment and rating:
            # Create or update the review for the user and book
            review, created = Review.objects.get_or_create(user=request.user, book=book)
            review.comment = comment
            review.rating = int(rating)
            review.save()

            messages.success(request, "Your review has been submitted!")
        else:
            messages.error(request, "Please provide both a rating and a comment.")

        return redirect('books')  # Redirect back to the books list page

    return HttpResponse("Invalid request", status=400)

