from agents import Agent, Response
from avail_funcs import execute_tool_call, tools
from func_to_scheme import function_to_schema
from main import client

def run_full_turn(agent, messages):
    current_agent = agent
    num_init_messages = len(messages)
    messages = messages.copy()

    while True:

        # Превращаем функции python в инструменты и сохраняем их в map
        tool_schemas = [function_to_schema(tool) for tool in tools]
        tools_map = {tool.__name__: tool for tool in tools}# tools - набор функций, из которых может производиться выбор
#импортируется из другого файла с функциями, доступными для бота, tool_schemas - в перевариваемом для бота виде


        # === 1. Получаем ответ модели ===
        response = client.chat.completions.create(
            model=agent.model,
            messages=[{"role": "system", "content": agent.instructions}] + messages,
            tools=tool_schemas or None,
        )
        message = response.choices[0].message
        messages.append(message)

        if message.content:  # Печатаем ответ агента
            print(f"{current_agent.name}:", message.content)

        if not message.tool_calls:  # если обработка вызовов инструментов завершена
            break

        # === 2. Обрабатываем вызовы инструментов ===

        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call, tools_map, current_agent.name)

            if type(result) is Agent:
                current_agent = result
                result=(
                    f"Transferred to {current_agent.name}. Adopt persona immideately."
                )

            result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            messages.append(result_message)

    # ==== 3. Возвращаем новые сообщение =====
    return Response(agent=current_agent, messages=messages[num_init_messages:])
