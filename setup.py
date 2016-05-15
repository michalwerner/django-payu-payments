from setuptools import setup, find_packages


setup(
    name='django-payu-payments',
    version='0.1.3',
    description='PayU integration for Django.',
    url='https://github.com/michalwerner/django-payu-payments',
    author='Michal Werner',
    author_email='michal@hurtowniapixeli.pl',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django',
        'jsonfield',
        'requests',
        'django-ipware'
    ],
)
