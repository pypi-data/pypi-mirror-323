from typing import List, Optional, Literal, Callable
from pydantic.dataclasses import dataclass
from dataclasses import field
from .langgpt import langgpt

# Dataclass for tools used by llm
@dataclass
class BirbTool:
    name: str
    description: str
    function: Callable
    arguments: dict = field(default_factory={})
    required: list[str] = field(default_factory=[])

# Dataclass for system prompt template and variables
@dataclass
class BirbPrompt:
    name: str = "Birb"
    author: Optional[str] = None
    version: Optional[str] = "1.0"
    language: str = "English"
    description: str = "You are a helpful AI assistant."
    background: Optional[str] = None
    rules: Optional[List[str]] = None
    workflow: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    examples: Optional[List[dict[Literal["title", "text"], str]]] = None
    init_message: Optional[str] = "As a/an <Role>, you must follow the <Rules>, you must talk to user in default <Language>."
    template: Optional[str] = langgpt
