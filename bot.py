import base64
import json
import os
import random
import sys
import time
from urllib.parse import parse_qs, unquote
from datetime import datetime, timedelta
from ton_farms import TonFarms



def print_(word):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"[{now}] | {word}")

def gets(id):
        tokens = json.loads(open("tokens.json").read())
        if str(id) not in tokens.keys():
            return None
        return tokens[str(id)]

def save(id, token):
        tokens = json.loads(open("tokens.json").read())
        tokens[str(id)] = token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))

def update(id, new_token):
    tokens = json.loads(open("tokens.json").read())
    if str(id) in tokens.keys():
        tokens[str(id)] = new_token
        open("tokens.json", "w").write(json.dumps(tokens, indent=4))
    else:
        return None

def delete_all():
    open("tokens.json", "w").write(json.dumps({}, indent=4))

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def load_query():
    try:
        with open('tonfarms_query.txt', 'r') as f:
            queries = [line.strip() for line in f.readlines()]
        return queries
    except FileNotFoundError:
        print("File query .txt not found.")
        return [  ]
    except Exception as e:
        print("Failed get Query :", str(e))
        return [  ]

def parse_query(query: str):
    parsed_query = parse_qs(query)
    parsed_query = {k: v[0] for k, v in parsed_query.items()}
    user_data = json.loads(unquote(parsed_query['user']))
    parsed_query['user'] = user_data
    return parsed_query

def print_delay(delay):
    print()
    while delay > 0:
        now = datetime.now().isoformat(" ").split(".")[0]
        hours, remainder = divmod(delay, 3600)
        minutes, seconds = divmod(remainder, 60)
        sys.stdout.write(f"\r[{now}] | Waiting Time: {round(hours)} hours, {round(minutes)} minutes, and {round(seconds)} seconds")
        sys.stdout.flush()
        time.sleep(1)
        delay -= 1
    print_("Waiting Done, Starting....\n")


def main():
    selector_game = input("choose : 1(playgame) 2(spin) n(skip all) 1/2/n : ")
    while True:
        delete_all()
        start_time = time.time()
        delay = 8*3600
        clear_terminal()
        queries = load_query()
        sum = len(queries)
        ton_farms = TonFarms()
        for index, query in enumerate(queries, start=1):
            users = parse_query(query).get('user')
            id = users.get('id')
            print_(f"SxG======= Account {index}/{sum} [ {users.get('username','')} ] ========SxG")
            payload = {
                'avatar': users.get('photo_url'),
                'firstname': users.get('first_name'),
                'lastname': users.get('last_name'),
                'telegram_id': users.get('id'),
                'username': users.get('username')
            }
            token = gets(id)
            data_sign = ton_farms.signin(payload, token)
            if data_sign is not None:
                data = data_sign.get('data')
                access_token = data.get('access_token')
                if token is None:
                    save(id, access_token)
                else:
                    update(id, access_token)
                is_checkin_today = data.get('is_checkin_today', True)
                username = data.get('username','')
                coin = data.get('coin', 0)
                ton = data.get('ton',0)
                energy = data.get('energy', 0)
                clan_id = data.get('clan_id', 0)
                level = data.get('level', 0)
                print_(f"Coin : {coin} | TON : {ton} | energy : {energy} | Level : {level}")

                if is_checkin_today == False:
                    energys = ton_farms.checkin(access_token)

                if clan_id == 0:
                    ton_farms.join_clan(access_token)

                print_('Start Task')
                ton_farms.get_tasks(access_token)
                if selector_game == '1':
                    if energy > 1:
                        print_('Start Game')
                        for i in range(energy-1):
                            print_(f"Playing Game {i+1}")
                            data_start = ton_farms.start_game(access_token)
                            time.sleep(30)
                            if data_start is not None:
                                id_game = data_start.get('id', 0)
                                ton_game = data_start.get('ton', 0)
                                amount = random.randint(120, 150)
                                payload = {"amount":amount, "id":id_game, "ton":ton_game}
                                ton_farms.claim_game(access_token, payload)
                
                if selector_game == '2':
                    if energy >= 3:
                        while True:
                            data_spin = ton_farms.spin(access_token)
                            if data_spin is not None:
                                title = data_spin.get('title')
                                total_energy = data_spin.get('total_energy')
                                energy = total_energy
                                keys = title.lower()
                                reward = data_spin.get(f'{keys}')
                                print_(f"Spin Done, Reward : {reward} {title}")
                                if energy < 3:
                                    break


  
        end_time = time.time()
        total = delay - (end_time-start_time)
        if total > 0:
            print_delay(total)

if __name__ == "__main__":
     main()