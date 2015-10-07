#!/usr/bin/env python
import os
from flask import flash, Flask, render_template, request, url_for
from flask.ext.twilio import Twilio, Response
from twilio.rest.exceptions import TwilioRestException
from jinja2 import DictLoader

DEFAULT_NUMBER = '+15005550006'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['TWILIO_ACCOUNT_SID'] = os.environ['TWILIO_ACCOUNT_SID']
app.config['TWILIO_AUTH_TOKEN'] = os.environ['TWILIO_AUTH_TOKEN']
app.config['TWILIO_FROM'] = os.environ.get('TWILIO_FROM', DEFAULT_NUMBER)
twilio = Twilio(app)

app.jinja_loader = DictLoader({'example.html': '''\
<!doctype html>
<title>Flask-Twilio Test</title>
<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css">
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
<script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
<br>
<div class=container>
<div class=jumbotron>
<h2>Flask-Twilio Test</h2>
</div>
{% with messages = get_flashed_messages() %}
    {% for message in messages %}
        <div class="alert alert-danger">{{ message }}</div>
    {% endfor %}
{% endwith %}
<form method=post>
<div class="input-group">
<input autofocus class=form-control type=tel name=to value="{{ to }}">
<span class=input-group-btn><input class="btn btn-default" type=submit value=Call></span>
</div>
</form>
</div>
'''})

@app.route('/call.twiml')
@twilio.twiml
def test_call():
    resp = Response()
    resp.say('This is a voice call from Twilio!', voice='female')
    resp.sms('This is an SMS message from Twilio!')
    return resp

@app.route('/', methods=['GET'])
def index_get():
    return render_template(
        'example.html',
        to=request.values.get('to', DEFAULT_NUMBER))

@app.route('/', methods=['POST'])
def index_post():
    try:
        twilio.call_for('test_call', request.values.get('to', None))
    except TwilioRestException as e:
        flash('Failed to make call: ' + e.msg)
    return index_get()

app.run('0.0.0.0')
