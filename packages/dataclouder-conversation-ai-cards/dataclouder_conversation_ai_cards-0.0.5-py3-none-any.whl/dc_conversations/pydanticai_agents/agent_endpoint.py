from typing import List
from ..conversation_models import ChatResponseDTO, ConversationMessagesDTO, ChatRole, LLMProvider, ListModelsResponse
from .pydantic_ai_utils import get_model

from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
    SystemPromptPart
)

from pydantic_ai.models.gemini import  GeminiModelName
from pydantic_ai.models.openai import  ChatModel
from pydantic_ai.models.groq import  GroqModelName
from pydantic_ai.models.anthropic import  LatestAnthropicModelNames



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix='/api/agent', tags=['agents'])


@router.get("/list_models")
async def get_model_names(provider: LLMProvider) -> List[ListModelsResponse]:
    if provider == LLMProvider.OpenAI:
        names = ChatModel.__args__
        return [ListModelsResponse(name=name, id=name) for name in names]
    elif provider == LLMProvider.Google:
        names = GeminiModelName.__args__
        return [ListModelsResponse(name=name, id=name) for name in names]
    elif provider == LLMProvider.OpenRouter:
        names = ['model_name', 'someothermode', 'testmodel']
        return [ListModelsResponse(name=name, id=name) for name in names]
    elif provider == LLMProvider.Groq:
        names = GroqModelName.__args__
        return [ListModelsResponse(name=name, id=name) for name in names]
    elif provider == LLMProvider.Anthropic:
        names = LatestAnthropicModelNames.__args__
        return [ListModelsResponse(name=name, id=name) for name in names]
    else:
        raise ValueError(f"Provider {provider} not supported")


@router.post("/chat")
async def chat(conversation_messages_dto: ConversationMessagesDTO) -> ChatResponseDTO:
    print(conversation_messages_dto)
    provider = conversation_messages_dto.provider or 'groq'
    model = conversation_messages_dto.modelName or None

    model = get_model(provider, model)
    
    # Extract system messages and combine them into a single prompt
    system_messages = [msg.content for msg in conversation_messages_dto.messages or [] if msg.role == "system"]
    system_prompt = "\n".join(system_messages) if system_messages else "You are a helpful assistant."
    
    # Create agent with system prompt
    agent = Agent( model, system_prompt=system_prompt)
    
    # Get the last user message or use a default
    user_messages = [msg for msg in conversation_messages_dto.messages or []  if msg.role == "user"]
    user_prompt = user_messages[-1].content if user_messages else "Hello"
    
    # Convert messages to proper ModelMessage format
    message_history = []
    for msg in (conversation_messages_dto.messages or [])[:-1]:  # Exclude last user message
        if msg.role == "system":
            message_history.append(ModelRequest(parts=[ SystemPromptPart(content=msg.content)]))
        elif msg.role == "user":
            message_history.append(ModelRequest(parts=[ UserPromptPart(content=msg.content) ]))
        elif msg.role == "assistant":
            message_history.append(ModelResponse(parts=[TextPart(content=msg.content)]))
    # What i can see this version create the whole conversation like chatgpt, so not sure if i'm adding more value. 
    
    # Run the agent with history if available
    if message_history:
        result = await agent.run(user_prompt, message_history=message_history)
    else:
        result = await agent.run(user_prompt)

    return ChatResponseDTO(role=ChatRole.Assistant, content=result.data, metadata={})



