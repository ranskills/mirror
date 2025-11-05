from langchain.tools import tool
from pydantic import BaseModel, Field

from client import supabase


class LogUnansweredQuestionInput(BaseModel):
    session_id: str = Field(description='The ID for the active session')
    name: str = Field(description='The name of user')
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
