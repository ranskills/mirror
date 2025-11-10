import requests


def create_send_push_notifcation(*, logger, token: str, user: str):
    def send_push_notification(message: str) -> dict[str, str]:
        try:
            data = {
                'token': token,
                'user': user,
                'message': message,
            }
            resp = requests.post('https://api.pushover.net/1/messages.json', data=data)

            data = resp.json()
            logger.info(f'PushOver response: {data}')

        except Exception as e:
            error_msg = f'PushOver push notification failed: {e}'
            logger.error(error_msg)
            return error_msg

    return send_push_notification
