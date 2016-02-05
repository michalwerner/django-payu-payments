import json
from decimal import Decimal

from django.contrib import admin
from django.utils.translation import ugettext as _
from django.utils.html import format_html, mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma
from django.conf import settings

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    def get_status(self, obj):
        if obj.status == 'COMPLETED':
            color = '#009200'
        elif obj.status in ('CANCELED', 'REJECTED'):
            color = '#e60000'
        else:
            color = None

        if color:
            return format_html('<span style="color: {}">{}</span>', color, obj.get_status_display())
        else:
            return obj.get_status_display()
    get_status.short_description = _('Status')

    def get_products(self, obj):
        products = json.loads(obj.products)
        try:
            if not products:
                return ''
            output = format_html('<table><tr><td><strong>{}</strong></td><td><strong>{}</strong></td><td><strong>{}</strong></td></tr>', _('Product'), _('Unit price'), _('Quantity'))
            for p in products:
                unit_price = intcomma(round(Decimal(p['unitPrice'] / 100), 2))
                output += format_html('<tr><td>{}</td><td>{} PLN</td><td>{}</td></tr>', p['name'], unit_price, p['quantity'])
            output += '</table>'
            return mark_safe(output)
        except (KeyError, ValueError):
            return _('Invalid data.')
    get_products.short_description = _('Products')

    def get_total(self, obj):
        return '{} PLN'.format(intcomma(round(Decimal(obj.total / 100), 2)))
    get_total.short_description = _('Total')

    list_display = ('id', 'payu_order_id', 'pos_id', 'created',
                    'get_status', 'get_total')
    list_filter = ('status',)
    readonly_fields = ('id', 'payu_order_id', 'pos_id', 'customer_ip',
                       'created', 'get_status', 'get_total', 'description', 'get_products')

    fieldsets = [
        (None, {
            'fields': (('id', 'payu_order_id'), ('pos_id', 'customer_ip'),
                       'created', 'description', 'get_status', 'get_products',
                       'get_total', 'notes')
        }),
    ]

    if 'grappelli' in settings.INSTALLED_APPS:
        change_list_template = 'admin/change_list_filter_sidebar.html'
        change_list_filter_template = 'admin/filter_listing.html'
