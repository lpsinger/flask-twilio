from base64 import urlsafe_b64encode
from functools import wraps
from os import urandom
from urlparse import urlsplit, urlunsplit
from twilio.rest import TwilioRestClient
from twilio.util import RequestValidator
from twilio.twiml import Response as TwimlResponse
from flask import Response as FlaskResponse
from flask import abort, current_app, make_response, request, url_for
from itsdangerous import TimestampSigner


# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class Response(FlaskResponse, TwimlResponse):
    def __init__(self, *args, **kwargs):
        TwimlResponse.__init__(self)
        FlaskResponse.__init__(self, *args, **kwargs)

    @property
    def response(self):
        return [self.toxml()]

    @response.setter
    def response(self, value):
        pass


class Twilio(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

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
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'twilio_client'):
                ctx.twilio_client = TwilioRestClient(
                    current_app.config['TWILIO_ACCOUNT_SID'],
                    current_app.config['TWILIO_AUTH_TOKEN'])
            return ctx.twilio_client

    @property
    def validator(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'twilio_validator'):
                ctx.twilio_validator = RequestValidator(
                    current_app.config['TWILIO_AUTH_TOKEN'])
            return ctx.twilio_validator

    @property
    def signer(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'twilio_signer'):
                ctx.twilio_signer = TimestampSigner(
                    current_app.config['SECRET_KEY'], 'twilio')
            return ctx.twilio_signer

    def twiml(self, view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_app.testing:
                auth = request.authorization
                if not auth:
                    return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
                authorized = (
                    auth.username == 'twilio' and
                    self.signer.validate(auth.password, max_age=600))
                if not authorized:
                    abort(401)
                valid = self.validator.validate(
                    request.url,
                    request.form,
                    request.headers.get('X-Twilio-Signature', ''))
                if not valid:
                    abort(403)
            rv = view_func(*args, **kwargs)
            resp = make_response(rv)
            resp.mimetype = 'text/xml'
            return resp
        wrapper.methods = ('GET', 'POST',)
        return wrapper

    def call_for(self, endpoint, to, **values):
        values = dict(values, _external=True)
        from_ = values.pop('from_', None) or current_app.config['TWILIO_FROM']
        url = url_for(endpoint, **values)
        if not current_app.testing:
            urlparts = list(urlsplit(url))
            password = self.signer.sign(urlsafe_b64encode(urandom(24)))
            urlparts[1] = 'twilio:' + password + '@' + urlparts[1]
            url = urlunsplit(urlparts)
        return self.client.calls.create(to=to, from_=from_, url=url)
