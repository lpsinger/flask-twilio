from six.moves.urllib.parse import urlsplit
from base64 import b64encode
import pytest
from flask import Flask
from twilio.request_validator import RequestValidator
from twilio.rest.api.v2010.account.call import CallList
from flask_twilio import Twilio, Response
from twilio.twiml.voice_response import Say


def basic_auth(username, password):
    auth = 'Basic ' + b64encode((username + ':' + password).encode()).decode()
    return {'Authorization': auth}


@pytest.fixture
def twilio():
    app = Flask(__name__)
    app.config['TWILIO_ACCOUNT_SID'] = 'sid'
    app.config['TWILIO_AUTH_TOKEN'] = 'token'
    app.config['TWILIO_FROM'] = '+15005550006'
    twilio = Twilio(app)

    @app.route('/call')
    @twilio.twiml
    def call():
        resp = Response()
        resp.append(Say('Testing, 1, 2, 3.'))
        return resp

    return twilio


@pytest.fixture
def always_valid(monkeypatch):
    monkeypatch.setattr(
        RequestValidator, 'validate', lambda *args, **kargs: True)


@pytest.fixture
def always_invalid(monkeypatch):
    monkeypatch.setattr(
        RequestValidator, 'validate', lambda *args, **kargs: False)


@pytest.fixture
def mock_create_call(monkeypatch):
    ret = dict()

    def store(self, to, from_, url):
        ret['to'] = to
        ret['from_'] = from_
        ret['url'] = url

    monkeypatch.setattr(CallList, 'create', store)
    return ret


def test_get_denied(twilio):
    """Check that GET requests are denied."""
    app = twilio.app
    test_client = app.test_client()
    resp = test_client.get('/call')
    assert resp.status_code == 405


def test_post_denied(twilio):
    """Check that POST requests are denied if they do not carry a valid Twilio
    signature."""
    app = twilio.app
    test_client = app.test_client()
    resp = test_client.post('/call')
    assert resp.status_code == 403


def test_testing_allowed(twilio):
    """Check that POST requests are allowed in testing mode."""
    app = twilio.app
    test_client = app.test_client()
    app.config['TESTING'] = True
    resp = test_client.post('/call')
    assert resp.status_code == 200


def test_valid_allowed(twilio, always_valid):
    """Check that POST requests are allowed if Twilio validates them."""
    app = twilio.app
    test_client = app.test_client()
    resp = test_client.post('/call')
    assert resp.status_code == 200


def test_invalid_allowed(twilio, always_invalid):
    """Check that invalid POST requests are denied if Twilio does not validate
    them."""
    app = twilio.app
    test_client = app.test_client()
    resp = test_client.post('/call')
    assert resp.status_code == 403


def test_no_auth(twilio):
    """Test that server sends auth challenge if secret key is set"""
    app = twilio.app
    test_client = app.test_client()
    app.config['SECRET_KEY'] = 'secret'
    resp = test_client.post('/call')
    assert resp.status_code == 401


def test_wrong_username(twilio):
    """Test that server declines if username is wrong"""
    app = twilio.app
    test_client = app.test_client()
    app.config['SECRET_KEY'] = 'secret'
    resp = test_client.post('/call', headers=basic_auth('bob', 'password'))
    assert resp.status_code == 401


def test_wrong_password(twilio):
    """Test that server declines if username is wrong"""
    app = twilio.app
    test_client = app.test_client()
    app.config['SECRET_KEY'] = 'secret'
    resp = test_client.post('/call', headers=basic_auth('twilio', 'password'))
    assert resp.status_code == 401


def test_auth_correct(twilio, always_valid, mock_create_call):
    """Test that server permits a request that is not spoofed"""
    app = twilio.app
    test_client = app.test_client()
    app.config['SECRET_KEY'] = 'secret'
    with app.test_request_context():
        twilio.call_for('call', to='+15005550006')
    urlparts = urlsplit(mock_create_call['url'])
    username, password = urlparts.netloc.split('@')[0].split(':')
    resp = test_client.post(
        urlparts.path, headers=basic_auth(username, password))
    assert resp.status_code == 200
