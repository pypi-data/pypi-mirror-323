import requests
from datetime import datetime
import os
import logging

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
url_h = os.getenv("HASURA_URL")
hasura_secret = os.getenv("HASURA_SECRET") 
start_hour = int(os.getenv("TELEGRAM_START_HOUR", 0))
end_hour = int(os.getenv("TELEGRAM_END_HOUR", 24))
sourse = os.getenv("SOURSE", "not specified")

if not bot_token or not chat_id or not url_h or not hasura_secret:
    raise ValueError("Bot token or chat ID or HASURA_URL or HASURA_SECRET not set. Please check your .env file.")

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

def send(message: str, parse_mode: str = "Markdown") -> None:
    """
    Відправляє повідомлення в Telegram в заданий час (від 0 до 24).
    """
    
    now = datetime.now()
    current_hour = now.hour
    telegram_max_symbol = 4096
    if start_hour <= current_hour and current_hour < end_hour:
        try:
            if len(message) > telegram_max_symbol:
                message = message[:telegram_max_symbol]
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                # "disable_notification": True # повідомлення буде надіслано без звукового сповіщення
                "parse_mode": parse_mode
            }
            my_rez=requests.post(url, json=payload, timeout=10)
            
            if my_rez.status_code == 200:
                logging.info(f"Message sent successfully to chat_id={chat_id}")
            else:
                logging.error(f"Message sent with reason: {my_rez.reason}")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending message: {e}") # помилки, пов’язані з HTTP-запитами
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
    else:
        logging.info(f"Current time ({current_hour}) is outside the allowed range ({start_hour}-{end_hour}).")
        #connect to hasura
        url = url_h
        headers={'X-Hasura-Admin-Secret': hasura_secret}  
                
        mutation = """
          mutation m($object: python_telegram_insert_input!) {
              insert_python_telegram_one(object: $object) {
               id
               }
            }
           """
        variables = {  "object": {
                           "telegram_id": chat_id,
                           "message":message,
                           "format_type": parse_mode,
                           "created_by": sourse
                            }
                    }
        
        payload = {
            "query": mutation,
            "variables": variables
            }


        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
           data = response.text
           logging.info(f"Record added ID: {data}")
        else:
           logging.error(f"The error is not added to the list: {response.status_code}")

