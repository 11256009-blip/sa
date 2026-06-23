from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Bookstore', '0002_remove_book_author_remove_book_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='quantity',
        ),
    ]
