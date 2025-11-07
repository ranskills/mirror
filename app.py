import time

import gradio as gr
from pypdf import PdfReader

from common import Session, SessionID, KNOWLEDGE_BASE_DIR, AVATARS_DIR, logger
from client import create_telegram_client
from llm import get_proverb, chat_llm


sessions: dict[SessionID, Session] = {}

telegram = create_telegram_client()

reader = PdfReader(f'{KNOWLEDGE_BASE_DIR}/Profile.pdf')

context = 'LinkedIn Profile: '
for page in reader.pages:
    context += page.extract_text() + '\n\n'


message_to_ask_for_name = {
    'role': 'assistant',
    'content': 'Before you enter my MirrorVerse, please tell me your name?',
}


def init_session() -> Session:
    global sessions
    logger.debug('Initializing new session')
    session = Session.new_session()
    sessions[session.session_id] = session
    return session


last_polled_at = 0
POLL_INTERVAL = 1


def poll_telegram_replies():
    global sessions, last_polled_at

    now = time.time()
    if now - last_polled_at < POLL_INTERVAL:
        return

    last_polled_at = now
    logger.debug('Polling telegram for updates')

    def find_owning_session(message_id: int) -> Session | None:
        for session in sessions.values():
            if message_id in session.message_ids:
                return session
        return None

    updates = telegram.get_updates()

    for update in updates:
        reply_to_message_id = (
            update.get('message', {}).get('reply_to_message', {}).get('message_id')
        )
        is_broadcast = reply_to_message_id is None

        message = update['message']['text']

        response = {'role': 'assistant', 'content': message}
        if is_broadcast:
            logger.info(f'Broadcasting to all {len(sessions)} sessions: {message}')
            for session_id in sessions:
                session = sessions[session_id]

                if session.is_live_chat:
                    session.history.append(response)
        else:
            session = find_owning_session(reply_to_message_id)
            if session:
                logger.debug(f'Adding message to session {session.session_id}')
                if session.is_live_chat:
                    session.history.append(response)


def refresh_chat(state: Session):
    global sessions

    if state is None or not state.is_live_chat:
        return gr.Chatbot(type='messages'), state

    session_id = state.session_id
    logger.debug(
        f'Refreshing state {state.session_id}. # Session: {len(sessions.keys())} Last Update ID: {telegram.last_update_id}'
    )

    history = state.history
    if not state.is_live_chat:
        return history, state

    poll_telegram_replies()

    return sessions[session_id].history, state


def handle_user_name(message, history, state: Session, timer: gr.Timer):
    state.name = message.strip()
    logger.info(f'New user joined: {message}')
    # state.history.append({'role': 'assistant', 'content': 'Please, what is your name?'})
    history.append(message_to_ask_for_name)
    history.append({'role': 'user', 'content': message})

    history.append({'role': 'assistant', 'content': f'Thank you, **{state.name}**! 🫱🏾‍🫲🏽'})
    history.append({'role': 'assistant', 'content': get_proverb()})
    with open(KNOWLEDGE_BASE_DIR / 'intro.md', 'r', encoding='utf-8') as file:
        history.append({'role': 'assistant', 'content': file.read()})

    return '', history, state, gr.Timer(active=False)


def handle_live_chat_request(message, history, state: Session, timer: gr.Timer):
    state.is_live_chat = True
    response = """
    Live chat **activated** 👤↔️👤, if he is not busy, you will get a response.
    To exit live chat mode, type **exit**
    """

    state.live_chat_start_at = time.time()
    history.append({'role': 'user', 'content': message})
    history.append({'role': 'assistant', 'content': response})

    return '', history, state, gr.Timer(active=True)


def handle_live_chat_exit(message, history, state: Session, timer: gr.Timer):
    state.is_live_chat = False
    response = 'Live chat **deactivated**. You can continue chatting with the mirror bot.'
    history.append({'role': 'assistant', 'content': response})

    return '', history, state, gr.Timer(active=False)


def chat(message, history, state: Session, timer: gr.Timer):
    if state is None:
        state = init_session()

    response = state.session_id
    history = state.history

    if not state.name:
        return handle_user_name(message, history, state, timer)

    live_chat_request_received = message.lower() in ['mirror', 'mirror mirror']
    live_chat_exit_received = message.lower() in ['exit', 'goodbye', 'bye', 'done', 'end']

    if live_chat_request_received:
        return handle_live_chat_request(message, history, state, timer)

    history.append({'role': 'user', 'content': message})

    if state.is_live_chat and not live_chat_exit_received:
        result = telegram.send_message(message)
        logger.debug(f'Telegram API response: {type(result)} {result}')
        message_id = result.get('message_id')
        logger.debug(f'Adding new message id: {message_id}')
        state.message_ids.add(message_id)

        return '', history, state, gr.Timer(active=True)

    exit_live_chat = state.is_live_chat and live_chat_exit_received
    if exit_live_chat:
        return handle_live_chat_exit(message, history, state, timer)

    response, tools_used = chat_llm(context, message, history, state)

    metadata = {}
    if tools_used:
        metadata['title'] = '🛠️ Tools used: ' + ', '.join(tools_used)
    history.append({'role': 'assistant', 'content': response, 'metadata': metadata})

    return '', history, state, gr.Timer(active=False)


title = '🪞 Mirror'
with gr.Blocks(title=title, fill_height=True) as ui:
    state: Session | None = gr.State(None)
    gr.Markdown("""
    # Mirror 🪞

    ## Look closely into the mirror and you might just see 👀 me!
    """)

    chatbot = gr.Chatbot(
        value=[message_to_ask_for_name],
        type='messages',
        height='80vh',
        # resizable=True,
        group_consecutive_messages=False,
        avatar_images=[AVATARS_DIR / 'circle-user.svg', AVATARS_DIR / 'chatbot.svg'],
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
