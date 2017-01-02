import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s\t%(filename)s\t%(levelname)s\t%(funcName)s:%(lineno)d\t%(message)s',
    filename="ir.log")
log = logging.getLogger(__name__)

from pprint import pprint, pformat

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

import os

def irsend(device, key):
    cmd = "irsend SEND_ONCE %s %s --count=3" % (device, key)
    log.debug(cmd)
    os.system(cmd)

class RootResource(Resource):
    intents = [
        'Testing',
        'TvPower',
        'YouviewPower',
        'ChangeChannel',
    ]

    channels = {
        "Dave": "039",
        "BBC 1": "101",
        "BBC 2": "102",
        "ITV": "103",
    }

    def alexa_response(self, text=None):
        if text is None:
            text = "sorry, I don't know how to do that"
        response = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": text
                }
            },
        }
        log.debug(pformat(response))
        return response

    def sorry(self):
        return self.alexa_response(text=None)

    def tv_power(self):
        irsend("toshiba_tv", "KEY_POWER")
        return self.alexa_response(text="TV power toggled")

    def youview_power(self):
        irsend("youview", "KEY_POWER")
        return self.alexa_response(text="Youview power toggled")

    def _send_digit(self, digit):
        irsend("youview", "KEY_NUMERIC_%s" % digit)

    def change_channel(self, channel):
        log.info("changing channel to %s" % channel)

        if channel not in self.channels:
            return self.alexa_response(text="I don't know that channel")

        #TODO press close/back or something
        for digit in self.channels[channel]:
            self._send_digit(digit)

        return self.alexa_response(text="channel changed to %s" % channel)

    def post(self):
        log.debug(pformat(request.get_json()))

        #TODO validate the signature

        alexa = request.get_json()
        if alexa['request']['type'] != 'IntentRequest':
            return self.sorry()

        intent = alexa['request']['intent']['name']
        ts = alexa['request']['timestamp']
        #TODO reject old requests

        if intent not in self.intents:
            return self.sorry()

        if intent == 'TvPower':
            return self.tv_power()

        if intent == 'YouviewPower':
            return self.youview_power()

        if intent == 'ChangeChannel':
            slots_channel = alexa['request']['intent']['slots']['channel']
            if 'value' not in slots_channel:
                return self.alexa_response(text="sorry, I didn't catch the channel name")

            channel = alexa['request']['intent']['slots']['channel']['value']
            return self.change_channel(channel)

        if intent == "Testing":
            return self.alexa_response(text="Testing, testing, 1, 2, 3.")

        return self.sorry()

api.add_resource(RootResource, '/')

if __name__ == '__main__':
    log.info("starting...")
    app.run(debug=True, port=8000, host='0.0.0.0')
