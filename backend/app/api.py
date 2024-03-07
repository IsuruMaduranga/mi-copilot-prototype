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

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from models.base import ChatRequest, ChatResponse, QuestionGenerationResponse
from ai.copilot import Copilot
from dotenv import load_dotenv

load_dotenv()

api = FastAPI()
copilot = Copilot()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.post("/code-gen-chat", response_model=ChatResponse)
async def code_gen_chat(request: ChatRequest, response: Response) -> ChatResponse:
    response.headers["Content-Type"] = "text/event-stream"
    return StreamingResponse(copilot.code_gen_chat(request.messages, request.context, request.num_questions))

@api.get("/question-gen", response_model=QuestionGenerationResponse)
async def question_gen_get(num_questions: int) -> QuestionGenerationResponse:
    return await copilot.generate_q([], {}, num_questions)

@api.post("/question-gen", response_model=QuestionGenerationResponse)
async def question_gen(request: ChatRequest, response: Response):
    return await copilot.generate_q(request.messages, request.context, request.num_questions)
