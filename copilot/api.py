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

import functools
import asyncio
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from copilot.models.base import ChatRequest, ChatResponse, SuggestionResponse, SuggestionRequest
from copilot.ai.copilot import Copilot
import yaml
import io
from dotenv import load_dotenv

load_dotenv()

api = FastAPI(
    title="WSO2 MI Copilot",
    description="Backend for WSO2 MI Copilot VSCode Extension",
    version="0.1.0",
    license_info={"name": "Apache 2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0"}
)
api.openapi_version = "3.0.2"

copilot = Copilot()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# additional yaml version of openapi.json
@api.get('/openapi.yaml', include_in_schema=False)
@functools.lru_cache()
def read_openapi_yaml() -> Response:
    openapi_json= api.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type='text/yaml')

async def stream_numbers(count: int):
    counter = 0
    while True:
        yield f"data: {counter}\n\n"
        counter += 1
        if counter == count:
            break
        await asyncio.sleep(0.1)

@api.get("/health")
async def health():
    return {"status": "ok"}

@api.get("/health/stream", description="Streaming endpoint for load testing")
async def health_stream(count: int,response: Response):
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    return StreamingResponse(stream_numbers(count), media_type='text/event-stream')
        
@api.post("/chat/artifact-generation", response_model=ChatResponse, operation_id="artifact_gen_chat", tags=["generation"])
async def artifact_gen_chat(request: ChatRequest, response: Response) -> ChatResponse:
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    return StreamingResponse(copilot.code_gen_chat(request.messages, request.context, request.num_suggestions))

@api.get("/suggestions/initial", response_model=SuggestionResponse, operation_id="initial_suggestions", tags=["suggestions"])
async def initial_suggestions(num_suggestions: int, q_type: str, response: Response) -> SuggestionResponse:
    response.headers["Cache-Control"] = "no-cache"
    return await copilot.generate_q([], {}, num_suggestions, q_type)

@api.post("/suggestions", response_model=SuggestionResponse, operation_id="suggestions", tags=["suggestions"])
async def suggestions(request: SuggestionRequest, response: Response):
    response.headers["Cache-Control"] = "no-cache"
    return await copilot.generate_q(request.messages, request.context, request.num_suggestions, request.type)

@api.post("/chat/copilot", response_model=ChatResponse, operation_id="copilot_chat", tags=["chat"])
async def copilt_chat(request: ChatRequest, response: Response, operation_id="copilt_chat"):
    response.headers["Cache-Control"] = "no-cache"
    return StreamingResponse(copilot.chat(request.messages))

@api.post("/chat/artifact-editing", response_model=ChatResponse, operation_id="artifact_edit_chat", tags=["generation"])
async def artifact_edit_chat(request: ChatRequest, response: Response) -> ChatResponse:
    response.headers["Content-Type"] = "text/event-stream"
    response.headers["Cache-Control"] = "no-cache"
    return StreamingResponse(copilot.artifact_edit_chat(request.messages, request.context))
