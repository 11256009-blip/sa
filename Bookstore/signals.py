from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User
from .models import BorrowRecord


@receiver(post_save, sender=BorrowRecord)
def set_due_date_on_borrow(sender, instance, created, **kwargs):
    """
    創建新的借閱記錄時自動設定預期歸還日期
    """
    if created and instance.action == BorrowRecord.Action.BORROW and not instance.due_date:
        instance.due_date = timezone.now() + timezone.timedelta(days=7)
        instance.save()
