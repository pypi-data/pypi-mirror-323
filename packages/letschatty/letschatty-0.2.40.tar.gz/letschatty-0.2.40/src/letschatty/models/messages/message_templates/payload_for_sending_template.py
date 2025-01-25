from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from .template_for_frontend_use import ParametersFromFrontend
from .raw_meta_template import ComponentType

class NamedParameterForPayload(BaseModel):
    type: str = Field(default="text")
    parameter_name: str
    text: str
    
    @classmethod
    def from_template_parameters(cls, parameters: List[ParametersFromFrontend]) -> List[NamedParameterForPayload]:
        return [cls(type="text", parameter_name=parameter.id, text=parameter.text) for parameter in parameters]

class PositionalParameterForPayload(BaseModel):
    type: str = Field(default="text")
    text: str
    
    @classmethod
    def from_template_parameters(cls, parameters: List[ParametersFromFrontend]) -> List[PositionalParameterForPayload]:
        for i in range(len(parameters)):
            parameters[str(i)] = cls(type="text", text=parameters[i].text)
        return parameters

class ComponentForPayload(BaseModel):
    type: ComponentType
    parameters: List[NamedParameterForPayload | PositionalParameterForPayload]

class TemplateComponentForPayload(BaseModel):
    name: str
    language: dict 
    components: List[ComponentForPayload]

class TemplateRequestPayload(BaseModel):
    messaging_product: str = Field(default="whatsapp")
    recipient_type: str = Field(default="individual")
    to: str
    type: str = Field(default="template")
    template: TemplateComponentForPayload
