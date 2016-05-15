from django.conf import settings


TEST_POS_ID = 145227
TEST_MD5_KEY = '12f071174cb7eb79d4aac5bc2f07563f'
TEST_SECOND_MD5_KEY = '13a980d4f851f3d9a1cfc792fb1f5e50'

PAYU_POS_ID = getattr(settings, 'PAYU_POS_ID', TEST_POS_ID)
PAYU_MD5_KEY = getattr(settings, 'PAYU_MD5_KEY', TEST_MD5_KEY)
PAYU_SECOND_MD5_KEY = getattr(settings, 'PAYU_SECOND_MD5_KEY',
                              TEST_SECOND_MD5_KEY)
PAYU_CONTINUE_PATH = getattr(settings, 'PAYU_CONTINUE_PATH', '/')
PAYU_VALIDITY_TIME = getattr(settings, 'PAYU_VALIDITY_TIME', 600)
