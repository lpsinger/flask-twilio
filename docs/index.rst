Flask-Twilio Documentation
==========================

Flask-Twilio Installation
-------------------------

Install the extension by running pip::

    $ pip install Flask-Twilio


Set Up
------

Flask-Twilio can be initialized by first creating the application and then
creating the :py:class:`flask_twilio.Twilio` instance::

    from flask import Flask
    from flask_twilio import Twilio

    app = Flask(__name__)
    twilio = Twilio(app)

or using the factory method approach, creating the application first, then the
:py:class:`flask_twilio.Twilio` instance, and finally calling
:py:meth:`flask_twilio.Twilio.init_app`::

    twilio = Twilio()
    app = Flask(__name__)
    twilio.init_app(app)


Making a Call
-------------

Making a call involves two steps: first, creating a call view, and second,
placing a call. The view produces an XML file that serves as a script for
Twilio to follow. Here is an example call view::

    from flask_twilio import Response
    from twilio.twiml.messaging_response import Message
    from twilio.twiml.voice_response import Say

    @app.route('/call.xml')
    @twilio.twiml
    def call():
        resp = Response()
        resp.append(Say('This is a voice call from Twilio!', voice='female'))
        resp.append(Message('This is an SMS message from Twilio!'))
        return resp

The :py:attr:`flask_twilio.Twilio.twiml` decorator adds some validation and must come
`after` the ``app.route`` decorator.

To place a call using this view, we use the
:py:meth:`flask_twilio.Twilio.call_for` method, which is based on
:py:func:`flask.url_for`::

    twilio.call_for('call', to='+15005550006')


Sending a Text Message
----------------------

The above example simultaneously places a voice call and sends a text message.
If you only want to send a text message, there is a shortcut::

    twilio.message('This is an SMS message from Twilio!', to='+15005550006')


Full Example Flask Application
------------------------------

See `example.py on GitHub`_ for a full example Flask application.

.. _example.py on GitHub: https://github.com/lpsinger/flask-twilio/blob/master/example.py


Configuration Variables
-----------------------

Flask-Twilio understands the following configuration values:

=========================== ====================================================
``TWILIO_ACCOUNT_SID``      Your Twilio account SID.
``TWILIO_AUTH_SID``         The SID that you use to authenticate with Twilio,
                            if different from your account SID (for example, if
                            you are using an `API key`_).
``TWILIO_AUTH_TOKEN``       Your Twilio authentication token.
``TWILIO_FROM``             Your default 'from' phone number (optional).
                            Note that there are some useful
                            `dummy numbers for testing`_.
``SECRET_KEY``              Same as the standard Flask coniguration value.
                            If provided, then Flask-Twilio will perform some
                            sanity checking to ensure that requests from Twilio
                            result from calls placed by this application.
=========================== ====================================================

.. _dummy numbers for testing: https://www.twilio.com/docs/api/rest/test-credentials#test-sms-messages-parameters-From
.. _api key: https://www.twilio.com/docs/api/rest/keys


API
---

.. automodule:: flask_twilio
