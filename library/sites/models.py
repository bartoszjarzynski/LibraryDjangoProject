from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.files.base import ContentFile
import requests
from io import BytesIO
from django.core.files.images import ImageFile
from datetime import datetime

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('employee', 'Employee'),
        ('administrator', 'Administrator'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reader',
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.username
    
class Book(models.Model):
    GENRE_CHOICES = (
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
        ('fantasy', 'Fantasy'),
    )

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        default='fiction',
    )
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    published_date = models.DateField(null=True, blank=True)
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0,
    )
    external_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

def save_books_from_api(api_response):
    for book_data in api_response.get('items', []):
        book_info = book_data.get('volumeInfo', {})
        
        # Ensure external_id is correctly fetched
        external_id = book_data.get('id')
        print(f"Saving book with external_id: {external_id}")  # Debugging line
        
        book, created = Book.objects.update_or_create(
            external_id=external_id,
            defaults={
                'title': book_info.get('title', ''),
                'author': ', '.join(book_info.get('authors', [])),
                'isbn': book_info.get('industryIdentifiers', [{}])[0].get('identifier', ''),
                'description': book_info.get('description', ''),
                'published_date': book_info.get('publishedDate', None),
                'available_copies': 1,
                'total_copies': 1,
                'genre': book_info.get('categories', [])[0] if book_info.get('categories') else 'fiction',
            }
        )

        # Handle cover image separately after book is created
        cover_url = book_info.get('imageLinks', {}).get('thumbnail', '')
        if cover_url and (not book.cover_image):
            try:
                response = requests.get(cover_url)
                if response.status_code == 200:
                    img_content = ContentFile(response.content)
                    file_name = f"{external_id}.jpg"
                    book.cover_image.save(file_name, img_content, save=True)
            except Exception as e:
                print(f"Failed to save cover image: {e}")

        print(f"Book with title '{book.title}' saved with external_id: {book.external_id}")

# def save_books_from_api(api_response):
#     for book_data in api_response.get('items', []):
#         book_info = book_data.get('volumeInfo', {})
        
#         external_id = book_data.get('id')
#         title = book_info.get('title', '')
#         authors = book_info.get('authors', [])
#         author = ', '.join(authors) if authors else ''
        
#         # Extract ISBN 13 if available
#         isbn = ''
#         for identifier in book_info.get('industryIdentifiers', []):
#             if identifier.get('type') == 'ISBN_13':
#                 isbn = identifier.get('identifier')
#                 break
#         if not isbn and book_info.get('industryIdentifiers'):
#             # fallback to first identifier if ISBN_13 not found
#             isbn = book_info['industryIdentifiers'][0].get('identifier', '')

#         description = book_info.get('description', '')

#         # Handle cover image download and saving
#         cover_url = book_info.get('imageLinks', {}).get('thumbnail', '')
        
#         # Parse published date safely
#         published_date_str = book_info.get('publishedDate', None)
#         published_date = None
#         if published_date_str:
#             try:
#                 # Google Books API sometimes returns year only or full date
#                 if len(published_date_str) == 4:
#                     published_date = datetime.strptime(published_date_str, '%Y').date()
#                 elif len(published_date_str) == 7:
#                     published_date = datetime.strptime(published_date_str, '%Y-%m').date()
#                 else:
#                     published_date = datetime.strptime(published_date_str, '%Y-%m-%d').date()
#             except Exception:
#                 published_date = None

#         categories = book_info.get('categories', [])
#         genre = categories[0].lower() if categories else 'fiction'
#         if genre not in dict(Book.GENRE_CHOICES):
#             genre = 'fiction'

#         book, created = Book.objects.update_or_create(
#             external_id=external_id,
#             defaults={
#                 'title': title,
#                 'author': author,
#                 'isbn': isbn,
#                 'description': description,
#                 'published_date': published_date,
#                 'available_copies': 1,
#                 'total_copies': 1,
#                 'genre': genre,
#             }
#         )

#         # Handle cover image separately after book is created
#         if cover_url and (not book.cover_image):
#             try:
#                 response = requests.get(cover_url)
#                 if response.status_code == 200:
#                     img_content = ContentFile(response.content)
#                     file_name = f"{external_id}.jpg"
#                     book.cover_image.save(file_name, img_content, save=True)
#             except Exception:
#                 pass

#         print(f"Book with title '{book.title}' saved with external_id: {book.external_id}")
    
class Loan(models.Model):
    STATUS_CHOICES = (
        ('reserved', 'Reserved'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    loan_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='borrowed',
    )

    def update_status(self):
        if self.status != 'returned':
            if timezone.now().date() > self.due_date:
                self.status = 'overdue'
            else:
                self.status = 'borrowed'
            self.save()

    def save(self, *args, **kwargs):
        # Handle book borrowing logic
        if self._state.adding:
            if self.book.available_copies <= 0:
                raise ValueError("No available copies to borrow")
            # Decrease available copies of the book
            self.book.available_copies -= 1
            self.book.save()

        elif self.status == 'returned' and not self.return_date:
            self.book.available_copies += 1
            self.book.save()
            self.return_date = timezone.now().date()

        super().save(*args, **kwargs)
        self.update_status()

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"