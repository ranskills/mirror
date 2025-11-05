import uuid
from typing import TypeAlias
from dataclasses import dataclass, field


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