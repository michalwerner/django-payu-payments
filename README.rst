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

``PAYU['test']``
^^^^^^^^^^^^^^^^

    Enables PayU test channel, ignoring ``post_id``,
    ``md5_key`` and ``second_md5_key``.


``PAYU['continue_path']``
^^^^^^^^^^^^^^^^^^^^^^^^^

    Specifies path on your website, where user should be redirected after payment (successful, or not).
    May be absolute path, like ``/some-page/`` or ``reverse('some:thing')``.

Usage
=====

To create payment object you have to call ``Payment.create`` method: ::

    from payu import Payment


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

``Payment.create`` will return URL where buyer should be redirected, or ``False`` if not successful.
