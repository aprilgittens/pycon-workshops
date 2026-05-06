from dotenv import load_dotenv
from os import environ
from langchain.globals import set_llm_cache
from langchain_openai import AzureChatOpenAI
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import AgentExecutor, create_openai_tools_agent
from service import TravelAgentTools as agent_tools

load_dotenv(override=False)


chat : AzureChatOpenAI | None=None
agent_with_chat_history : RunnableWithMessageHistory | None=None


def get_chat_client() -> AzureChatOpenAI:
    azure_endpoint = environ.get("AZURE_OPENAI_ENDPOINT")
    azure_api_key = environ.get("AZURE_OPENAI_API_KEY")
    azure_api_version = environ.get("AZURE_OPENAI_API_VERSION")
    azure_deployment = (
        environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
        or environ.get("AZURE_OPENAI_DEPLOYMENT")
    )

    missing = []
    if not azure_endpoint:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not azure_api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    if not azure_api_version:
        missing.append("AZURE_OPENAI_API_VERSION")
    if not azure_deployment:
        missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")

    if missing:
        missing_vars = ", ".join(missing)
        raise ValueError(
            f"Missing required Azure OpenAI settings: {missing_vars}. "
            "Set them in your environment or .env file before starting the API."
        )

    return AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=azure_api_version,
        azure_deployment=azure_deployment,
        temperature=0,
    )

def LLM_init():
    global chat,agent_with_chat_history
    chat = get_chat_client()
    tools = [agent_tools.vacation_lookup, agent_tools.itinerary_lookup, agent_tools.book_cruise ]

    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful and friendly travel assistant for a cruise company. Answer travel questions to the best of your ability providing only relevant information. In order to book a cruise you will need to capture the person's name.",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "Answer should be embedded in html tags. {input}"),
         MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
    )

    #Answer should be embedded in html tags. Only answer questions related to cruise travel, If you can not answer respond with \"I am here to assist with your travel questions.\". 


    agent = create_openai_tools_agent(chat, tools, prompt)
    agent_executor  = AgentExecutor(agent=agent, tools=tools, verbose=True)

    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: MongoDBChatMessageHistory( database_name="travel",
                                                 collection_name="history",
                                                   connection_string=environ.get("MONGO_CONNECTION_STRING"),
                                                   session_id=session_id),
        input_messages_key="input",
        history_messages_key="chat_history",
)

LLM_init()