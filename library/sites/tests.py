from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from sites.models import Book, Loan

# Create your tests here.

user = get_user_model().objects.first()  # Get an existing user
book = Book.objects.first()  # Get your test book

Loan.objects.create(
    user=user,
    book=book,
    due_date=timezone.now() + timezone.timedelta(days=14),
    status='borrowed'
)

# Verify
print(Loan.objects.filter(user=user).count())  # Should be 1
print(book.available_copies)  # Should decrease by 1