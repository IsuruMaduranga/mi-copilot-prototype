from models.base import Template, Message
from typing import Self, List

class PromptTemplate(Template):
    def compile(self, **kwargs) -> str:
        return self.template.format(**kwargs)
    
    def __add__(self, other: Self) -> Self:
        return PromptTemplate(template=self.template + "\n" + other.template)
    
class PromptTemplateStorage():
    @classmethod
    def load_from_storage(cls, name: str) -> PromptTemplate:
        with open(f"prompts/storage/{name}.prompt", "r") as f:
            template = f.read()
        return PromptTemplate(template=template)
    
    @classmethod
    def get(cls, name: str, **kwargs) -> str:
        return cls.load_from_storage(name).compile(**kwargs)

class PromptFactory():
    default_system_msg = PromptTemplateStorage.load_from_storage("system_v3")
    synapase_gen_instructions = PromptTemplateStorage.load_from_storage("synapse_generation_instructions")
    related_q_gen = PromptTemplateStorage.load_from_storage("related_question_generation")
    integration_q_gen = PromptTemplateStorage.load_from_storage("integration_question_generation")
