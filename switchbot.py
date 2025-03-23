import json
import time
import hashlib
import hmac
import base64
import uuid
import requests  # GETリクエスト用
import os
from dotenv import load_dotenv

load_dotenv()

class SwitchBot:
    token = os.getenv("SWITCHBOT_TOKEN")
    secret = os.getenv("SWITCHBOT_SECRET")
    scene_id = os.getenv("SWITCHBOT_SCENE")

    def make_header(self):
        # Declare empty header dictionary
        apiHeader = {}
        nonce = uuid.uuid4()
        t = int(round(time.time() * 1000))
        string_to_sign = '{}{}{}'.format(self.token, t, nonce)

        string_to_sign = bytes(string_to_sign, 'utf-8')
        secret = bytes(self.secret, 'utf-8')

        sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())
        '''
        print('Authorization: {}'.format(self.token))
        print('t: {}'.format(t))
        print('sign: {}'.format(str(sign, 'utf-8')))
        print('nonce: {}'.format(nonce))'
        '''

        # Build api header JSON
        apiHeader['Authorization'] = self.token
        apiHeader['Content-Type'] = 'application/json'
        apiHeader['charset'] = 'utf8'
        apiHeader['t'] = str(t)
        apiHeader['sign'] = str(sign, 'utf-8')
        apiHeader['nonce'] = str(nonce)
        return apiHeader
    
    def exec_scene(self):
        url = "https://api.switch-bot.com/v1.1/scenes/" + self.scene_id + "/execute"
        apiHeader = self.make_header()
        response = requests.post(url, headers=apiHeader)

        # レスポンスの確認
        if response.ok:
            print("Response:")
            print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        else:
            print("Error:", response.status_code)
            print(response.text)
