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
from typing import List, AsyncGenerator
from ai.agent import ChatAgent, QuestionGenerationAgent
from models.base import Message, ChatResponse, Event, QuestionGenerationResponse

class Copilot():
    
    def __init__(self):
        # Creating agents
        self.chat_agent = ChatAgent()
        self.question_agent = QuestionGenerationAgent()
        
    async def code_gen_chat(self, messages: List[Message], context: List[str], num_predicted_questions: int) -> AsyncGenerator[ChatResponse, None]:
        response = ""
        async for chunk in await self.chat_agent.chat(messages, context=context):
            if(chunk):
                response += chunk
                yield ChatResponse(content=chunk, event=Event.CHAT_GENERATING).model_dump_json() + "\n"
        messages.append(Message(role="system", content=response))
        try:
            q = await self.question_agent.generate(messages, context, num_predicted_questions)
            parsed_q = json.loads(q)["questions"]
        except:
            yield ChatResponse(questions=[], event=Event.QUESTION_GENERATION_ERROR).model_dump_json() + "\n"
        else:
            yield ChatResponse(questions=parsed_q, event=Event.QUESTION_GENERATION_SUCCESS).model_dump_json() + "\n"
    
    async def generate_q(self,  messages: List[Message], context: List[str], num_predicted_questions: int) -> QuestionGenerationResponse:
        try:
            q = await self.question_agent.generate(messages, context, num_predicted_questions)
            parsed_q = json.loads(q)["questions"]
        except:
            return QuestionGenerationResponse(questions=[], event=Event.QUESTION_GENERATION_ERROR)
        else:
            return QuestionGenerationResponse(questions=parsed_q, event=Event.QUESTION_GENERATION_SUCCESS)
