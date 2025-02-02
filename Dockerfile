FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
ENV WEBHOOK_URL https://munin-odinsraven.azurewebsites.net/
ENV TELEGRAM_BOT_TOKEN 1921970606:AAFvOb2DLn58gQqaBGXy2R4a5PFewMcP5NE 
ENV OPENAI_API_KEY sk-proj-FomcOA0Ki3x5Sk2WERo0T3BlbkFJiShYtnFHtNh12QbODdyU
ENV GOOGLE_SEARCH AIzaSyCwepsrp8-MCtax0Hr2WwM4lW6tqDvsbIU

EXPOSE 8080
ENTRYPOINT ["python", "main.py"]
