from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.openai_functions import create_structured_output_chain
from pydantic import BaseModel
from config import openai_api_key

TOPIC = "인공지능은 인간의 창의성을 넘어설 수 있는가?"

class DebateResponse(BaseModel):
    respond: str
    mind: str

debater_prompt = PromptTemplate(
    input_variables=["topic", "chat_history", "mind"],
    template="""
당신은 열정적인 토론자입니다.

주제: "{topic}"
접근 관점 (mind): "{mind}"

지금까지의 대화:
{chat_history}

위의 관점(mind)을 바탕으로, 이 주제에 대해 논리적으로 반응(respond)하십시오.
아래 형식으로 JSON으로 출력하십시오:

{{
  "respond": "...당신의 주장...",
  "mind": "...이 주장에 담긴 전략/사고 방식 요약..."
}}
"""
)

moderator_prompt = PromptTemplate(
    input_variables=["topic", "chat_history"],
    template="""
당신은 중립적인 중재자입니다.
주제: "{topic}"

{chat_history}

간략하게 요약하고 다음 발언자를 지목해주세요.
"""
)

def create_debate_chains(num_debaters=2):
    chains = []
    memories = []
    for _ in range(num_debaters):
        llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, openai_api_key=openai_api_key)
        memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
        chain = create_structured_output_chain(output_schema=DebateResponse, llm=llm, prompt=debater_prompt)
        chains.append(chain)
        memories.append(memory)
    return chains, memories

def create_moderator_chain():
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=openai_api_key)
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    chain = create_structured_output_chain(output_schema=DebateResponse, llm=llm, prompt=moderator_prompt)
    return chain, memory
