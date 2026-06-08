from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

openai = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0
)