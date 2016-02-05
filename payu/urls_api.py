from django.conf.urls import url

# callable views
from .api import notify


urlpatterns = [
    url(r'^notify/$', notify, name='notify')
]
