from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator
from ...base_models.chatty_asset_model import ChattyAssetModel
from ...utils.types.identifier import StrObjectId
from ...utils.definitions import Area
from ...utils.types.serializer_type import SerializerType
from bson import ObjectId
from zoneinfo import ZoneInfo
import logging
from enum import StrEnum
logger = logging.getLogger(__name__)

class CampaignStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    INCOMPLETE = "INCOMPLETE"
    ERROR = "ERROR"

class TemplateCampaign(ChattyAssetModel):
    template_name: str
    campaign_name: str
    area: Area
    agent_email: str
    recipients: List[Dict[str, str]]
    assign_to_agent: Optional[str] = None
    parameters: List[str] = Field(default_factory=list)
    tags: List[StrObjectId] = Field(default_factory=list)
    products: List[StrObjectId] = Field(default_factory=list)
    flow: List[StrObjectId] = Field(default_factory=list)
    description: Optional[str] = None
    forced_send: bool = Field(default=False)
    date: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    q_recipients: Optional[int] = None
    q_processed_recipients: int = 0
    q_recipients_succesfully_sent: int = 0
    status: CampaignStatus = Field(default=CampaignStatus.PENDING)
    progress: float = 0.0
    
    exclude_fields = {
        SerializerType.FRONTEND_ASSET_PREVIEW: {"recipients", "tags", "products", "flow", "agent_email", "assign_to_agent", "parameters", "description", "forced_send"}
    }

        
    class ConfigDict:
        arbitrary_types_allowed = True
                

    @field_validator('recipients')
    def validate_recipients(cls, v):
        if len(v) == 0:
            raise ValueError("No recipients specified")
        return v

    @field_validator('q_recipients')
    def set_q_recipients(cls, v, values):
        if v is None:
            return len(values.data.get('recipients', []))
        return v

    def pause(self):
        if self.status in [CampaignStatus.PROCESSING, CampaignStatus.PENDING]:
            self.status = CampaignStatus.PAUSED
        else:
            raise ValueError(f"Campaign {self.campaign_name} can't be paused because its status is {self.status}")

    def is_processing(self):
        return self.status == CampaignStatus.PROCESSING

    def resume(self):
        logger.info(f"Resuming campaign {self.campaign_name} status {self.status}")
        if self.status in [CampaignStatus.PAUSED, CampaignStatus.INCOMPLETE]:
            self.status = CampaignStatus.PROCESSING
        else:
            raise ValueError(f"Campaign {self.campaign_name} can't be resumed because its status is {self.status}")
    
    def start_processing(self):
        if self.status == CampaignStatus.PENDING:
            self.status = CampaignStatus.PROCESSING
        else: 
            raise ValueError(f"Campaign {self.campaign_name} can't be started because its status is {self.status}")

    def finish(self):
        if self.status != CampaignStatus.PROCESSING:
            raise ValueError(f"Campaign {self.campaign_name} can't be finished because its status is {self.status}")
        
        self.status = CampaignStatus.COMPLETED if self.q_recipients == self.q_processed_recipients else CampaignStatus.INCOMPLETE

    def error(self):
        self.status = CampaignStatus.ERROR
