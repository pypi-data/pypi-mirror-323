from haystack.dataclasses import ChatMessage, ChatRole 
from typing import List 
from haystack import component
from jinja2 import Template
import tiktoken

# Trim message history based on max length
@component
class BufferTrimmer:
    def __init__(self, max_length: int, tiktoken_model: str = "gpt-4o") -> None:
        self.max_length = max_length
        self.encoder = tiktoken.encoding_for_model(tiktoken_model)
    @component.output_types(output=List[ChatMessage])
    def run(self, messages: List[ChatMessage]):
        # Trim
        n_tokens = 0
        for i in range(1, len(messages) + 1):
            text = messages[-i].text
            if not text: continue
            n_tokens += len(self.encoder.encode(text))
            if n_tokens > self.max_length:
                messages = messages[-i:]
                break
        # Ensure that buffer starts with user message
        start = 0
        for i, message in enumerate(messages):
            if message.is_from(ChatRole.USER):
                start = i
                break
        messages = messages[start:]
        return {"output": messages}

# Join multiple sequential user messages together
@component
class UserMessageJoiner:
    def __init__(self, multiuser: bool = False, template: str | None = None) -> None:
        self.multiuser = multiuser
        self.template = Template(template) if template else Template("{{name}}: {{text}}") 
    @component.output_types(output=List[ChatMessage])
    def run(self, messages: List[ChatMessage]):
        # Create a join mask
        mask: list[bool] = []
        for i, message in enumerate(messages):
            if i == 0 or not message.is_from(ChatRole.USER) or not message.text:
                mask.append(False)
            elif message.role == messages[i-1].role:
                if self.multiuser:
                    if messages[i-1].name == message.name:
                        mask.append(True)
                    else:
                        mask.append(False)
                else:
                    mask.append(True)
            else:
                mask.append(False)
        # Join messages
        new_messages = []
        for i, message in enumerate(messages):
            name = message.name if message.name else "User"
            if not mask[i]:
                new_message = message
                if i != len(mask) - 1 and mask[i+1]:
                    new_text = self.template.render(name=name, text=message.text)
                    new_message = ChatMessage.from_user(new_text, meta=message.meta)
                new_messages.append(new_message)
            else:
                new_text = self.template.render(name=name, text=message.text)
                new_text = f"{new_messages[-1].text}\n{new_text}"
                new_messages[-1] = ChatMessage.from_user(new_text, meta=new_messages[-1].meta)
        return {"output": new_messages}
