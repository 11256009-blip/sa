from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from datetime import timedelta
from .models import Book, BorrowRecord


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'category')
    search_fields = ('isbn', 'title', 'category')
    list_filter = ('category',)


class OverdueListFilter(admin.SimpleListFilter):
    """自訂篩選：顯示到期與逾期狀態"""
    title = '到期狀態'
    parameter_name = 'due_status'

    def lookups(self, request, model_admin):
        return (
            ('overdue', '已逾期'),
            ('due_soon', '即將到期'),
            ('active', '進行中'),
            ('returned', '已歸還'),
            ('cancelled', '已取消'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        soon = now + timedelta(days=BorrowRecord.WARNING_DAYS)
        if self.value() == 'overdue':
            return queryset.filter(
                status=BorrowRecord.Status.ACTIVE,
                action=BorrowRecord.Action.BORROW,
                due_date__lt=now
            )
        elif self.value() == 'due_soon':
            return queryset.filter(
                status=BorrowRecord.Status.ACTIVE,
                action=BorrowRecord.Action.BORROW,
                due_date__gte=now,
                due_date__lte=soon
            )
        elif self.value() == 'active':
            return queryset.filter(status=BorrowRecord.Status.ACTIVE)
        elif self.value() == 'returned':
            return queryset.filter(status=BorrowRecord.Status.RETURNED)
        elif self.value() == 'cancelled':
            return queryset.filter(status=BorrowRecord.Status.CANCELLED)
        return queryset


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'action', 'created_at', 'due_date', 'status_display', 'due_status_badge', 'notification_status')
    list_filter = (OverdueListFilter, 'action', 'status', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'book__title', 'book__isbn')
    readonly_fields = ('created_at', 'returned_at', 'due_status_badge')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('基本資訊', {
            'fields': ('user', 'book', 'action', 'status')
        }),
        ('借閱期限', {
            'fields': ('created_at', 'due_date', 'returned_at', 'due_status_badge', 'is_overdue_notified')
        }),
    )

    def status_display(self, obj):
        """顯示狀態"""
        return obj.get_status_display()
    status_display.short_description = '狀態'

    def due_status_badge(self, obj):
        """顯示到期預警"""
        if obj.action != BorrowRecord.Action.BORROW:
            return format_html('<span style="color: #6b7280;">預約無到期日</span>')
        if obj.status == BorrowRecord.Status.RETURNED:
            return format_html('<span style="color: #15803d;">已歸還</span>')
        if obj.status == BorrowRecord.Status.CANCELLED:
            return format_html('<span style="color: #6b7280;">已取消</span>')
        if not obj.due_date:
            return format_html('<span style="color: #b45309; font-weight: 600;">未設定到期日</span>')
        if obj.warning_level == 'overdue':
            return format_html(
                '<span style="color: #b91c1c; font-weight: 700;">逾期 {} 天</span>',
                obj.days_overdue
            )
        if obj.warning_level == 'due_soon':
            return format_html(
                '<span style="color: #c2410c; font-weight: 600;">{} 天後到期</span>',
                obj.days_until_due
            )
        if obj.warning_level == 'normal':
            return format_html(
                '<span style="color: #2563eb;">{} 天後到期</span>',
                obj.days_until_due
            )
        return '-'
    due_status_badge.short_description = '到期預警'

    def notification_status(self, obj):
        """顯示是否已標記逾期通知"""
        if obj.warning_level != 'overdue':
            return '-'
        if obj.is_overdue_notified:
            return format_html('<span style="color: #15803d;">已通知</span>')
        return format_html('<span style="color: #b91c1c; font-weight: 600;">待通知</span>')
    notification_status.short_description = '通知狀態'

    def get_queryset(self, request):
        """優化查詢"""
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'book')

