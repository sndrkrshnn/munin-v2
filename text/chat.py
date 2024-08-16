from openai import OpenAI
from dotenv import load_dotenv
import json
from text.functions.weather import get_weather

load_dotenv()
import os

BACKGROUND_PROMPT = "You are Munin. You are Odin's raven who goes around the world and comes back with information. You will pass on your wisdom to the person who asks for it, by answering their questions appropriately. Maintain the ancient wise one demeanor in your replies. "

def fetch_weather(location):
    if location:
        return get_weather(location)
    return "Location not provided."


async def generate_chat_response(prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    functions = [
        {
            "type": "function",
            "function": {
                "name": "fetch_weather",
                "description": "Get the current weather for a given location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The name of the location to get the weather for.",
                        }
                    },
                    "required": ["location"],
                    "additionalProperties": False,
                },
            },
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": BACKGROUND_PROMPT,
            },
            {"role": "user", "content": prompt},
        ],
        tools=functions,
        tool_choice="auto",
    )
    fn_res = None
    if len(completion.choices[0].message.tool_calls) > 0:
        tool_call = completion.choices[0].message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)

        if 'weather' in tool_call.function.name:
            location = arguments.get("location")
            fn_res = fetch_weather(location)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": BACKGROUND_PROMPT+"Use the given prompt details to summarize the content into the ancient one's wisdom tone. The metrics to be used are km/h, celsius and others in the metric system.",
                    },
                    {"role": "user", "content": str(fn_res)},
                ],
            )
            return completion.choices[0].message.content

    return completion.choices[0].message.content
