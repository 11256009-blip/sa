from django.db import models

class Book(models.Model):
    isbn = models.CharField('ISBN', max_length=20, unique=True)
    title = models.CharField('書名', max_length=200)
    quantity = models.IntegerField('總量', default=1)
    category = models.CharField('分類', max_length=100, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"{self.title} ({self.isbn})"
