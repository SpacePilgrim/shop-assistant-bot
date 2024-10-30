from agents import triage_agent
from full_turn import run_full_turn

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
