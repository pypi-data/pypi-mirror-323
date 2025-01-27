from pydantic import BaseModel


class QACheckResult(BaseModel):
    qa_check: str
    passed: bool
    object_id: str
    message: str
