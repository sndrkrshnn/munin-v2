import io
from PIL import Image
import requests
from openai import OpenAI
client = OpenAI()

async def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    
    image_url = response.data[0].url
    image_response= requests.get(image_url)
    image = io.BytesIO(image_response.content)
    return image # Return the file-like object
