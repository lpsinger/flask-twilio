Flask-Twilio Documentation
==========================

.. module:: flask.ext.twilio

Flask-Twilio Installation
-------------------------

Install the extension with one of the following commands::

    $ easy_install Flask-Cache

or alternatively if you have pip installed::

    $ pip install Flask-Cache


Set Up
------

Flask-Twilio can be initialized two interchangeable ways::

    from flask import Flask
    from flask.ext.twilio import Twilio

    app = Flask(__name__)
    twilio = Twilio(app)

or using the factory method approach, creating the ``Twilio`` instance first::

    from flask import Flask
    from flask.ext.twilio import Twilio

    twilio = Twilio()
    app = Flask(__name__)
    twilio.init_app(app)


Configuration Variables
-----------------------

Flask-Twilio understands the following configuration values:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

=========================== ====================================================
``TWILIO_ACCOUNT_SID``      Your Twilio account SID
``TWILIO_AUTH_TOKEN``       Your Twilio account's authentication token
``TWILIO_FROM``             Your default 'from' phone number (optional)
``SECRET_KEY``              Same as the standard Flask coniguration value.
                            Required for signing Twilio requests.
=========================== ====================================================


API
---

.. autoclass:: Twilio
   :members: init_app,
             call_for, message, client, validator, signer

.. autoclass:: Response