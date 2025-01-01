import os
import sys
import random
import string
import requests
import time
import json
from datetime import datetime, timedelta
import requests

class TonFarms:
    def __init__(self):
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding' : 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            # 'content-type': 'application/json',
            'origin': 'https://game.tonfarms.com',
            'referer': 'https://game.tonfarms.com/',
            'host':'api.tonfarms.com',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge WebView2";v="131"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        }
    
    def print_(self, word):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"[{now}] | {word}")

    def make_request(self, method, url, headers=None, json=None, data=None, params=None):
        retry_count = 0
        while True:
            time.sleep(2)
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, json=json)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json, data=data, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=json, data=data)
            else:
                raise ValueError("Invalid method.")
            if response.status_code >= 500:
                if retry_count >= 4:
                    self.print_(f"Status Code: {response.status_code} | {response.text}")
                    return None
                retry_count += 1
            elif response.status_code >= 400:
                self.print_(f"Status Code: {response.status_code} | {response.text}")
                return None
            elif response.status_code >= 200:
                return response
    
    def signin(self, payload, token):
        url = 'https://api.tonfarms.com/api/v1/signin'
        headers= {
                **self.headers
            }
        
        if token is not None:
            headers['authorization'] = f"Bearer {token}"

        res = self.make_request('post', url, headers=headers, json=payload)
        if res is not None:
            data = res.json()
            success = data.get('success', False)
            if success:
                return data

    def checkin(self, token):
        url = 'https://api.tonfarms.com/api/v1/achievement/checkin'
        headers= {
            **self.headers,
            'authorization': f"Bearer {token}"
        }
        res = self.make_request('get', url, headers=headers)
        if res is not None:
            data = res.json()
            success = data.get('success', False)
            if success:
                dats = data.get('data')
                day = dats.get('day')
                energy = dats.get('energy')
                star = dats.get('star')
                coin = dats.get('coin')
                ton = dats.get('ton')
                self.print_(f"Checkin day {day} Done, Reward : {energy} Energy | {star} Star | {coin} Coin | {ton} TON")
                return energy

    def start_game(self, token):
        url = 'https://api.tonfarms.com/api/v1/game/start'
        headers= {
            **self.headers,
            'authorization': f"Bearer {token}"
        }
        res = self.make_request('get', url, headers=headers)
        if res is not None:
            data = res.json()
            success = data.get('success', False)
            dats = data.get('data')
            if success:
                return dats
    
    def claim_game(self, token, payload):
        url = 'https://api.tonfarms.com/api/v1/game/get'
        headers= {
            **self.headers,
            'authorization': f"Bearer {token}"
        }
        res = self.make_request('post', url, headers=headers, json=payload)
        if res is not None:
            data = res.json()
            success = data.get('success', False)
            dats = data.get('data')
            if success:
                amount = dats.get('amount', 0)
                ton = dats.get('ton', 0)
                bonus_level = dats.get('bonus_level', 0)
                bonus_share = dats.get('bonus_share', 0)
                total_coin = dats.get('total_coin', 0)
                total_ton = dats.get('total_ton', 0)
                self.print_(f"Play game Done, Reward : {amount} Point & {ton} TON")
                self.print_(f"Bonus Point, Level : {bonus_level} Point | Share : {bonus_share} Point")
                self.print_(f"Total Coin : {total_coin} Point | Total TON : {total_ton} TON")
    
    def get_tasks(self, token):
        url = 'https://api.tonfarms.com/api/v1/quest/list'
        payload = {}
        headers= {
            **self.headers,
            'authorization': f"Bearer {token}",
            'content-length': str(len(payload))
        }
        try:
            res = self.make_request('post', url, headers=headers, json={})
            if res is not None:
                data = res.json()
                success = data.get('success', False)
                dats = data.get('data')
                for item in dats:
                    id = item.get('id', 0)
                    name = item.get('name', '')
                    if name in ['Daily shopping']:
                        continue
                    reward_amount = item.get('reward_amount')
                    is_completed = item.get('is_completed')
                    is_claimed = item.get('is_claimed')
                    if is_claimed:
                        self.print_(f"Task {name} Done!!")
                    else:
                        payload = {"quest_id":id}
                        time.sleep(3)
                        self.verify_task(token, payload)
        except Exception as Error:
            print(Error)
    
    def verify_task(self, token, payload):
        url = 'https://api.tonfarms.com/api/v1/quest/verify'
        headers= {
            **self.headers,
            'authorization': f"Bearer {token}"
        }
        res = self.make_request('post', url, headers=headers, json=payload)
        if res is not None:
            data = res.json()
            success = data.get('success', False)
            if success:
                dats = data.get('data')
                name = dats.get('name')
                reward_amount = dats.get('reward_amount')
                type = dats.get('type')
                if type == 0:
                    self.print_(f"Task {name} Done, Reward : {reward_amount} Point")
        
    def join_clan(self, token):
        url = 'https://api.tonfarms.com/api/v1/clan/join'
        headers= {
        **self.headers,
        'authorization': f"Bearer {token}"
        }
        payload = {"clan_id":"dSq68C"}
        res = self.make_request('post', url, headers=headers, json=payload)
        if res is not None:
            data = res.json()
            success = data.get('success', False)
            if success:
                self.print_("Join Clan Done")
    
    def spin(self, token):
        url = 'https://api.tonfarms.com/api/v1/lucky/spin'
        headers= {
            **self.headers,
            'authorization': f"Bearer {token}"
        }
        res = self.make_request('get', url, headers=headers)
        if res is not None:
            data = res.json()
            success = data.get('success', False)
            dats = data.get('data')
            if success:
                return dats





