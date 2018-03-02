__version__ = '0.0.6'
__all__ = ('Response', 'Twilio')

from string import ascii_letters, digits
from random import SystemRandom
from functools import wraps
from six.moves.urllib.parse import urlsplit, urlunsplit
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from twilio.twiml import TwiML
from flask import Response as FlaskResponse
from flask import abort, current_app, make_response, request, url_for
from flask import _app_ctx_stack as stack
from itsdangerous import TimestampSigner


rand = SystemRandom()
letters_and_digits = ascii_letters + digits


class Response(FlaskResponse, TwiML):
    """
    A response class for constructing TwiML documents, providing all of
    the verbs that are available through :py:class:`twilio.twiml.Response`.
    See also https://www.twilio.com/docs/api/twiml.
    """

    def __init__(self, *args, **kwargs):
        TwiML.__init__(self)
        FlaskResponse.__init__(self, *args, **kwargs)

    @property
    def response(self):
        return [self.to_xml()]

    @response.setter
    def response(self, value):
        pass


class Twilio(object):
    """This class is used to control Twilio calls."""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Factory method."""
        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'twilio_client'):
            del ctx.twilio_client
        if hasattr(ctx, 'twilio_validator'):
            del ctx.twilio_validator
        if hasattr(ctx, 'twilio_signer'):
            del ctx.twilio_signer

    @property
    def client(self):
        """
        An application-specific intance of
        :py:class:`twilio.rest.Client`. Primarily for internal use.
        """
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'twilio_client'):
                username = current_app.config.get('TWILIO_AUTH_SID')
                account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
                if username is None:
                    username = account_sid
                elif account_sid is None:
                    account_sid = username
                password = current_app.config['TWILIO_AUTH_TOKEN']
                ctx.twilio_client = Client(
                    username=username, password=password,
                    account_sid=account_sid)
            return ctx.twilio_client

    @property
    def validator(self):
        """
        An application-specific instance of
        :py:class:`twilio.request_validator.RequestValidator`.
        Primarily for internal use.
        """
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'twilio_validator'):
                ctx.twilio_validator = RequestValidator(
                    current_app.config['TWILIO_AUTH_TOKEN'])
            return ctx.twilio_validator

    @property
    def signer(self):
        """
        An application-specific instance of
        :py:class:`itsdangerous.TimestampSigner`, or ``None`` if no secret key
        is set. Primarily for internal use.
        """
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'twilio_signer'):
                if current_app.secret_key is not None:
                    ctx.twilio_signer = TimestampSigner(
                        current_app.secret_key, 'twilio')
                else:
                    ctx.twilio_signer = None
            return ctx.twilio_signer

    def twiml(self, view_func):
        """Decorator for marking view that will create TwiML documents."""
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not(current_app.debug or current_app.testing):
                if request.method != 'POST':
                    abort(405)

                # Perform HTTP Basic authentication if a secret key is set.
                #
                # The username must be `twilio`, and the password must be a
                # validly signed string that was generated less than 10 minutes
                # ago. This guarantees that the Twilio call was initiated by
                # this application, rather than a malicious agent.
                #
                # Note that if we are using HTTP, then a malicious agent can
                # still snoop on the data that we are sending to and from
                # Twilio, and can also spoof our reply to Twilio. Both issues
                # would be addressed by using HTTPS.
                if self.signer is not None:
                    auth = request.authorization
                    authorized = (
                        auth and
                        auth.username == 'twilio' and
                        self.signer.validate(auth.password, max_age=600))
                    if not authorized:
                        # If authorization failed, then issue a challenge.
                        return 'Unauthorized', 401, {
                            'WWW-Authenticate': 'Basic realm="Login Required"'}
                # Validate the Twilio request. This guarantees that the request
                # came from Twilio, rather than some other malicious agent.
                valid = self.validator.validate(
                    request.url,
                    request.form,
                    request.headers.get('X-Twilio-Signature', ''))
                if not valid:
                    # If the request was spoofed, then send '403 Forbidden'.
                    abort(403)
            # Call the view itself.
            rv = view_func(*args, **kwargs)
            # Adjust MIME type and return.
            resp = make_response(rv)
            resp.mimetype = 'text/xml'
            return resp
        wrapper.methods = ('GET', 'POST')
        # Done!
        return wrapper

    def call_for(self, endpoint, to, **values):
        """
        Initiate a Twilio call.

        Parameters
        ----------
        endpoint : `str`
            The view endpoint, as would be passed to :py:func:`flask.url_for`.
        to : `str`
            The destination phone number.
        values : `dict`
            Additional keyword arguments to pass to :py:func:`flask.url_for`.

        Returns
        -------
        call : `twilio.rest.resources.Call`
            An object representing the call in progress.
        """
        # Extract keyword arguments that are intended for `calls.create`
        # instead of `url_for`.
        values = dict(values, _external=True)
        from_ = values.pop('from_', None) or current_app.config['TWILIO_FROM']

        # Construct URL for endpoint.
        url = url_for(endpoint, **values)

        # If we are not in debug or testing mode and a secret key is set, then
        # add HTTP basic auth information to the URL. The username is `twilio`.
        # The password is a random string that has been signed with
        # `itsdangerous`.
        if not(current_app.debug or current_app.testing or self.signer is None):
            urlparts = list(urlsplit(url))
            token = ''.join(rand.choice(letters_and_digits) for i in range(32))
            password = self.signer.sign(token).decode()
            urlparts[1] = 'twilio:' + password + '@' + urlparts[1]
            url = urlunsplit(urlparts)

        # Issue phone call.
        return self.client.calls.create(to=to, from_=from_, url=url)

    def message(self, body, to, **values):
        """
        Send an SMS message with Twilio.

        Parameters
        ----------
        body : `str`
            The body of the text message.
        to : `str`
            The destination phone number.
        values : `dict`
            Additional keyword arguments to pass to
            :py:meth:`twilio.rest.resources.SmsMessages.create`.

        Returns
        -------
        message : :py:class:`twilio.rest.resources.SmsMessage`
            An object representing the message that was sent.
        """
        values = dict(values)
        from_ = values.pop('from_', None) or current_app.config['TWILIO_FROM']
        return self.client.messages.create(
            body=body, to=to, from_=from_, **values)
