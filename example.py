#!/usr/bin/env python
"""
Demo Flask-Twilio application
"""

# Imports.
import os
from flask import flash, Flask, render_template, request, url_for
from flask_twilio import Twilio, Response
from twilio.rest.exceptions import TwilioRestException
from jinja2 import DictLoader

# A standard test number.
# See https://www.twilio.com/docs/api/rest/test-credentials.
DEFAULT_NUMBER = '+15005550006'

# Application configuration.
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['TWILIO_ACCOUNT_SID'] = os.environ['TWILIO_ACCOUNT_SID']
app.config['TWILIO_AUTH_TOKEN'] = os.environ['TWILIO_AUTH_TOKEN']
app.config['TWILIO_FROM'] = os.environ.get('TWILIO_FROM', DEFAULT_NUMBER)
twilio = Twilio(app)

# Main form template.
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
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endwith %}
    <form method=post>
        <div class=input-group>
            <input type=hidden id=say name=say value=1>
            <input type=hidden id=sms name=sms value=1>
            <input autofocus class=form-control type=tel name=to value="{{ to }}">
            <div class=input-group-btn>
                <button class="btn btn-default" type=submit>
                    Say + SMS
                </button>
                <button type=button class="btn btn-default dropdown-toggle" data-toggle=dropdown aria-haspopup=true aria-expanded=false>
                    <span class=caret></span>
                </button>
                <ul class="dropdown-menu dropdown-menu-right">
                    <li><a href="#" onclick="$('form').submit();">Say + SMS</a></li>
                    <li><a href="#" onclick="$('#sms').val(0); $('form').submit();">Say only</a></li>
                    <li><a href="#" onclick="$('#say').val(0); $('form').submit();">SMS only</a></li>
                </ul>
            </div>
        </div>
    </form>
</div>
'''})

@app.route('/twiml')
@twilio.twiml
def test_call():
    """View for producing the TwiML document."""
    say = int(request.values.get('say', 1))
    sms = int(request.values.get('sms', 1))
    resp = Response()
    if say: resp.say('This is a voice call from Twilio!', voice='female')
    if sms: resp.sms('This is an SMS message from Twilio!')
    return resp

@app.route('/', methods=['GET'])
def index_get():
    """Main form view."""
    return render_template(
        'example.html',
        to=request.values.get('to', DEFAULT_NUMBER))

@app.route('/', methods=['POST'])
def index_post():
    """Main form action."""
    try:
        say = int(request.values.get('say', 1))
        sms = int(request.values.get('sms', 1))
        to = request.values.get('to', None)
        if say:
            twilio.call_for('test_call', to, say=say, sms=sms)
        else:
            twilio.message('This is an SMS message from Twilio!', to)
        flash('Request was successfully sent to Twilio.', 'success')
    except TwilioRestException as e:
        flash('Failed to make call: ' + e.msg, 'danger')
    return index_get()

# Start application.
app.run('0.0.0.0')
