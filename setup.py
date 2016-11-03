"""
Flask-Twilio
-------------

Make Twilio voice/SMS calls with Flask
"""
from setuptools import setup
exec(open('flask_twilio.py').readline())


setup(
    name='Flask-Twilio',
    version=__version__,
    url='https://github.com/lpsinger/flask-twilio',
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
        'six',
        'twilio'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Telephony'
    ]
)