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

from enum import Enum
from pydantic import BaseModel
from typing import List, Literal, Optional

class Event(Enum):
    SUGGESTION_GENERATION_ERROR = "suggestion_generation_error"
    SUGGESTION_GENERATION_SUCCESS = "suggestion_generation_success"
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
    context: Optional[List[str]] = None
    num_suggestions: Optional[int] = 1
    
class SuggestionRequest(BaseModel):
    messages: List[Message]
    context: Optional[List[str]] = None
    num_suggestions: Optional[int] = 1
    type: Literal['artifact_gen', 'copilot_chat']
    
class SuggestionResponse(BaseModel):
    event: Event
    error: Error = None
    questions: List[str]
