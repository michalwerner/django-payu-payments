from django.contrib import admin
from django.utils.translation import ugettext as _
from django.utils.html import format_html
from django.conf import settings

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def get_status(self, obj):
        if obj.status == 'COMPLETED':
            color = '#009200'
        elif obj.status in ('CANCELED', 'REJECTED'):
            color = '#e60000'
        else:
            color = None

        if color:
            return format_html(
                '<span style="color: {}">{}</span>',
                color,
                obj.get_status_display()
            )
        else:
            return obj.get_status_display()
    get_status.short_description = _('Status')

    list_display = ('id', 'payu_order_id', 'pos_id', 'created',
                    'get_status', 'get_total_display')
    list_filter = ('status',)
    readonly_fields = ('id', 'payu_order_id', 'pos_id', 'customer_ip',
                       'created', 'get_status', 'get_total_display',
                       'description', 'get_products_table')

    fieldsets = [
        (None, {
            'fields': (('id', 'payu_order_id'), ('pos_id', 'customer_ip'),
                       'created', 'description', 'get_status',
                       'get_products_table', 'get_total_display', 'notes')
        }),
    ]

    if 'grappelli' in settings.INSTALLED_APPS:
        change_list_template = 'admin/change_list_filter_sidebar.html'
        change_list_filter_template = 'admin/filter_listing.html'
