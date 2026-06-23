from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Bookstore', '0003_remove_book_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='quantity',
            field=models.PositiveIntegerField(default=1, verbose_name='總量'),
        ),
        migrations.CreateModel(
            name='BorrowRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('borrow', '借閱'), ('reserve', '預約')], max_length=10, verbose_name='操作類型')),
                ('status', models.CharField(choices=[('active', '進行中'), ('returned', '已歸還'), ('cancelled', '已取消')], default='active', max_length=10, verbose_name='狀態')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('returned_at', models.DateTimeField(blank=True, null=True, verbose_name='完成時間')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrow_records', to='Bookstore.Book', verbose_name='書籍')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='使用者')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': '借閱/預約紀錄',
                'verbose_name_plural': '借閱/預約紀錄',
            },
        ),
    ]
