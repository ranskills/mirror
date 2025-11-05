import requests


class TelegramClient:
  def __init__(self, token: str, chat_id: str):
    self.token = token
    self.chat_id = chat_id
    self.base_url = f'https://api.telegram.org/bot{self.token}'


  def send_message(self, message):
    url = f'{self.base_url}/sendMessage'
    data = {'chat_id': self.chat_id, 'text': message}
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    ret = response.json()

    return ret


  def get_updates(self, last_update_id: int | None):
    print('Fetching updates from Telegram')
    url = f'{self.base_url}/getUpdates'
    # data = {'chat_id': self.chat_id, 'text': message}
    params = {'limit': 10, 'timeout': 30}
    if last_update_id is not None:
        params['offset'] = last_update_id + 1

    response = requests.get(url, params=params)
    print("Status Code:", response.status_code)
    print(response)
    ret = response.json()

    # if ret['ok']
    return ret['result']


def create_client(token, chat_id) -> TelegramClient:
    return TelegramClient(token, chat_id)