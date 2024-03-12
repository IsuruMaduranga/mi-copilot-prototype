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
from jinja2 import Template
from copilot.models.base import Message
from copilot.prompts.base import PromptFactory
from copilot.ai.llm import LLM, LLMFactory
from copilot.ai.utils import pretty_print_chat

class BaseAgent:
    """
    Base class for all agents
    Create a new agent for each subtask
    """
    def __init__(self, **kwargs):
        # Don't mofify in runtime unless you want weird bugs
        self._llm = kwargs.get("llm", LLMFactory.get_default_llm())
        self._system_message = kwargs.get("system_message", PromptFactory.base_agent_system_msg)
        self._base_prompt = kwargs.get("base_prompt", None)
        self._tools = kwargs.get("tools", {})
    
    @property
    def llm(self) -> LLM:
        return self._llm
    
    @property
    def system_message(self) -> Template:
        return self._system_message
    
    @property
    def base_prompt(self) -> Template:
        return self._base_prompt
    
    @property
    def tools(self) -> dict:
        return self._tools
    
    def prepare_chat(self, messages: List[Message] = [], kwargs = {}) -> List[Message]:
        # Add system message to the chat
        chat = [Message(role="system", content=self.system_message.render())] + messages
        if self.base_prompt:
            chat.append(Message(role="user", content=self.base_prompt.render(**kwargs)))
        return chat
    
    def chat(self, messages: List[Message], prompt_args: dict = {}, llm_args: dict = {}, stream: bool = True ) -> AsyncGenerator[str, None]:
        chat = self.prepare_chat(messages=messages, kwargs=prompt_args)
        return self.llm.chat(messages=chat, stream=stream, **llm_args)

### Custom Agents
class ArtifactGenAgent(BaseAgent):
    def __init__(self):
        llm = LLMFactory.get_llm("codegen_chat")
        system_message = PromptFactory.code_gen_chat_system
        base_prompt = PromptFactory.code_gen_chat_base
        super().__init__(llm=llm, system_message=system_message, base_prompt=base_prompt)
        
    def chat(self, messages: List[Message], context: List[str]) -> AsyncGenerator[str, None]:
        prompt_args = {"question": messages[-1].content, "context": context}
        return super().chat(messages=messages[:-1], prompt_args=prompt_args)
    
class QGenAgent():
    pattern = re.compile(r'```xml(.*?)```', re.DOTALL)
    
    def __init__(self, **kwargs):
        llm = kwargs.get("llm", LLMFactory.get_llm("q_gen"))
        system_message = PromptFactory.q_gen_system_msg
        related_q_gen_prompt = PromptFactory.related_q_gen
        related_q_gen_context_prompt =  PromptFactory.related_q_gen_context
        integration_q_gen_prompt = PromptFactory.integration_q_gen
        
        # Create agents for each subtask
        self.related_q_gen_agent =  BaseAgent(llm=llm, system_message=system_message, base_prompt=related_q_gen_prompt)
        self.related_q_gen_context_agent = BaseAgent(llm=llm, system_message=system_message, base_prompt=related_q_gen_context_prompt)
        self.integration_q_gen_agent = BaseAgent(llm=llm, system_message=system_message, base_prompt=integration_q_gen_prompt)
        
    
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
        prompt_args = {"num_of_questions": num_of_questions, "context": context, "chat_history": self.prepare_messages(chat_history)}
        llm_args = {"json_mode": True}
        if context:
            return await self.related_q_gen_context_agent.chat(messages=[], prompt_args=prompt_args, llm_args=llm_args, stream=False)
        else:
            # Improvement: offload this to a separate thread if it takes too long
            xml = re.search(self.pattern, "\n".join([m.content for m in chat_history]))
            if xml:
                return await self.related_q_gen_agent.chat(messages=[], prompt_args=prompt_args, llm_args=llm_args, stream=False)
            else:
                return await self.integration_q_gen_agent.chat(messages=[], prompt_args=prompt_args, llm_args=llm_args, stream=False)

class CopilotChatAgent(BaseAgent):
    def __init__(self):
        llm = LLMFactory.get_llm("copilot_chat")
        system_message = PromptFactory.copilot_chat_system
        super().__init__(llm=llm, system_message=system_message)

class CopilotChatQGenAgent(BaseAgent):
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
        prompt_args = {"num_of_questions": num_of_questions, "context": context, "chat_history": self.prepare_messages(chat_history)}
        llm_args = {"json_mode": True}
        return await super().chat(messages=[], prompt_args=prompt_args, llm_args=llm_args, stream=False)

class ArtifactEditAgent(BaseAgent):
    def __init__(self):
        llm = LLMFactory.get_llm("artifact_edit_chat")
        system_message = PromptFactory.artifact_edit_system
        base_prompt = PromptFactory.artifact_edit_base
        super().__init__(llm=llm, system_message=system_message, base_prompt=base_prompt)
        
    def chat(self, messages: List[Message], context: List[str]) -> AsyncGenerator[str, None]:
        prompt_args = {"question": messages[-1].content, "file": context[0], "context": context[1:]}
        return super().chat(messages=messages[:-1], prompt_args=prompt_args)