from typing import List, Optional 
from haystack.dataclasses import ChatMessage, ChatRole
from haystack.tools import Tool
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.tools import ToolInvoker
from haystack.utils import Secret
from jinja2 import Template
from dataclasses import asdict
import logging
import json
from .models import BirbTool, BirbPrompt
from .components import UserMessageJoiner, BufferTrimmer
logger = logging.getLogger("BirbTalk")

# Default BirbTalk class with short-term memory buffer and tools 
class BirbTalk:
    def __init__(self,
                 api_key: Optional[str] = None,
                 api_url: Optional[str] = None,
                 model: str = "gpt-4o",
                 system_prompt: BirbPrompt | None = None,
                 buffer_size: int = 512,
                 multiuser: bool = False,
                 tools_strict: bool = True,
                 temperature: float = 1.0,
                 chat_id: Optional[str] = None,
                 tools: List[BirbTool] = [],
                 ):
        assert api_key, "Api key is required"
        self.chat_id = chat_id
        self.buffer = []
        # Generate system message
        system_prompt = system_prompt if system_prompt else BirbPrompt()
        self.system_prompt = Template(system_prompt.template).render(**asdict(system_prompt))
        self.system_message = ChatMessage.from_system(self.system_prompt)
        # Convert BirbTools to haystack tools
        self.tools = [Tool(
            name=x.name,
            description=x.description,
            function=x.function,
            parameters={
                "type": "object",
                "properties": x.arguments,
                "required": x.required,
            }
        ) for x in tools]
        # Initialize components
        self.message_joiner = UserMessageJoiner(multiuser=multiuser)
        self.generator = OpenAIChatGenerator(
            api_key = Secret.from_token(api_key),
            api_base_url = api_url, 
            model = model, 
            generation_kwargs = {
                "temperature": temperature
            },
            tools_strict = tools_strict
        )
        self.invoker = ToolInvoker(tools = self.tools) if self.tools else None
        self.trimmer = BufferTrimmer(max_length=buffer_size)

    # Generate chat completion
    def generate(self, prompt: str, name: str = "User"):
        # Trim buffer
        self.buffer = self.trimmer.run(messages=self.buffer)["output"]
        # Add user message to buffer
        self.buffer.append(ChatMessage.from_user(prompt, name=name))
        # Construct and pre-process message list
        messages = [self.system_message] + self.buffer
        messages = self.message_joiner.run(messages)["output"]
        # Generate first reply
        messages += self.generator.run(messages=messages, tools=self.tools)["replies"]
        # Process tool calls
        if len(messages[-1].tool_calls) > 0 and self.invoker:
            # Add chat id to tool call
            if self.chat_id:
                for i in range(len(messages[-1].tool_calls)):
                    messages[-1].tool_calls[i].arguments["chat_id"] = self.chat_id
            # Call tools and save results
            messages += self.invoker.run(messages=messages)["tool_messages"]
            # Generate new reply
            messages += self.generator.run(messages=messages)["replies"]
        # Add assistant reply to the buffer
        self.buffer.append(messages[-1])
        # Print debug message and return reply text
        self.debug(messages)
        return messages[-1].text
    
    # Pretty-print context
    def debug(self, messages):
        debug_text = []
        for message in messages:
            text = message.text
            if len(message.tool_calls) > 0:
                text = json.dumps(message.to_openai_dict_format())
            elif message.is_from(ChatRole.TOOL):
                text = f'{message._role.value}: {json.dumps(message.tool_call_result.result)}'
            elif not message.is_from(ChatRole.SYSTEM):
                text = f'{message._role.value}: {message.text}'
            debug_text.append(text)
        debug_text = "\n\n".join(debug_text)
        logger.debug(f"\n{debug_text}")
    
    # Dump buffer in openai format
    def dump_buffer(self):
        return [x.to_openai_dict_format() for x in self.buffer]
    
    # Load buffer from openai format
    def load_buffer(self, buffer: List[dict]):
        self.buffer = [ChatMessage.from_openai_dict_format(x) for x in buffer]

