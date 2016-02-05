import uuid
import json
import requests

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.core.exceptions import ImproperlyConfigured

from ipware.ip import get_real_ip, get_ip


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
    payu_order_id = models.CharField(_('PayU order ID'), max_length=255)
    pos_id = models.CharField(_('PayU POS ID'), max_length=255)
    customer_ip = models.CharField(_('customer IP'), max_length=255)
    created = models.DateTimeField(_('creation date'), auto_now_add=True, editable=True)
    status = models.CharField(_('status'), max_length=255, choices=STATUS_CHOICES, default='NEW')
    total = models.PositiveIntegerField(_('total'))
    description = models.TextField(_('description'), null=True, blank=True)
    products = JSONField(_('products'), default='', blank=True)
    notes = models.TextField(_('notes'), null=True, blank=True)

    class Meta:
        app_label = 'payu'
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        return str(self.id)

    @staticmethod
    def get_payu_params():
        try:
            payu_settings = settings.PAYU
            if payu_settings['test']:
                return {
                    'pos_id': TEST_POS_ID,
                    'md5_key': TEST_MD5_KEY,
                    'second_md5_key': TEST_SECOND_MD5_KEY,
                    'continue_path': payu_settings['continue_path']
                }
            else:
                return {
                    'pos_id': payu_settings['pos_id'],
                    'md5_key': payu_settings['md5_key'],
                    'second_md5_key': payu_settings['second_md5_key'],
                    'continue_path': payu_settings['continue_path']
                }
        except (AttributeError, KeyError):
            raise ImproperlyConfigured('PayU settings does not exist or not complete.')

    @classmethod
    def get_oauth_token(cls):
        params = cls.get_payu_params()

        oauth_request_data = {
            'grant_type': 'client_credentials',
            'client_id': params['pos_id'],
            'client_secret': params['md5_key']
        }
        try:
            oauth_request = requests.post(OAUTH_URL, data=oauth_request_data)
            response = oauth_request.json()
            return response['access_token']
        except:
            return False

    @classmethod
    def create(cls, request, description, products, buyer, notes=None):
        params = cls.get_payu_params()

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
            pos_id=params['pos_id'],
            customer_ip=customer_ip,
            total=total,
            description=description,
            products=json.dumps(processed_products),
            notes=notes
        )

        payment_request_data = {
            'extOrderId': str(payment.id),
            'customerIp': customer_ip,
            'merchantPosId': params['pos_id'],
            'description': description,
            'currencyCode': 'PLN',
            'totalAmount': total,
            'products': processed_products,
            'buyer': buyer,
            'settings': {'invoiceDisabled': True},
            'notifyUrl': request.build_absolute_uri(reverse('payu:api:notify')),
            'continueUrl': request.build_absolute_uri(params['continue_path']),
        }
        payment_request_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(cls.get_oauth_token())
        }
        try:
            payment_request = requests.post(ENDPOINT_URL,
                                            json=payment_request_data,
                                            headers=payment_request_headers,
                                            allow_redirects=False)
            response = payment_request.json()
            payu_order_id = escape(response['orderId'])
            redirect_url = response['redirectUri']
        except:
            return False

        payment.payu_order_id = payu_order_id
        payment.save()

        return redirect_url
