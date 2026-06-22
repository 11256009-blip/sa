from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from Bookstore.models import BorrowRecord
from datetime import timedelta


class Command(BaseCommand):
    help = '檢查逾期與即將到期的借閱記錄'

    def handle(self, *args, **options):
        """檢查所有未歸還的借閱記錄是否逾期或即將到期"""
        now = timezone.now()
        soon = now + timedelta(days=BorrowRecord.WARNING_DAYS)
        
        # 查找所有進行中且已逾期、尚未標記通知的借閱記錄
        overdue_records = BorrowRecord.objects.filter(
            status=BorrowRecord.Status.ACTIVE,
            due_date__lt=now,
            is_overdue_notified=False,
            action=BorrowRecord.Action.BORROW
        ).select_related('user', 'book')

        # 查找即將到期但尚未逾期的借閱記錄，僅輸出提醒，不標記逾期通知
        due_soon_records = BorrowRecord.objects.filter(
            status=BorrowRecord.Status.ACTIVE,
            due_date__gte=now,
            due_date__lte=soon,
            action=BorrowRecord.Action.BORROW
        ).select_related('user', 'book')

        overdue_records = list(overdue_records)
        due_soon_records = list(due_soon_records)

        if overdue_records:
            # 獲取所有管理員
            admins = User.objects.filter(is_superuser=True)
            
            # 標記所有超期記錄
            for record in overdue_records:
                record.is_overdue_notified = True
                record.save()
                
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  逾期通知: {record.user.username} 未歸還《{record.book.title}》'
                        f'(預期: {record.due_date.strftime("%Y-%m-%d")}, 逾期 {record.days_overdue} 天)'
                    )
                )

            if admins.exists():
                admin_list = ', '.join([admin.get_full_name() or admin.username for admin in admins])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ 已標記 {len(overdue_records)} 筆逾期記錄'
                        f'\n通知對象: {admin_list}'
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS('✓ 沒有新的逾期記錄'))

        if due_soon_records:
            for record in due_soon_records:
                self.stdout.write(
                    self.style.NOTICE(
                        f'即將到期: {record.user.username} 借閱《{record.book.title}》'
                        f'(預期: {record.due_date.strftime("%Y-%m-%d")}, {record.days_until_due} 天後到期)'
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS('✓ 沒有即將到期的借閱記錄'))
