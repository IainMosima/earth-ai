from typing import Dict, Optional, Any, List

from pydantic import Field
from pydantic.v1 import BaseModel

# Request
class AIRequest(BaseModel):
    user_id: str
    aerial_key: str
    ground_key: str

class AerialResultOutput(BaseModel):
    content: str
    additional_kwargs: Dict[str, Any] = Field(default_factory=dict)
    response_metadata: Dict[str, Any] = Field(default_factory=dict)
    type: str
    name: Optional[str] = None
    id: str
    example: bool
    tool_calls: List[Any] = Field(default_factory=list)
    invalid_tool_calls: List[Any] = Field(default_factory=list)
    usage_metadata: Optional[Any] = None


class AerialResult(BaseModel):
    input: Dict[str, str]
    output: AerialResultOutput

# Response
class AIResponse(BaseModel):
    user_id: str
    aerial_result: AerialResult
    carbon_credits: float
