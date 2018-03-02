#!/usr/bin/env python
"""
Demo Flask-Twilio application
"""

import os
import socket

from flask import flash, Flask, render_template, request
from flask_twilio import Twilio, Response
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import Message
from twilio.twiml.voice_response import Say
from jinja2 import DictLoader

# A standard test number.
# See https://www.twilio.com/docs/api/rest/test-credentials.
DEFAULT_NUMBER = '+15005550006'

# Application configuration.
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SERVER_NAME'] = socket.getfqdn() + ':5000'
app.config['TWILIO_ACCOUNT_SID'] = os.environ.get('TWILIO_ACCOUNT_SID')
app.config['TWILIO_AUTH_SID'] = os.environ.get('TWILIO_AUTH_SID')
app.config['TWILIO_AUTH_TOKEN'] = os.environ.get('TWILIO_AUTH_TOKEN')
app.config['TWILIO_FROM'] = os.environ.get('TWILIO_FROM', DEFAULT_NUMBER)
twilio = Twilio(app)

# Main form template.
app.jinja_loader = DictLoader({'example.html': '''\
<!doctype html>
<title>Flask-Twilio Test</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
<style>
.vertical-container {
    min-height: 100%;
    min-height: 100vh;
    display: flex;
    align-items: center;
}
</style>
<div class=vertical-container>
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
            <input type=hidden id=say name=say value=1>
            <input type=hidden id=sms name=sms value=1>
            <div class=input-group>
                <input autofocus class=form-control type=tel name=to value="{{ to }}">
                <div class=input-group-append>
                    <button class="btn btn-outline-primary" type=submit>
                        Say + SMS
                    </button>
                    <button type=button class="btn btn-outline-primary dropdown-toggle" data-toggle=dropdown aria-haspopup=true aria-expanded=false>
                    </button>
                    <div class="dropdown-menu dropdown-menu-right">
                        <a class=dropdown-item href="#" onclick="$('form').submit();">Say + SMS</a></li>
                        <a class=dropdown-item href="#" onclick="$('#sms').val(0); $('form').submit();">Say only</a></li>
                        <a class=dropdown-item href="#" onclick="$('#say').val(0); $('form').submit();">SMS only</a></li>
                    </div>
                </div>
            </div>
        </form>
    </div>
</div>
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
'''})


@app.route('/twiml')
@twilio.twiml
def test_call():
    """View for producing the TwiML document."""
    say = int(request.values.get('say', 1))
    sms = int(request.values.get('sms', 1))
    resp = Response()
    if say:
        resp.append(Say('This is a voice call from Twilio!', voice='female'))
    if sms:
        resp.append(Message('This is an SMS message from Twilio!'))
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
        app.logger.exception('Failed to make call')
    return index_get()


# Start application.
app.run('0.0.0.0')
