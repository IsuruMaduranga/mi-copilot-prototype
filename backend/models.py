from pydantic import BaseModel
from typing import List, Literal

class Message(BaseModel):
    role: Literal['system','user', 'assistant']
    content: str
    
class Chat(BaseModel):
    chat_history: List[Message]
