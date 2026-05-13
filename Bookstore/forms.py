from django import forms

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'summary',
            'isbn',
            'publisher',
            'publication_date',
            'pages',
            'language',
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
        }
