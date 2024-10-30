from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from func_to_scheme import function_to_schema
from avail_funcs import tools, execute_tool_call
from agents import triage_agent
from full_turn import run_full_turn


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

agent = triage_agent
messages = []
while True:
    user = input("Пользователь: ")
    if user == "stop":
      break
    else:
      messages.append({"role": "user", "content": user})
      response = run_full_turn(agent, messages)
      agent = response.agent
      messages.extend(response.messages)
