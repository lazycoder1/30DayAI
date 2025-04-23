from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from utils import remove_think_from_string
model = init_chat_model("deepseek-r1:8b", model_provider="ollama")




messages = [
    SystemMessage("You are a sarcastic teenager , that uses curse words with every message."),
    HumanMessage("Hello, how the fuck are you?")
]

response = model.invoke(messages)

print(remove_think_from_string(response.content))
