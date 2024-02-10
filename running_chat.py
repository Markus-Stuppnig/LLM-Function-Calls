token = "your openai chatgpt api token starting with sk-"

from openai import OpenAI
import json

client = OpenAI(api_key=token)

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def mache_termin_aus(arzt: str):
    # print("debug: Arzt - '" + arzt + "'")
    """Returned einen Termin, an dem der angegebene Arzt noch Platz hat"""
    if "maximilian" in arzt.lower():
        return json.dumps({"termin": "5. Februar 2024"})
    elif "moritz" in arzt.lower():
        return json.dumps({"termin": "7. Februar 2024"})
    else:
        print('didn\'t find')
        return json.dumps({"error": "Dieser Arzt existiert nicht."})
		
    
def run_dialogue(tools: list, available_functions: dict):

    messages = []

    while True:
        new_text: str = input('user (q=quit): ')
        if 'q' == new_text.lower():
            break

        messages.append({"role": "user", "content": new_text})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # print('debug:', response_message)
        messages.append(response_message) #error if this line ain't here and tool_calls - Markus

        if tool_calls:

            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    arzt=function_args.get("arzt"),
                )
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
            second_response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages,
            )  # get a new response from the model where it can see the function response
            second_response_message = second_response.choices[0].message
            messages.append(second_response_message)
            print('assistent:', second_response_message.content)
        else:
            print('assistent:', response_message.content)
            
tools = [
    {
        "type": "function",
        "function": {
            "name": "mache_termin_aus",
            "description": "Macht einen Termin beim angegebenen Arzt aus.",
            "parameters": {
                "type": "object",
                "properties": {
                    "arzt": {
                        "type": "string",
                        "description": "Der Name des Arztes",
                    },
                },
                "required": ["arzt"],
            },
        },
    }
]

available_functions = {
    "mache_termin_aus": mache_termin_aus,
}

print(run_dialogue(tools, available_functions))