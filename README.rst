.. image:: https://codeclimate.com/github/michalwerner/django-payu-payments/badges/gpa.svg
   :target: https://codeclimate.com/github/michalwerner/django-payu-payments
   :alt: Code Climate

Installation
============

1. Install via pip: ::

    pip install django-payu-payments

2. Add ``payu`` to INSTALLED_APPS: ::

    INSTALLED_APPS = [
        ...
        'payu',
        ...
    ]

3. Add URLs to URLConf: ::

    url(r'^payments/', include('payu.urls', namespace='payu')),

4. Add following settings to your settings module: ::

    PAYU = {
        'test': True,
        'pos_id': 'YOUR POS ID',
        'md5_key': 'YOUR MD5 KEY',
        'second_md5_key': 'YOUR SECOND MD5 KEY',
        'continue_path': '/some-page/'
    }

5. Run migrations: ::

    python manage.py migrate

Configuration
=============

- ``PAYU['test']``

    Enables PayU test channel, ignoring ``post_id``,
    ``md5_key`` and ``second_md5_key``.

- ``PAYU['continue_path']``

    Specifies path on your website, where user should be redirected after payment (successful, or not).
    May be absolute path, like ``/some-page/`` or ``reverse('some:thing')``.

Create payment
==============

To create payment object you have to call ``Payment.create`` method: ::

    from payu.models import Payment


    description = 'Some stuff'
    products = [
        {
            'name': 'Some product',
            'unitPrice': 14.99,
            'quantity': 1
        },
        {
            'name': 'Some other product',
            'unitPrice': 3.19,
            'quantity': 4
        }
    ]
    buyer = {
        'email': 'john.doe@domain.com',
        'firstName': 'John',
        'lastName': 'Doe'
    }
    notes = 'This client is important for us, we should prioritize him.'

    payment = Payment.create(request, description, products, buyer, notes)

``request`` is just Django HTTP request object, we need it to get buyer IP, and absolute URLs.

``notes`` are optional, all other arguments are required.

``Payment.create`` will return two-key dictionary, containing ``Payment`` object and URL where buyer should be redirected, or ``False`` if not successful. ::

    {
        'object': <Payment object>,
        'redirect_url': 'https://...'
    }

Fetch payment's data
====================

To get data associated with payment you just need to retrieve ``Payment`` object: ::

    Payment.objects.get(...)

There are also few helpful methods, which you can call on ``Payment`` object:

- ``get_total_display()``

    Returns pretty formatted ``total`` value.

- ``get_products_table()``

    Returns pretty formatted table of products associated with payment.

- ``is_successful()``

    For ``status`` equal ``COMPLETED`` returns ``True``, otherwise ``False``.

- ``is_not_successful()``

    For ``status`` equal ``CANCELED`` or ``REJECTED`` returns ``True``, otherwise ``False``.


Changelog
=========

0.1.2
-----
- changelog added
- ``get_total_display()``,  ``get_products_table()``, ``is_successful()`` and ``is_not_successful()`` methods added
- JSONField is not Postgres-only anymore
- ``Payment.create()`` now returns two-key dictionary instead of just redirect URL
- ``Payment`` objects are now ordered from newest to oldest, by default

JSONField and ordering related changes requires you to take some action when upgrading.

1) run migrations: ``python manage.py migrate payu``.

2) run following code, using Django shell (``python manage.py shell``): ::

    import json
    from payu.models import Payment


    for p in Payment.objects.all():
        if isinstance(p.products, str):
             p.products = json.loads(p.products)
             p.save()

0.1.1
-----
- sum added to products table

0.1.0
-----
- initial version
