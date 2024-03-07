#####################################################################
#  Copyright (c) WSO2 LLC. (http://www.wso2.org) All Rights Reserved.
#
#  WSO2 LLC. licenses this file to you under the Apache License,
#  Version 2.0 (the "License"); you may not use this file except
#  in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#####################################################################

import re
from typing import List, AsyncGenerator
from models.base import Message
from prompts.base import PromptFactory
from ai.llm import LLM, LLMFactory
from ai.utils import pretty_print_chat

class BaseAgent:
    def __init__(self, **kwargs):
        self.llm = kwargs.get("llm", LLMFactory.get_default_llm())
        self.system_message = kwargs.get("system_message", PromptFactory.base_agent_system_msg)
        self.base_prompt = kwargs.get("base_prompt", None)
        self.tools = kwargs.get("tools", {})
    
    def prepare_chat(self, messages: List[Message] = [], kwargs = {}) -> List[Message]:
        # Add system message to the chat
        chat = [Message(role="system", content=self.system_message.render())] + messages
        if self.base_prompt:
            chat.append(Message(role="user", content=self.base_prompt.render(**kwargs)))
        return chat
    
    def chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        return self.llm.chat(messages=messages)

### Custom Agents
class ArtifactGenAgent(BaseAgent):
    def __init__(self):
        llm = LLMFactory.get_llm("codegen_chat")
        system_message = PromptFactory.code_gen_chat_system
        base_prompt = PromptFactory.code_gen_chat_base
        super().__init__(llm=llm, system_message=system_message, base_prompt=base_prompt)
        
    def chat(self, messages: List[Message], context: List[str]) -> AsyncGenerator[str, None]:
        chat = self.prepare_chat(messages=messages[:-1], kwargs={"question": messages[-1].content, "context": context})
        return super().chat(messages=chat)
    
class QGenAgent(BaseAgent):
    pattern = re.compile(r'```xml(.*?)```', re.DOTALL)
    
    def __init__(self, **kwargs):
        llm = kwargs.get("llm", LLMFactory.get_llm("q_gen"))
        system_message = kwargs.get("system_message", PromptFactory.q_gen_system_msg)
        base_prompt = kwargs.get("base_prompt", None)
        super().__init__(llm=llm, system_message=system_message, base_prompt=base_prompt)
    
    @staticmethod
    def prepare_messages(messages: List[Message]) -> str:
        m = ""
        for message in messages:
            l = ""
            if message.role == "user":
                l = "You: " + message.content
            elif message.role == "system":
                l = "AI: \n" + message.content
            m += l + "\n"
        return m
        
    async def generate(self, chat_history: List[Message] = [], context: List[str] = [], num_of_questions = 1) -> str:
        if context:
            self.base_prompt = PromptFactory.related_q_gen_context
        else:
            # Improvement: offload this to a separate thread if it takes too long
            xml = re.search(self.pattern, "\n".join([m.content for m in chat_history]))
            if xml:
                self.base_prompt = PromptFactory.related_q_gen
            else:
                self.base_prompt = PromptFactory.integration_q_gen
        chat = self.prepare_chat(messages=[], kwargs={"num_of_questions": num_of_questions, "context": context, "chat_history": self.prepare_messages(chat_history)})
        result =  await self.llm.chat(messages=chat, stream=False, json_mode=True)
        return result

class CopilotChatAgent(BaseAgent):
    def __init__(self):
        llm = LLMFactory.get_llm("copilot_chat")
        system_message = PromptFactory.copilot_chat_system
        super().__init__(llm=llm, system_message=system_message)
    
    def chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        chat = self.prepare_chat(messages=messages)
        return super().chat(messages=chat)

class CopilotChatQGenAgent(QGenAgent):
    def __init__(self, **kwargs):
        llm = kwargs.get("llm", LLMFactory.get_llm("q_gen"))
        system_message = kwargs.get("system_message", PromptFactory.copilot_q_gen_system)
        base_prompt = kwargs.get("base_prompt", PromptFactory.copilot_q_gen_base)
        super().__init__(llm=llm, system_message=system_message, base_prompt=base_prompt)
    
    @staticmethod
    def prepare_messages(messages: List[Message]) -> str:
        m = ""
        for message in messages:
            l = ""
            if message.role == "user":
                l = "You: " + message.content
            elif message.role == "system":
                l = "AI: \n" + message.content
            m += l + "\n"
        return m
        
    async def generate(self, chat_history: List[Message] = [], context: List[str] = [], num_of_questions = 1) -> str:
        chat = self.prepare_chat(messages=[], kwargs={"num_of_questions": num_of_questions, "context": context, "chat_history": self.prepare_messages(chat_history)})
        return await self.llm.chat(messages=chat, stream=False, json_mode=True)
