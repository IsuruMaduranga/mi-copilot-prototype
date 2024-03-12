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

import json
import logging
from typing import List, AsyncGenerator
from . agent import ArtifactGenAgent, QGenAgent, CopilotChatAgent, CopilotChatQGenAgent, ArtifactEditAgent
from .. models.base import Message, ChatResponse, Event, SuggestionResponse

class Copilot():
    
    def __init__(self):
        # Creating agents
        self.artifact_gen_agent = ArtifactGenAgent()
        self.q_gen_agent = QGenAgent()
        self.copilot_chat_agent = CopilotChatAgent()
        self.copilot_chat_q_gen_agent = CopilotChatQGenAgent()
        self.artifact_edit_agent = ArtifactEditAgent()
        
    async def code_gen_chat(self, messages: List[Message], context: List[str], num_predicted_questions: int) -> AsyncGenerator[ChatResponse, None]:
        response = ""
        async for chunk in await self.artifact_gen_agent.chat(messages, context=context):
            if(chunk):
                response += chunk
                yield ChatResponse(content=chunk, event=Event.CHAT_GENERATING).model_dump_json() + "\n"
        yield ChatResponse(content="", event=Event.CHAT_SUCCESS).model_dump_json() + "\n"
        messages.append(Message(role="assistant", content=response))
        try:
            q = await self.q_gen_agent.generate(messages, context, num_predicted_questions)
            parsed_q = json.loads(q)["questions"]
        except Exception as e:
            logging.error(e)
            yield ChatResponse(questions=[], event=Event.SUGGESTION_GENERATION_ERROR).model_dump_json() + "\n"
        else:
            yield ChatResponse(questions=parsed_q, event=Event.SUGGESTION_GENERATION_SUCCESS).model_dump_json() + "\n"
    
    async def generate_q(self,  messages: List[Message], context: List[str], num_predicted_questions: int, q_type: str) -> SuggestionResponse:
        try:
            if q_type == "copilot_chat":
                q = await self.copilot_chat_q_gen_agent.generate(messages, context, num_predicted_questions)
            else:
                q = await self.q_gen_agent.generate(messages, context, num_predicted_questions)
            parsed_q = json.loads(q)["questions"]
        except Exception as e:
            logging.error(e)
            return SuggestionResponse(questions=[], event=Event.SUGGESTION_GENERATION_ERROR)
        else:
            return SuggestionResponse(questions=parsed_q, event=Event.SUGGESTION_GENERATION_SUCCESS)
        
    async def chat(self, messages: List[Message], ) -> AsyncGenerator[ChatResponse, None]:
        response = ""
        async for chunk in await self.copilot_chat_agent.chat(messages):
            if(chunk):
                response += chunk
                yield ChatResponse(content=chunk, event=Event.CHAT_GENERATING).model_dump_json() + "\n"
        messages.append(Message(role="assistant", content=response))
        yield ChatResponse(content="", event=Event.CHAT_SUCCESS).model_dump_json() + "\n"
        try:
            q = await self.copilot_chat_q_gen_agent.generate(messages, [], 1)
            parsed_q = json.loads(q)["questions"]
        except Exception as e:
            logging.error(e)
            yield ChatResponse(questions=[], event=Event.SUGGESTION_GENERATION_ERROR).model_dump_json() + "\n"
        else:
            yield ChatResponse(questions=parsed_q, event=Event.SUGGESTION_GENERATION_SUCCESS).model_dump_json() + "\n"
    
    async def artifact_edit_chat(self, messages: List[Message], context: List[str]) -> AsyncGenerator[ChatResponse, None]:
        async for chunk in await self.artifact_edit_agent.chat(messages, context):
            if(chunk):
                yield ChatResponse(content=chunk, event=Event.CHAT_GENERATING).model_dump_json() + "\n"
        yield ChatResponse(content="", event=Event.CHAT_SUCCESS).model_dump_json() + "\n"
        
        # Generate questions
        yield ChatResponse(questions=["Test question"], event=Event.SUGGESTION_GENERATION_SUCCESS).model_dump_json() + "\n"
        