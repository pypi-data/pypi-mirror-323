from sqlalchemy import Column, String, JSON
from at_common_models.base import BaseModel

class WorkflowModel(BaseModel):
    __tablename__ = "system_workflows"

    name = Column(String(255), primary_key=True, index=True)
    tags = Column(JSON, nullable=False, default=list)
    data = Column(JSON, nullable=False)