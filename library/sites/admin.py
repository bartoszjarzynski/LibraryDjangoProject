from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Book, Loan


class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "genre",
        "total_copies",
        "available_copies",
        "published_date",
    )
    search_fields = ("title", "author", "isbn")
    list_filter = ("genre", "published_date")


class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "loan_date", "return_date", "status")
    search_fields = ("book__title", "user__username")
    list_filter = ("status", "loan_date")


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Loan, LoanAdmin)
