from typing import List
from models.base import Message

def pretty_print_chat(messages: List[Message]):
    for message in messages:
        if message.role == "user":
            print(f"{message.role}: {message.content}")
        else:
            print(f"{message.role}: \n{message.content}")