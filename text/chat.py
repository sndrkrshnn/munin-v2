from openai import OpenAI
from dotenv import load_dotenv
import json
from text.functions.weather import get_weather
from text.functions.websearch import google_search
from langchain.chains import RetrievalQA
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI

load_dotenv()
import os

SYSTEM_PROMPT = "You are Munin. You are Odin's raven who goes around the world and comes back with information. You will pass on your wisdom to the person who asks for it, by answering their questions appropriately. Maintain the ancient wise one demeanor in your replies. "

def fetch_weather(location):
    if location:
        return get_weather(location)
    return "Location not provided."


def search_web(query, relevant_searches):
    llm=ChatOpenAI(
            model_name="gpt-4o-mini", temperature=0.2, openai_api_key=os.getenv("OPENAI_API_KEY"))
    db = google_search(query, relevant_searches)
    retriever = db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.5},
        )
    mq_retriever = MultiQueryRetriever.from_llm(
                retriever=retriever,
                llm=llm,
            )
    qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=mq_retriever,
        )
    response = qa_chain.invoke(SYSTEM_PROMPT+". Answer the following question with the above mentioned in mind. "+query)
    return f"{response['result']}. Had to search {relevant_searches} ancient documents for this answer."
    


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
        },
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web for relevant information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query you want to send to Google.",
                        },
                        "relevant_searches": {
                            "type": "integer",
                            "description": "The number of search results that need to be considered for the answer.",
                        }
                    },
                    "required": ["query", "relevant_searches"],
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
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": prompt},
        ],
        tools=functions,
        tool_choice="auto",
    )
    fn_res = None
    if completion.choices[0].message.tool_calls and len(completion.choices[0].message.tool_calls) > 0:
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
                        "content": SYSTEM_PROMPT+"The metrics to be used are km/h, celsius and others in the metric system.",
                    },
                    {"role": "user", "content": str(fn_res)},
                ],
            )
            return completion.choices[0].message.content
        elif 'search' in tool_call.function.name:
            query = arguments.get("query")
            relevant_searches = arguments.get("relevant_searches")
            fn_res = search_web(query, relevant_searches)
            return str(fn_res)

    return completion.choices[0].message.content
