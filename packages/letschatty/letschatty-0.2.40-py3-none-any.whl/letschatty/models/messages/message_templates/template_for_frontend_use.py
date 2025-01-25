from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field, model_validator
from ...utils.definitions import Area
from .chatty_template_campaign import TemplateCampaign
from ...utils.types.identifier import StrObjectId
import logging

logger = logging.getLogger(__name__)

class ParameterFormForFrontend(BaseModel):
    id: str
    example: str
    
class TemplateFormForFrontend(BaseModel):
    name: str
    text: str
    parameters: List[ParameterFormForFrontend]


class ParametersFromFrontend(BaseModel):
    id: str
    text: str
    
class TemplateDataFromFrontend(BaseModel):
    template_name: str
    area: Area
    agent_email: str
    assign_to_agent: str | None = None
    phone_number: str | None = None
    new_contact_name: str | None = None
    parameters: List[ParametersFromFrontend] = Field(default_factory=list)
    tags: List[StrObjectId] = Field(default_factory=list)
    products: List[StrObjectId] = Field(default_factory=list)
    flow: List[StrObjectId] = Field(default_factory=list)
    description: str | None = None
    forced_send: bool = False
    lenguage: str | None = None
    campaign_name: str | None = None
    campaign_id: StrObjectId | None = None
    body: str | None = None
    
    
    @model_validator(mode='after')
    def validate_template_data(self) -> dict:
  
        if self.area == Area.WITH_AGENT and not self.assign_to_agent:
            # TEMPORARY FIX FOR AGENT ASSIGNMENT: IF IT'S NOT SPECIFIED, ASSIGN TO THE AGENT EMAIL
            raise ValueError("Agent assignment must be specified for WITH AGENT area")

        if not self.phone_number:
            logger.warning("Phone number must be specified for single recipient")
            raise ValueError("Phone number must be specified for single recipient")

        self.phone_number = str(self.phone_number)

        if not self.new_contact_name:
            self.new_contact_name = self.phone_number

        return self

    @classmethod
    def from_campaign(cls, campaign: TemplateCampaign, recipient_data : dict) -> TemplateDataFromFrontend:
        phone_number :str = str(recipient_data.get("phone_number"))
        new_contact_name : str = recipient_data.get("name", phone_number)
        return cls(
            template_name=campaign.template_name,
            area=campaign.area,
            agent_email=campaign.agent_email,
            assign_to_agent=campaign.assign_to_agent,
            phone_number=phone_number,
            new_contact_name=new_contact_name,
            parameters=campaign.parameters,
            tags=campaign.tags,
            products=campaign.products,
            flow=campaign.flow,
            description=campaign.description,
            forced_send=campaign.forced_send,
            campaign_name=campaign.campaign_name,
            campaign_id=campaign._id
            
        )