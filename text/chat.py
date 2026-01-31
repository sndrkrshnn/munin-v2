from openai import OpenAI
from dotenv import load_dotenv
import json
from text.functions.weather import get_weather
from text.functions.websearch import google_search, find_relevant_chunks

load_dotenv()
import os

SYSTEM_PROMPT = "You are Munin. You are Odin's raven who goes around the world and comes back with information. You will pass on your wisdom to the person who asks for it, by answering their questions appropriately. Maintain the ancient wise one demeanor in your replies. "


def fetch_weather(location: str) -> dict | str:
    """Fetch weather data for a given location."""
    if location:
        return get_weather(location)
    return "Location not provided."


def search_web(query: str, relevant_searches: int) -> str:
    """
    Search the web and return a synthesized answer using OpenAI.
    
    Args:
        query: The search query
        relevant_searches: Number of search results to consider
        
    Returns:
        A synthesized answer based on the search results
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Get search results as text content
    text_content = google_search(query, relevant_searches)
    
    if not text_content:
        return "I could not find any relevant information from my search through the ancient scrolls."
    
    # Find the most relevant chunks using embeddings
    relevant_chunks = find_relevant_chunks(query, text_content, client, top_k=3, score_threshold=0.3)
    
    if not relevant_chunks:
        # If no chunks pass the threshold, use snippets from all results
        relevant_chunks = text_content[:3]
    
    # Combine relevant chunks for context
    context = "\n\n---\n\n".join(relevant_chunks)
    
    # Use OpenAI to synthesize an answer from the context
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=SYSTEM_PROMPT,
        input=f"""Based on the following information gathered from searching the web, answer the user's question.

Context from web search:
{context}

User's question: {query}

Provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, acknowledge that and provide what you can."""
    )
    
    return f"{response.output_text}. Had to search {relevant_searches} ancient documents for this answer."


async def generate_chat_response(prompt: str) -> str:
    """
    Generate a chat response using OpenAI's Responses API with function calling.
    
    Args:
        prompt: The user's message
        
    Returns:
        The assistant's response
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    tools = [
        {
            "type": "function",
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
        {
            "type": "function",
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
        }
    ]

    # Initial response with potential function call
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=SYSTEM_PROMPT,
        input=prompt,
        tools=tools,
    )

    # Check if there are any function calls in the output
    tool_calls = [item for item in response.output if item.type == "function_call"]
    
    if tool_calls:
        tool_call = tool_calls[0]
        arguments = json.loads(tool_call.arguments)

        if 'weather' in tool_call.name:
            location = arguments.get("location")
            fn_res = fetch_weather(location)
            
            # Get final response with weather data
            final_response = client.responses.create(
                model="gpt-4o-mini",
                instructions=SYSTEM_PROMPT + " The metrics to be used are km/h, celsius and others in the metric system.",
                input=str(fn_res),
            )
            return final_response.output_text
            
        elif 'search' in tool_call.name:
            query = arguments.get("query")
            relevant_searches = arguments.get("relevant_searches")
            fn_res = search_web(query, relevant_searches)
            return str(fn_res)

    # If no function call, return the text response
    # Get the text output from the response
    text_outputs = [item for item in response.output if item.type == "message"]
    if text_outputs:
        return text_outputs[0].content[0].text
    
    return response.output_text
