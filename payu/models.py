import uuid
import json
import requests
from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.html import escape, format_html, mark_safe
from django.utils.http import urlencode
from django.contrib.humanize.templatetags.humanize import intcomma

from jsonfield import JSONField
from ipware.ip import get_real_ip, get_ip

from . import settings as payu_settings


ENDPOINT_URL = 'https://secure.payu.com/api/v2_1/orders'
OAUTH_URL = 'https://secure.payu.com/pl/standard/user/oauth/authorize'

TEST_POS_ID = 145227
TEST_MD5_KEY = '12f071174cb7eb79d4aac5bc2f07563f'
TEST_SECOND_MD5_KEY = '13a980d4f851f3d9a1cfc792fb1f5e50'

STATUS_CHOICES = (
    ('NEW', _('New')),
    ('PENDING', _('Pending')),
    ('WAITING_FOR_CONFIRMATION', _('Waiting for confirmation')),
    ('COMPLETED', _('Completed')),
    ('CANCELED', _('Canceled')),
    ('REJECTED', _('Rejected')),
)


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payu_order_id = models.CharField(
        _('PayU order ID'), max_length=255, null=True, blank=True
    )
    pos_id = models.CharField(_('PayU POS ID'), max_length=255)
    customer_ip = models.CharField(_('customer IP'), max_length=255)
    created = models.DateTimeField(
        _('creation date'), auto_now_add=True, editable=True
    )
    status = models.CharField(
        _('status'), max_length=255, choices=STATUS_CHOICES, default='NEW'
    )
    total = models.PositiveIntegerField(_('total'))
    description = models.TextField(_('description'), null=True, blank=True)
    products = JSONField(_('products'), default='', blank=True)
    notes = models.TextField(_('notes'), null=True, blank=True)

    class Meta:
        app_label = 'payu'
        ordering = ('-created',)
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        return str(self.id)

    @classmethod
    def get_oauth_token(cls):
        oauth_request_data = {
            'grant_type': 'client_credentials',
            'client_id': payu_settings.PAYU_POS_ID,
            'client_secret': payu_settings.PAYU_MD5_KEY
        }
        try:
            oauth_request = requests.post(OAUTH_URL, data=oauth_request_data)
            response = oauth_request.json()
            return response['access_token']
        except:
            return False

    @classmethod
    def create(cls, request, description, products, buyer,
               validity_time=payu_settings.PAYU_VALIDITY_TIME, notes=None):
        try:
            processed_products = [{
                'name': p['name'],
                'unitPrice': int(p['unitPrice']*100),
                'quantity': p['quantity']
            } for p in products]
        except (KeyError, ValueError):
            raise ValueError('Invalid list of products.')

        total = 0
        for p in processed_products:
            total += p['unitPrice'] * p['quantity']

        customer_ip = get_real_ip(request) or get_ip(request)

        payment = cls(
            pos_id=payu_settings.PAYU_POS_ID,
            customer_ip=customer_ip,
            total=total,
            description=description,
            products=json.dumps(processed_products),
            notes=notes
        )
        # not saved yet!

        if total:
            payment_request_data = {
                'extOrderId': str(payment.id),
                'customerIp': customer_ip,
                'merchantPosId': payu_settings.PAYU_POS_ID,
                'description': description,
                'currencyCode': 'PLN',
                'totalAmount': total,
                'products': processed_products,
                'buyer': buyer,
                'settings': {'invoiceDisabled': True},
                'notifyUrl': request.build_absolute_uri(
                    reverse('payu:api:notify')
                ),
                'continueUrl': request.build_absolute_uri(
                    payu_settings.PAYU_CONTINUE_PATH
                ),
                'validityTime': validity_time
            }
            payment_request_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(cls.get_oauth_token())
            }
            try:
                payment_request = requests.post(
                    ENDPOINT_URL,
                    json=payment_request_data,
                    headers=payment_request_headers,
                    allow_redirects=False
                )
                response = payment_request.json()
                payu_order_id = escape(response['orderId'])
                redirect_url = response['redirectUri']

                payment.payu_order_id = payu_order_id
                payment.save()

                return {
                    'object': payment,
                    'redirect_url': redirect_url
                }
            except:
                return False

        else:  # total == 0
            payment.status = 'COMPLETED'
            payment.save()
            return {
                'object': payment,
                'redirect_url': (payu_settings.PAYU_CONTINUE_PATH + '?' +
                                 urlencode({'no_payment': 1}))
            }

    def get_total_display(self):
        return '{} PLN'.format(intcomma(round(Decimal(self.total / 100), 2)))
    get_total_display.short_description = _('Total')

    def get_products_table(self):
        products = self.products
        try:
            if not products:
                return ''
            output = format_html(
                '''
                    <table>
                        <tr>
                            <td><strong>{}</strong></td>
                            <td><strong>{}</strong></td>
                            <td><strong>{}</strong></td>
                            <td><strong>{}</strong></td>
                        </tr>
                ''',
                _('Product'), _('Unit price'), _('Quantity'), _('Sum')
            )
            for p in products:
                unit_price = intcomma(round(Decimal(p['unitPrice'] / 100), 2))
                product_sum = intcomma(
                    round(Decimal(p['unitPrice'] / 100), 2) * p['quantity']
                )
                output += format_html(
                    '''
                        <tr>
                            <td>{}</td>
                            <td>{} PLN</td>
                            <td>{}</td>
                            <td>{} PLN</td>
                        </tr>
                    ''',
                    p['name'], unit_price, p['quantity'], product_sum
                )
            output += '</table>'
            return mark_safe(output)
        except (KeyError, ValueError):
            return _('Invalid data.')
    get_products_table.short_description = _('Products')

    def is_successful(self):
        return self.status == 'COMPLETED'

    def is_not_successful(self):
        return self.status in ('CANCELED', 'REJECTED')
