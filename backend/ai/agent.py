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

from typing import List, AsyncGenerator
from models.base import Message
from prompts.base import PromptFactory
from ai.llm import LLM, LLMFactory

class BaseAgent:
    def __init__(self, llm: LLM, system_message: str,  **kwargs):
        self.llm = llm
        self.system_message = system_message
        self.base_prompt = kwargs.get("base_prompt", None)
        self.tools = kwargs.get("tools", {})
    
    def prepare_chat(self, messages: List[Message] = [], args = {}) -> List[Message]:
        # Add system message to the chat
        chat = [Message(role="system", content=self.system_message)] + messages
        if self.base_prompt:
            chat.append(Message(role="system", content=self.base_prompt.compile(**args)))
        return chat

### Custom Agents
class ChatAgent(BaseAgent):
    def __init__(self):
        llm = LLMFactory.get_llm("default")
        system_message=PromptFactory.default_system_msg + PromptFactory.synapase_gen_instructions
        super().__init__(llm=llm, system_message=system_message.compile())
        
    def chat(self, messages: List[Message]) -> AsyncGenerator[str, None]:
        chat = self.prepare_chat(messages=messages)
        return self.llm.chat(messages=chat)

class QuestionGenerationAgent(BaseAgent):
    def __init__(self):
        llm = LLMFactory.get_llm("default")
        system_message=PromptFactory.default_system_msg + PromptFactory.synapase_gen_instructions
        system_message = system_message.compile()
        super().__init__(llm=llm, system_message=system_message)
        
    async def generate(self, messages: List[Message], num_of_questions, related = True) -> str:
        if related:
            self.base_prompt = PromptFactory.related_q_gen
        else:
            self.base_prompt = PromptFactory.integration_q_gen
        chat = self.prepare_chat(messages=messages, args={"num_of_questions": num_of_questions})
        result =  await self.llm.chat(messages=chat, stream=False, json_mode=True)
        return result
