from setuptools import setup, find_packages


setup(
    name='django-payu-payments',
    version='0.1.0',
    description='PayU payments system intergration.',
    url='https://github.com/michalwerner/django-payu-payments',
    author='Michal Werner',
    author_email='werner@hurtowniapixeli.pl',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    packages=find_packages(),
    install_requires=['django', 'requests', 'django-ipware'],
)
