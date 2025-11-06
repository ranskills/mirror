import time

import gradio as gr
from dotenv import load_dotenv
from pypdf import PdfReader

from common import Session, SessionID
from secret import get_secret
from client import create_telegram_client
from llm import create_agent_with_context


sessions: dict[SessionID, Session] = {}

load_dotenv(override=True)

TELEGRAM_TOKEN = get_secret('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = get_secret('TELEGRAM_CHAT_ID')


telegram_client = create_telegram_client(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

KNOWLEDGE_BASE_DIR = 'knowledge-base'
reader = PdfReader(f'{KNOWLEDGE_BASE_DIR}/Profile.pdf')

context = 'LinkedIn Profile: '
for page in reader.pages:
    context += page.extract_text() + '\n\n'


def ask_llm(message, history, state: Session):
    agent = create_agent_with_context(context, state)

    try:
        messages = history + [{'role': 'user', 'content': message}]
        result = agent.invoke({'messages': messages})

        last_message = result['messages'][-1]
        print('Last message')
        print(last_message)

        return last_message.content
    except Exception as e:
        print(f'Error invoking agent: {e}')
        return "🔥 I'm sorry, I encountered an error while processing your request."


message_to_ask_for_name = {
    'role': 'assistant',
    'content': 'Before you enter my MirrorVerse, please tell me your name?',
}


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
        reply_to_message_id = (
            update.get('message', {}).get('reply_to_message', {}).get('message_id')
        )
        is_broadcast = reply_to_message_id is None

        message = update['message']['text']

        response = {'role': 'assistant', 'content': message}
        if is_broadcast:
            print(f'Broadcasting to all {len(sessions)} sessions: {message}')
            for session_id in sessions:
                session = sessions[session_id]

                if session.is_live_chat:
                    session.history.append(response)
        else:
            session = find_owning_session(reply_to_message_id)
            if session:
                print(f'Adding message to session {session.session_id}')
                if session.is_live_chat:
                    session.history.append(response)


def refresh_chat(state: Session):
    global sessions

    if state is None or not state.is_live_chat:
        # return [], state
        return gr.Chatbot(type='messages'), state

    session_id = state.session_id
    print(
        f'Refreshing state {state.session_id}. # Session: {len(sessions.keys())} Last Update ID: {telegram_client.last_update_id}'
    )

    history = state.history
    if not state.is_live_chat:
        return history, state
        # return gr.Chatbot(), state

    poll_telegram_replies()

    return sessions[session_id].history, state


def chat(message, history, state: Session, timer: gr.Timer):
    if state is None:
        state = init_session()

    response = state.session_id
    history = state.history

    if not state.name:
        state.name = message.strip()
        print(f'User says he/she is: {message}')
        # state.history.append({'role': 'assistant', 'content': 'Please, what is your name?'})
        history.append(message_to_ask_for_name)
        history.append({'role': 'user', 'content': message})

        history.append({'role': 'assistant', 'content': f'Thank you, **{state.name}**'})
        with open(f'{KNOWLEDGE_BASE_DIR}/intro.md', 'r', encoding='utf-8') as file:
            history.append({'role': 'assistant', 'content': file.read()})

        return '', history, state, gr.Timer(active=False)

    live_chat_request_received = message.lower() in ['mirror', 'mirror mirror']
    live_chat_exit_received = message.lower() in ['exit', 'goodbye', 'bye', 'done', 'end']

    if live_chat_request_received:
        state.is_live_chat = True
        response = """
        Live chat **activated** 👤↔️👤, if he is not busy, you will get a response.
        To exit live chat mode, type **exit**
        """
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': response})
        return '', history, state, gr.Timer(active=True)

    history.append({'role': 'user', 'content': message})

    if state.is_live_chat and not live_chat_exit_received:
        result = telegram_client.send_message(message)
        print(f'Sent result: {type(result)} {result}')
        message_id = result.get('message_id')
        print(f'Adding new message id: {message_id}')
        state.message_ids.add(message_id)

        return '', history, state, gr.Timer(active=True)

    exit_live_chat = state.is_live_chat and live_chat_exit_received
    if exit_live_chat:
        state.is_live_chat = False
        response = 'Live chat **deactivated**. You can continue chatting with the mirror bot.'
        history.append({'role': 'assistant', 'content': response})
        return '', history, state, gr.Timer(active=False)

    response = ask_llm(message, history, state)
    history.append({'role': 'assistant', 'content': response})
    return '', history, state, gr.Timer(active=False)


title = '🪞 Mirror'
with gr.Blocks(title=title, fill_height=True) as ui:
    state: Session | None = gr.State(None)
    gr.Markdown("""
    # Mirror 🪞

    ## Look closely into the mirror and you might just see me
    """)

    chatbot = gr.Chatbot(
        value=[message_to_ask_for_name],
        type='messages',
        height='80vh',
    )
    msg = gr.Textbox(
        autofocus=True,
        container=False,
    )
    timer = gr.Timer(1, active=False)

    msg.submit(chat, inputs=[msg, chatbot, state, timer], outputs=[msg, chatbot, state, timer])
    timer.tick(refresh_chat, inputs=[state], outputs=[chatbot, state])


if __name__ == '__main__':
    ui.launch(debug=True)
