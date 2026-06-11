from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Book, BorrowRecord


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'category')
    search_fields = ('isbn', 'title', 'category')
    list_filter = ('category',)


class OverdueListFilter(admin.SimpleListFilter):
    """自訂篩選：顯示逾期記錄"""
    title = '狀態'
    parameter_name = 'overdue_status'

    def lookups(self, request, model_admin):
        return (
            ('overdue', '已逾期'),
            ('active', '進行中'),
            ('returned', '已歸還'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'overdue':
            return queryset.filter(
                status=BorrowRecord.Status.ACTIVE,
                due_date__lt=now
            )
        elif self.value() == 'active':
            return queryset.filter(status=BorrowRecord.Status.ACTIVE)
        elif self.value() == 'returned':
            return queryset.filter(status=BorrowRecord.Status.RETURNED)
        return queryset


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'action', 'created_at', 'due_date', 'status_display', 'overdue_warning')
    list_filter = (OverdueListFilter, 'action', 'status', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'book__title', 'book__isbn')
    readonly_fields = ('created_at', 'returned_at', 'due_date')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'book', 'action', 'status')
        }),
        ('借閱期限', {
            'fields': ('created_at', 'due_date', 'returned_at', 'is_overdue_notified')
        }),
    )

    def status_display(self, obj):
        """顯示狀態"""
        return obj.get_status_display()
    status_display.short_description = '狀態'

    def overdue_warning(self, obj):
        """顯示逾期警告"""
        if obj.status == BorrowRecord.Status.ACTIVE and obj.due_date:
            if timezone.now() > obj.due_date:
                days_overdue = (timezone.now() - obj.due_date).days
                return format_html(
                    '<span style="color: red; font-weight: bold;">⚠️ 逾期 {} 天</span>',
                    days_overdue
                )
            else:
                days_left = (obj.due_date - timezone.now()).days
                if days_left <= 2:
                    return format_html(
                        '<span style="color: orange;">⏰ {} 天後到期</span>',
                        days_left
                    )
        return '-'
    overdue_warning.short_description = '逾期提醒'

    def get_queryset(self, request):
        """優化查詢"""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'book')

