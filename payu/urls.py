from django.conf.urls import url, include


urlpatterns = [
    url(r'^api/', include('payu.urls_api', namespace='api'))
]
