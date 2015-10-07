"""
Flask-Twilio
-------------

Make Twilio voice/SMS calls with Flask
"""
from setuptools import setup


setup(
    name='Flask-Twilio',
    version='1.0',
    url='http://example.com/flask-twilio/',
    license='BSD',
    author='Leo Singer',
    author_email='leo.singer@ligo.org',
    description='Make Twilio voice/SMS calls with Flask',
    long_description=__doc__,
    py_modules=['flask_twilio'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'itsdangerous',
        'Flask',
        'twilio'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Telephony'
    ]
)