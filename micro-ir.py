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
        "BBC1": "1",
        "BBC2": "2",
        "ITV": "3",
        "channel 4": "4",
        "channel 5": "5",
        "ITV2": "6",
        "local TV": "7",
        "London live": "8",
        "BBC4": "9",
        "ITV3": "10",
        "pick": "11",
        "Dave": "12",
        "channel 4 plus 1": "13",
        "more 4": "14",
        "film 4": "15",
        "QVC": "16",
        "really": "17",
        "4 music": "18",
        "yesterday": "19",
        "drama": "20",
        "5 USA": "21",
        "ideal world": "22",
        "create and craft": "23",
        "create an craft": "23", #
        "ITV4": "24",
        "Home": "25",
        "ITV be": "26",
        "ITV3+1": "34",
        "ITV2+1": "27",
        "E4": "28",
        "E4+1": "29",
        "5 star": "30",
        "spike": "31",
        "movie mix": "32",
        "ITV+1": "33",
        "QVC beauty": "35",
        "QVC style": "36",
        "quest": "37",
        "quest+1": "38",
        "the store": "39",
        "rocks and co": "40",
        "food network UK": "41",
        "travel channel": "42",
        "gems TV": "43",
        "channel 5+1": "44",
        "film 4+1": "45",
        "challenge": "46",
        "47": "47",
        "movies for men": "48",
        "TJC": "49",
        "movies for men +1": "50",
        "TG4": "51",
        "RTE1": "52",
        "RTE2": "53",
        "my 5": "54",
        "5 star +1": "55",
        "5 USA +1": "56",
        "viva": "57",
        "ITV Be +1": "58",
        "BT showcase": "59",
        "true crime": "60",
        "true entertainment": "61",
        "ITV4+1": "62",
        "community": "63",
        "CBS action": "64",
        "TBN UK": "65",
        "CBS reality": "66",
        "CBS reality+1": "67",
        "TruTV": "68",
        "TruTV+1": "69",
        "horror": "70",
        "CBS drama": "71",
        "your TV": "72",
        "your TV+1": "73",
        "true movies 1": "74",
        "chart show TV": "75",
        "jewellery maker": "76",
        "rishtey europe": "77",
        "shop 8-12": "78",
        "Dave ja vu": "79",
        "ShowBiz TV": "80",
        "talking pictures": "81",
        "vintage TV": "82",
        "blaze": "83",
        "blaze+1": "84",
        "hochanda": "85",
        "viva+1": "86",
        "keep it country": "87",
        "clubland TV": "89",
        "front runner TV": "91",
        "children's section": "95",
        "ketchup TV": "96",
        "freeview information": "100",
        "BBC1 HD": "101",
        "BBC2 HD": "102",
        "ITV HD": "103",
        "channel 4 HD": "104",
        "channel 5 HD": "105",
        "BBC4 HD": "106",
        "BBC news HD": "107",
        "Al Jazeera Eng HD": "108",
        "Channel 4+1 HD": "109",
        "47 HD": "110",
        "QVC+1 HD": "111",
        "QVC beauty HD": "112",
        "RT HD": "113",
        "CBBC": "120",
        "CBeebies": "121",
        "CITV": "122",
        "CBBC HD": "123",
        "CBeebies HD": "124",
        "POP": "125",
        "Tiny POP": "126",
        "Kix": "127",
        "POP+1": "128",
        "Tiny POP+1": "129",
        "BBC news": "130",
        "BBC parliament": "131",
        "Sky news": "132",
        "RT": "135",
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

        try:
            if int(channel) > 0 and int(channel) < 999:
                #specific channel number
                for digit in channel:
                    self._send_digit(digit)
                return self.alexa_response(text="channel changed to %s" % channel)
        except ValueError:
            if channel not in self.channels:
                return self.alexa_response(text="I don't know that channel")

        #TODO press close/back or something
        irsend("youview", "KEY_CLOSE")
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
