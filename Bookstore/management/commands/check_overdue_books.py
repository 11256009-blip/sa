from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from Bookstore.models import BorrowRecord


class Command(BaseCommand):
    help = '檢查超期借閱記錄並標記通知'

    def handle(self, *args, **options):
        """檢查所有未歸還的借閱記錄是否超期"""
        now = timezone.now()
        
        # 查找所有進行中且已超期的借閱記錄
        overdue_records = BorrowRecord.objects.filter(
            status=BorrowRecord.Status.ACTIVE,
            due_date__lt=now,
            is_overdue_notified=False,
            action=BorrowRecord.Action.BORROW
        )

        if overdue_records.exists():
            # 獲取所有管理員
            admins = User.objects.filter(is_superuser=True)
            
            # 標記所有超期記錄
            for record in overdue_records:
                record.is_overdue_notified = True
                record.save()
                
                days_overdue = (now - record.due_date).days
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  逾期通知: {record.user.username} 未歸還《{record.book.title}》'
                        f'(預期: {record.due_date.strftime("%Y-%m-%d")}, 逾期 {days_overdue} 天)'
                    )
                )

            if admins.exists():
                admin_list = ', '.join([admin.get_full_name() or admin.username for admin in admins])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ 已標記 {overdue_records.count()} 筆超期記錄'
                        f'\n通知對象: {admin_list}'
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS('✓ 沒有新的超期記錄'))
