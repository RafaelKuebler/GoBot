import requests
import importlib
from settings import token
from bothandler import BotHandler

def main():
    bot = BotHandler(token)
    expected_id = None

    while True:
        data = bot.get_last_update()
        update_id = data['update_id']

        if expected_id is None:
            expected_id = update_id + 1
        
        if update_id != expected_id:
            continue
        
        chat_id = data['message']['chat']['id']
        print(data['message'])
        text = data['message']['text']
        bot.send_message(chat_id, text)
        expected_id += 1
    
if __name__ == '__main__':  
    main()
