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

from models.base import Template
from typing import Self
from jinja2 import Environment, FileSystemLoader, Template
    
class PromptTemplateStorage():
    @classmethod
    def load_from_storage(cls, name: str) -> Template:
        env = Environment(loader=FileSystemLoader('prompts/storage'))
        return env.get_template(f"{name}.j2")

class PromptFactory():
    default_system_msg = PromptTemplateStorage.load_from_storage("system_v3")
    synapase_gen_instructions = PromptTemplateStorage.load_from_storage("synapse_generation_instructions")
    related_q_gen = PromptTemplateStorage.load_from_storage("related_question_generation")
    integration_q_gen = PromptTemplateStorage.load_from_storage("integration_question_generation")
