from pydantic import BaseModel, Field


class PounceState(BaseModel):
    task_id: str = Field(default='')
    user_message: str = Field(default='')
    report_path: str = Field(default='')
