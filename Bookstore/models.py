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
    DUE_DAYS = 7
    WARNING_DAYS = 2

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
        # 新建借閱記錄時，自動設定預期歸還日期
        if self.action == self.Action.BORROW and not self.due_date and not self.pk:
            self.due_date = timezone.now() + timedelta(days=self.DUE_DAYS)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """檢查是否逾期"""
        if self.status == self.Status.ACTIVE and self.due_date:
            return timezone.now() > self.due_date
        return False

    @property
    def days_overdue(self):
        """回傳逾期天數，未逾期則為 0。"""
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date.date()).days

    @property
    def days_until_due(self):
        """回傳距離到期的天數；已逾期或沒有到期日則回傳 None。"""
        if self.status != self.Status.ACTIVE or not self.due_date or self.is_overdue:
            return None
        return (self.due_date.date() - timezone.now().date()).days

    @property
    def is_due_soon(self):
        """檢查是否即將到期。"""
        days_left = self.days_until_due
        return days_left is not None and days_left <= self.WARNING_DAYS

    @property
    def warning_level(self):
        """提供後台和管理指令共用的預警等級。"""
        if self.action != self.Action.BORROW or self.status != self.Status.ACTIVE:
            return 'none'
        if self.is_overdue:
            return 'overdue'
        if self.is_due_soon:
            return 'due_soon'
        return 'normal'
