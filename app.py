import uuid
import time
from typing import TypeAlias
from dataclasses import dataclass, field

import gradio as gr
from dotenv import load_dotenv

from secret import get_secret
from telegram import create_client


SessionID: TypeAlias = str

@dataclass
class Session:
    session_id: SessionID
    name: str
    is_live_chat: bool
    history: list[dict[str, str]]
    message_ids: set[int] = field(default_factory=set)

    @classmethod
    def new_session(cls) -> 'Session':
        session_id = str(uuid.uuid4())[:5]
        return cls(
            session_id=session_id,
            name='',
            is_live_chat=False,
            history=[],
        )

sessions: dict[SessionID, Session] = {}

load_dotenv(override=True)

TELEGRAM_TOKEN = get_secret('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = get_secret('TELEGRAM_CHAT_ID')


telegram_client = create_client(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)


# class LiveChatRequestInput(BaseModel):
#   name: str = Field(description='The name of the user')


# # print(pydantic.__version__)
# @tool(args_schema=LiveChatRequestInput)
# def live_chat_request_notifier(name: str):
#   '''Detects if the user expresses the desire to chat/interact with me live'''
#   r = f'Hello {name}, skills will now be responding to you live!'
#   print(r)
#   return r


# @tool
# def sent_telegram_message(message: str):
#   '''In live mode, send the message to this channel'''

#   chat_id=1358504684
#   url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
#   data = {'chat_id': chat_id, 'text': message}
#   response = requests.post(url, json=data)
#   print("Status Code:", response.status_code)
#   print(response.json())

# @tool
# def capture_unanswered_question(question: str):
#     '''Captures questions that are not answered'''
#     print(f'I do not have an answer for the question: {question}')
def ask_llm(message, history, state):
    pass
    # print('Current State', state)
    # messages = history + [{'role': 'user', 'content': message}]
    # result = agent.invoke({'messages': messages})

    # return result['messages'][-1].content

def init_session() -> Session:
   global sessions

   print('Initializing new session')
   session = Session.new_session()

   sessions[session.session_id] = session
   return session

last_polled_at = 0
POLL_INTERVAL = 2

def poll_telegram_replies():
    global sessions, last_polled_at

    now = time.time()
    if now - last_polled_at < POLL_INTERVAL:
        return

    last_polled_at = now
    print('Polling')

    def find_owning_session(message_id: int) -> Session | None:
        for session in sessions.values():
            if message_id in session.message_ids:
                return session
        return None

    updates = telegram_client.get_updates()

    for update in updates:
        reply_to_message_id = update.get('message', {}).get('reply_to_message', {}).get('message_id')
        is_broadcast = reply_to_message_id is None

        message = update['message']['text']

        response = {'role': 'assistant', 'content': message}
        if is_broadcast:
            print(f'Broadcasting to all {len(sessions)} sessions: {message}')
            for session_id in sessions:
                sessions[session_id].history.append(response)
        else:
            session = find_owning_session(reply_to_message_id)
            if session:
                print(f'Adding message to session {session.session_id}')
                session.history.append(response)


def refresh_chat(state: Session):
    global sessions

    if state is None:
        return [], state
        # return gr.Chatbot(), state

    session_id = state.session_id
    print(f'Refreshing state {state.session_id}. # Session: {len(sessions.keys())} Last Update ID: {telegram_client.last_update_id}')

    history = state.history
    if not state.is_live_chat:
        return history, state
        # return gr.Chatbot(), state

    poll_telegram_replies()

    return sessions[session_id].history, state


def chat(message, history, state: Session):
    if state is None:
       state = init_session()

    response = state.session_id
    history = state.history

    is_requesting_live_chat = message.lower() in ['mirror', 'mirror mirror']
    # TODO: look for exit, e.g. exit, bye, bye
    should_exit_live_chat = message.lower() in ['exit', 'goodbye', 'bye', 'done', ]

    # if not state.name:
    #     state.name = message.strip()
    #     response = f'Hello {state.name}, how can I assist you today?'
    #     return '', history, state

    if is_requesting_live_chat:
        state.is_live_chat = True
        response = '''
        Live chat **activated** 👤↔️👤, if he is not busy, you will get a response.
        To exit live chat mode, type "exit"
        '''
        history.append({'role': 'assistant', 'content': response})
        return '', history, state


    history.append({'role': 'user', 'content': message})

    if state.is_live_chat:
        # if should_exit_live_chat:
        #     state['is_live_chat'] = False

        #     return '', 'Live chat ended, back to normal mode', state
        # sent_telegram_message.invoke({'message': message})
        result = telegram_client.send_message(message)
        print(f'Sent result: {type(result)} {result}')
        message_id = result.get('message_id')
        print(f'Adding new message id: {message_id}')
        state.message_ids.add(message_id)
        # sleep(2)
        # telegram_updates = telegram_client.get_updates()
        # print('Telegram Updates')
        # print(telegram_updates)
        # x = telegram_updates[-1]
        # print('x' * 80)
        # print(x)
        # TODO: get response
        # return '', x['message']['text'], state
        return '', history, state


    history.append({'role': 'assistant', 'content': response})

    return '', history, state
    # live_chat_request = message.lower() == 'mirror mirror'
    # # TODO: look for exit, e.g. exit, bye, bye
    # exit_detected = message.lower() in ['exit', 'bye']
    # if live_chat_request:
    #     state['is_live_chat'] = True
    # #   state['session_id'] = str(uuid.uuid4())
    #     return 'Live chat **activated** 👤↔️👤, if he is not busy, you will get a response\nTo exit live chat mode, type "exit"', state

    # if state['is_live_chat']:
    #     if exit_detected:
    #         state['is_live_chat'] = False

    #         return 'Live chat ended, back to normal mode', state
    #     # sent_telegram_message.invoke({'message': message})
    #     telegram_client.send_message(message)
    #     sleep(2)
    #     telegram_updates = telegram_client.get_updates()
    #     print('Telegram Updates')
    #     print(telegram_updates)
    #     x = telegram_updates[-1]
    #     print('x' * 80)
    #     print(x)
    #     # TODO: get response
    #     return x['message']['text'], state
    # return ask_llm(message, history, state), state

title = '🪞 Mirror'
with gr.Blocks(title=title, fill_height=True) as ui:
    
    state: Session | None = gr.State(None)
    gr.Markdown('''
    # Mirror 🪞

    ## Look closely into the mirror and you might just see me
    ''')

    chatbot = gr.Chatbot(
        type='messages',
        height='80vh'
    )
    msg = gr.Textbox(
        autofocus=True, 
        container=False,
    )

    msg.submit(chat, inputs=[msg, chatbot, state], outputs=[msg, chatbot, state])
    gr.Timer(1).tick(refresh_chat, inputs=[state], outputs=[chatbot, state])


if __name__ == '__main__':
    ui.launch(debug=True)