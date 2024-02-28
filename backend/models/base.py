from enum import Enum
from pydantic import BaseModel
from typing import List, Literal, Optional

class Event(Enum):
    QUESTION_GENERATION_ERROR = "question_generation_error"
    QUESTION_GENERATION_SUCCESS = "question_generation_success"
    CHAT_GENERATING = "chat_generating"
    CHAT_ERROR = "chat_error"
    CHAT_SUCCESS = "chat_success"
    
class Error(BaseModel):
    error: str

class Message(BaseModel):
    role: Literal['system','user', 'assistant']
    content: str
    
class ChatResponse(BaseModel):
    event: Event
    error: Error = None
    content: str = None
    questions: List[str] = []
    
class ChatRequest(BaseModel):
    messages: List[Message]
    context: Optional[List[str]]
    
class Template(BaseModel):
    template: str
