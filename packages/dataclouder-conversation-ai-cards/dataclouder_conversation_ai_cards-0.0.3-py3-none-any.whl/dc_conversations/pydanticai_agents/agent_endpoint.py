from ..conversation_models import ConversationMessagesDTO
from .pydantic_ai_utils import get_model

from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter
from pydantic_ai import Agent




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix='/api/agents', tags=['agents'])


@router.post("/chat")
async def chat(conversation_messages_dto: ConversationMessagesDTO):
    print(conversation_messages_dto)
    model = get_model('groq')

    agent = Agent(  
        model,
        system_prompt='Be concise, reply with one sentence.'
    )

    result = await agent.run('Where does "hello world" come from?')

    print(result.data)

    return result.data

@router.get("/auth")
async def verify_token_uid():
    return {"status": "serving"}

