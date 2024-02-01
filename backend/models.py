from pydantic import BaseModel
from typing import Deque, Literal

class Message(BaseModel):
    role: Literal['system','user', 'assistant']
    content: str
    
class Chat(BaseModel):
    chat_history: Deque[Message]
