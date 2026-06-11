from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Book(models.Model):
    isbn = models.CharField('ISBN', max_length=20, unique=True)
    title = models.CharField('書名', max_length=200)
    quantity = models.PositiveIntegerField('總量', default=1)
    category = models.CharField('分類', max_length=100, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class BorrowRecord(models.Model):
    class Action(models.TextChoices):
        BORROW = 'borrow', '借閱'
        RESERVE = 'reserve', '預約'

    class Status(models.TextChoices):
        ACTIVE = 'active', '進行中'
        RETURNED = 'returned', '已歸還'
        CANCELLED = 'cancelled', '已取消'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='使用者')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='書籍', related_name='borrow_records')
    action = models.CharField('操作類型', max_length=10, choices=Action.choices)
    status = models.CharField('狀態', max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField('建立時間', auto_now_add=True)
    due_date = models.DateTimeField('預期歸還日期', null=True, blank=True)
    returned_at = models.DateTimeField('完成時間', null=True, blank=True)
    is_overdue_notified = models.BooleanField('已通知逾期', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '借閱/預約紀錄'
        verbose_name_plural = '借閱/預約紀錄'

    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.book.title}"

    def save(self, *args, **kwargs):
        # 新建借閱記錄時，自動設定預期歸還日期為 7 天後
        if self.action == self.Action.BORROW and not self.due_date and not self.pk:
            self.due_date = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """檢查是否逾期"""
        if self.status == self.Status.ACTIVE and self.due_date:
            return timezone.now() > self.due_date
        return False
