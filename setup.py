from setuptools import setup, find_packages


setup(
    name='django-payu-payments',
    version='0.1.0',
    description='PayU integration for Django.',
    url='https://github.com/michalwerner/django-payu-payments',
    author='Michal Werner',
    author_email='werner@hurtowniapixeli.pl',
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
    install_requires=[
        'django',
        'requests',
        'django-ipware'
    ],
)
