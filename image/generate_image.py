# from PIL import Image

# import torch
# from diffusers import StableDiffusionPipeline

# async def generate_image(prompt):
#     model_id = "runwayml/stable-diffusion-v1-5"
#     pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, revision="fp16", allow_pickle=False)
#     # Use the MPS device for Apple Silicon (if available)
#     device = "mps" if torch.backends.mps.is_available() else "cpu"
#     pipe = pipe.to(device)

#     image = pipe(prompt).images[0]

#     # Convert the image to a BytesIO object
    # img_byte_arr = io.BytesIO()
    # image.save(img_byte_arr, format='PNG')
    # img_byte_arr.seek(0)  # Move the cursor to the start of the file

    # return img_byte_arr  # Return the file-like object
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
