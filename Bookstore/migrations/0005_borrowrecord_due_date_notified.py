# Generated migration file

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bookstore', '0004_add_borrowrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowrecord',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='預期歸還日期'),
        ),
        migrations.AddField(
            model_name='borrowrecord',
            name='is_overdue_notified',
            field=models.BooleanField(default=False, verbose_name='已通知逾期'),
        ),
    ]
