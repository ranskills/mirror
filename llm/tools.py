from langchain.tools import tool
from pydantic import BaseModel, Field

from common import get_settings
from client import supabase, create_telegram_client, send_pushover_notificaiton


settings = get_settings()


class SessionDetails(BaseModel):
    session_id: str = Field(description='The ID for the active session')
    name: str = Field(description='The name of user')


class LogUnansweredQuestionInput(SessionDetails):
    question: str = Field(description='The question that was not answered')


@tool(args_schema=LogUnansweredQuestionInput)
def log_unanswered_question(session_id, name, question):
    """Log questions that are not answered for later review to improve the system"""
    print(f'I do not have an answer for the question: {session_id} | {name} | {question}')

    data = {
        'session_id': session_id,
        'user': name,
        'question': question,
    }

    try:
        response = supabase.table('unanswered_questions').insert(data).execute()

        print(response)
    except Exception as e:
        print(f'Error logging unanswered question: {e}')

    try:
        telegram = create_telegram_client()
        telegram.send_message(
            f'Unanswered Question from {name} (Session: {session_id}): {question}'
        )
    except Exception as e:
        print(f'Error sending telegram message: {e}')


class RecordUserDetails(SessionDetails):
    email: str = Field(description='The email of the user')
    notes: str = Field(
        description="additional information about the conversation that's worth recording to give context"
    )


@tool(args_schema=RecordUserDetails)
def record_user_details(session_id, name, email, notes):
    """Record user details for future reference. Email to be collected and no phone numbers"""
    print(f'Recording user details: {session_id} | {name} | {email}')

    data = {
        'session_id': session_id,
        'user': name,
        'email': email,
        'notes': notes,
    }

    try:
        response = supabase.table('user_details').insert(data).execute()

        print(response)
    except Exception as e:
        print(f'Error recording user details: {e}')


class PushNoticiationInput(BaseModel):
    message: str = Field(description='The message to send')


@tool(args_schema=PushNoticiationInput)
def send_push_notification(message: str):
    """Send push notification"""
    return send_pushover_notificaiton(message)
