from enum import Enum
import json
from pydantic import BaseModel, Field
from pathlib import Path
from uuid import uuid4
from typing import Any, Dict, Optional, Union

class MessageType(Enum):
    system = "system"
    human = "human"
    gini = "gini"
    tool = "tool"
    error = "error"


class Attachment(BaseModel):
    name: str
    id: str = Field(default_factory=lambda: str(uuid4()))
    localPath: Optional[str] = None
    base64: Optional[str] = None
    
    @classmethod
    def from_path(cls, file_path: str) -> "Attachment":
        # Ensure the file exists
        path = Path(file_path).resolve()  # Convert to absolute path
        if not path.exists():
            raise FileNotFoundError(f"File not found at path: {path}")

        return cls(
            name=path.name,
            localPath=str(path)  # Convert absolute Path to string
        )



class GiniRequest(BaseModel):
    action: str
    data: Dict[str, Any]
    
    def json(self) -> str:
        """Convert the request to a JSON string"""
        return json.dumps({
            "action": self.action,
            "data": self.data
        })


class GiniResponse(BaseModel):
    response: Union[Dict[str, Any], str]
