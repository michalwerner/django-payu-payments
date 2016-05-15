import json
import hashlib

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils.html import escape

from .models import Payment
from . import settings as payu_settings


@require_http_methods(['POST'])
@csrf_exempt
def notify(request):
    signature = escape(request.META.get('HTTP_OPENPAYU_SIGNATURE')).split(';')
    signature_data = {}
    for param in signature:
        try:
            param = param.split('=')
            signature_data[param[0]] = param[1]
        except IndexError:
            continue

    try:
        incoming_signature = signature_data['signature']
    except KeyError:
        return HttpResponse(status=400)

    second_md5_key = payu_settings.PAYU_SECOND_MD5_KEY.encode('utf-8')
    expected_signature = hashlib.md5(request.body + second_md5_key).hexdigest()
    if incoming_signature != expected_signature:
        return HttpResponse(status=403)

    try:
        data = json.loads(request.body.decode('utf-8'))
        payu_order_id = escape(data['order']['orderId'])
        internal_id = escape(data['order']['extOrderId'])
    except:
        return HttpResponse(status=400)

    try:
        payment = Payment.objects.exclude(status='COMPLETED') \
                         .get(id=internal_id, payu_order_id=payu_order_id)
    except (Payment.DoesNotExist, ValueError):
        return HttpResponse(status=200)

    status = escape(data['order']['status'])
    if status in ('PENDING', 'WAITING_FOR_CONFIRMATION', 'COMPLETED',
                  'CANCELED', 'REJECTED'):
        payment.status = status
        payment.save()
    return HttpResponse(status=200)
