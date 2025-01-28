from sqlalchemy import Column, String, Float, Integer, Text, JSON
from at_common_models.base import BaseModel

class PromptModel(BaseModel):
    """Model for storing system prompts and their associated parameters.
    
    Attributes:
        name: Unique identifier for the prompt
        sys_tpl: System template text
        usr_tpl: User template text
        param_temperature: Controls randomness (0-1)
        param_top_p: Controls nucleus sampling (0-1)
        param_top_k: Controls diversity of responses
        param_max_tokens: Maximum tokens in response
    """
    __tablename__ = "system_prompts"

    name = Column(String(255), primary_key=True, index=True)
    description = Column(String(1000), nullable=True)
    tags = Column(JSON, nullable=False, default=list)
    sys_tpl = Column(Text, nullable=False)
    usr_tpl = Column(Text, nullable=False)
    param_temperature = Column(Float, nullable=False, default=0.0)
    param_top_p = Column(Float, nullable=False, default=1.0)
    param_top_k = Column(Integer, nullable=False, default=10)
    param_max_tokens = Column(Integer, nullable=False, default=8196)