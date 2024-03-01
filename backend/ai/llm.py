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

from typing import AsyncGenerator, List
from openai import AsyncOpenAI
from models.base import Message
from prompts.base import PromptFactory
import toml

class LLM():
    def __init__(self, model: str, seed: int, temperature: float):
        self.llm  = AsyncOpenAI()
        self.model = model
        self.seed = seed
        self.temperature = temperature
        
    async def chat(self, messages: List[Message], stream: bool = True, **kwargs) -> AsyncGenerator[str, None] | str:
        response_format =  { "type": "json_object" if kwargs.get("json_mode", False) else "text"}
        res = await self.llm.chat.completions.create(
            model=self.model,
            seed=self.seed,
            temperature=self.temperature,
            messages=messages,
            stream=stream,
            response_format=response_format
        )
        
        async def chat_stream():
            async for chunk in res:
                yield chunk.choices[0].delta.content
        if stream:
            return chat_stream()
        else:
            return res.choices[0].message.content
    
class LLMFactory():
    @classmethod
    def get_llm(cls, name) -> LLM:
        with open("config.toml", "r") as f:
            config = toml.load(f)
        return LLM(
            model=config["llm"][name]["model"],
            seed=config["llm"][name]["seed"],
            temperature=config["llm"][name]["temperature"]
        )
