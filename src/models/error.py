from pydantic import BaseModel


class Error(BaseModel):
    result: bool = False
    error_type: str
    error_message: str
